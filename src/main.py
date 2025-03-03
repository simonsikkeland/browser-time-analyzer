import sqlite3
import pandas as pd
import os
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from urllib.parse import urlparse
import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path

class BrowserHistoryAnalyzer:
    BROWSER_PATHS = {
        'Vivaldi': {
            'path': r'AppData\Local\Vivaldi\User Data',
            'profile_file': 'Local State'
        },
        'Chrome': {
            'path': r'AppData\Local\Google\Chrome\User Data',
            'profile_file': 'Local State'
        },
        'Edge': {
            'path': r'AppData\Local\Microsoft\Edge\User Data',
            'profile_file': 'Local State'
        },
        'Brave': {
            'path': r'AppData\Local\BraveSoftware\Brave-Browser\User Data',
            'profile_file': 'Local State'
        }
    }

    def __init__(self):
        self.base_path = None
        self.browser_type = None
        self.profiles = range(1, 9)  # Profiles 1 through 8
        self.history_data = {}
        self.profile_names = {}
        self.excluded_profiles = []

    def set_browser(self, browser_type):
        """Set the browser type and find its path"""
        self.browser_type = browser_type
        user_path = os.path.expanduser('~')
        self.base_path = os.path.join(user_path, self.BROWSER_PATHS[browser_type]['path'])
        self.profile_names = self.load_profile_names()

    def load_profile_names(self):
        """Load profile names from Local State file"""
        try:
            local_state_path = os.path.join(self.base_path, self.BROWSER_PATHS[self.browser_type]['profile_file'])
            with open(local_state_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                profile_names = {}
                if 'profile' in data and 'info_cache' in data['profile']:
                    for profile_id, info in data['profile']['info_cache'].items():
                        if profile_id.startswith('Profile'):
                            profile_num = int(profile_id.split()[-1])
                            profile_names[profile_num] = info.get('name', f'Profile {profile_num}')
                return profile_names
        except Exception as e:
            print(f"Error loading profile names: {str(e)}")
            return {}

    def set_excluded_profiles(self, profile_numbers):
        """Set which profiles to exclude from billing calculations"""
        self.excluded_profiles = profile_numbers

    def get_profile_path(self, profile_num):
        return os.path.join(self.base_path, f"Profile {profile_num}", "History")

    def connect_to_db(self, db_path):
        # Create a copy of the database file since it might be locked by the browser
        temp_db = f"temp_history_{datetime.now().strftime('%Y%m%d%H%M%S')}.db"
        with open(db_path, 'rb') as src, open(temp_db, 'wb') as dst:
            dst.write(src.read())
        
        conn = sqlite3.connect(temp_db)
        return conn, temp_db

    def cleanup_temp_db(self, temp_db):
        try:
            os.remove(temp_db)
        except:
            pass

    def convert_chrome_time(self, timestamp):
        """Convert Chrome time format to datetime object"""
        if timestamp == 0:
            return None
        # Chrome timestamp is expressed in microseconds since Jan 1 1601
        seconds_since_epoch = timestamp / 1000000 - 11644473600
        try:
            return datetime.fromtimestamp(seconds_since_epoch)
        except (ValueError, OSError):
            return None

    def analyze_profile(self, profile_num):
        profile_path = self.get_profile_path(profile_num)
        
        try:
            conn, temp_db = self.connect_to_db(profile_path)
            
            # Query to get visit history with timestamps
            query = """
            SELECT
                urls.url,
                urls.title,
                visits.visit_time,
                visits.visit_duration
            FROM urls
            JOIN visits ON urls.id = visits.url
            ORDER BY visits.visit_time DESC
            """
            
            df = pd.read_sql_query(query, conn)
            
            # Convert timestamps using our custom function
            df['visit_time'] = df['visit_time'].apply(self.convert_chrome_time)
            
            # Drop rows with invalid timestamps
            df = df.dropna(subset=['visit_time'])
            
            # Extract domain from URL
            df['domain'] = df['url'].apply(lambda x: urlparse(x).netloc)
            
            conn.close()
            self.cleanup_temp_db(temp_db)
            
            return df
            
        except Exception as e:
            print(f"Error analyzing profile {profile_num}: {str(e)}")
            return None

    def analyze_all_profiles(self):
        for profile in self.profiles:
            df = self.analyze_profile(profile)
            if df is not None and not df.empty:
                self.history_data[profile] = df

    def get_week_data(self, df, week_offset=0):
        """Filter dataframe for a specific week's data"""
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday() + (7 * week_offset))
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=7)
        return df[(df['visit_time'] >= week_start) & (df['visit_time'] < week_end)]

    def generate_time_report(self, week_offset=0, exclude_profiles=None):
        all_data = []
        for profile, df in self.history_data.items():
            if exclude_profiles and profile in exclude_profiles:
                continue
                
            df = self.get_week_data(df, week_offset)
            
            if df.empty:
                continue
                
            profile_data = df.groupby('domain').agg({
                'visit_time': 'count',
                'visit_duration': 'sum'
            }).reset_index()
            profile_data['profile'] = profile
            profile_data['profile_name'] = self.profile_names.get(profile, f'Profile {profile}')
            all_data.append(profile_data)
        
        if all_data:
            combined_data = pd.concat(all_data)
            # Convert visit_duration from microseconds to hours
            combined_data['hours'] = combined_data['visit_duration'].fillna(0) / (1000000 * 3600)
            
            # Group by domain across all profiles
            total_time = combined_data.groupby('domain').agg({
                'hours': 'sum',
                'visit_time': 'sum'
            }).sort_values('hours', ascending=False)
            
            # Also generate per-profile summary
            profile_summary = combined_data.groupby(['profile', 'profile_name']).agg({
                'hours': 'sum',
                'visit_time': 'sum'
            }).sort_values('hours', ascending=False)
            
            return total_time, profile_summary
        return None, None

    def calculate_billing_distribution(self, week_offset=0):
        """Calculate billing hours based on 40-hour week proportional to usage"""
        _, profile_summary = self.generate_time_report(
            week_offset=week_offset,
            exclude_profiles=self.excluded_profiles
        )
        
        if profile_summary is not None and not profile_summary.empty:
            total_hours = profile_summary['hours'].sum()
            profile_summary['billing_hours'] = (profile_summary['hours'] / total_hours * 40).round(2)
            return profile_summary
        return None

    def create_top_sites_plot(self, n=10, week_offset=0):
        """Create a matplotlib figure for top sites"""
        total_time, _ = self.generate_time_report(week_offset)
        if total_time is None:
            return None
        
        fig = Figure(figsize=(8, 4))
        ax = fig.add_subplot(111)
        
        top_sites = total_time.head(n)
        ax.bar(range(len(top_sites)), top_sites['hours'])
        ax.set_xticks(range(len(top_sites)))
        ax.set_xticklabels(top_sites.index, rotation=45, ha='right')
        
        week_str = "Current Week" if week_offset == 0 else f"Week {-week_offset} ago"
        ax.set_title(f'Top {n} Sites by Time Spent ({week_str})')
        ax.set_xlabel('Domain')
        ax.set_ylabel('Hours')
        
        fig.tight_layout()
        return fig

    def create_profile_usage_plot(self, week_offset=0):
        """Create a matplotlib figure for profile usage"""
        _, profile_summary = self.generate_time_report(week_offset)
        if profile_summary is None:
            return None
        
        fig = Figure(figsize=(8, 4))
        ax = fig.add_subplot(111)
        
        profile_names = [f"{row[1]} ({row[0]})" for row in profile_summary.index]
        ax.bar(range(len(profile_names)), profile_summary['hours'])
        ax.set_xticks(range(len(profile_names)))
        ax.set_xticklabels(profile_names, rotation=45, ha='right')
        
        week_str = "Current Week" if week_offset == 0 else f"Week {-week_offset} ago"
        ax.set_title(f'Time Spent per Profile ({week_str})')
        ax.set_xlabel('Profile')
        ax.set_ylabel('Hours')
        
        fig.tight_layout()
        return fig

class BrowserAnalyzerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Browser Time Analyzer")
        self.root.geometry("1200x800")
        
        self.analyzer = BrowserHistoryAnalyzer()
        self.setup_gui()

    def setup_gui(self):
        # Left panel for controls
        left_panel = ttk.Frame(self.root, padding=10)
        left_panel.pack(side="left", fill="y", padx=5, pady=5)
        
        # Browser selection
        browser_frame = ttk.LabelFrame(left_panel, text="Browser Selection", padding=10)
        browser_frame.pack(fill="x", pady=5)
        
        self.browser_var = tk.StringVar()
        for browser in self.analyzer.BROWSER_PATHS.keys():
            ttk.Radiobutton(browser_frame, text=browser, value=browser, 
                          variable=self.browser_var, command=self.update_profiles).pack(anchor="w")
        
        # Week selection
        week_frame = ttk.LabelFrame(left_panel, text="Week Selection", padding=10)
        week_frame.pack(fill="x", pady=5)
        
        self.week_offset = tk.IntVar(value=0)
        ttk.Label(week_frame, text="Weeks ago:").pack(side="left")
        week_spin = ttk.Spinbox(week_frame, from_=0, to=52, width=5,
                               textvariable=self.week_offset)
        week_spin.pack(side="left", padx=5)
        
        # Profile exclusion
        profile_frame = ttk.LabelFrame(left_panel, text="Exclude Profiles", padding=10)
        profile_frame.pack(fill="x", pady=5)
        
        self.excluded_profiles = []
        self.profile_vars = {}
        
        # Buttons
        button_frame = ttk.Frame(left_panel, padding=10)
        button_frame.pack(fill="x", pady=5)
        
        ttk.Button(button_frame, text="Analyze", command=self.analyze).pack(fill="x", pady=2)
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(fill="x", pady=2)
        
        # Right panel for results and charts
        right_panel = ttk.Frame(self.root, padding=10)
        right_panel.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Results text
        self.results_text = tk.Text(right_panel, height=10, width=60)
        self.results_text.pack(fill="x", pady=5)
        
        # Charts frame
        charts_frame = ttk.Frame(right_panel)
        charts_frame.pack(fill="both", expand=True)
        
        # Placeholders for charts
        self.top_sites_canvas = None
        self.profile_usage_canvas = None

    def update_profiles(self):
        try:
            if not self.browser_var.get():
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, "Please select a browser first")
                return
                
            self.analyzer.set_browser(self.browser_var.get())
            self.profile_vars.clear()
            
            # Find the profile frame in the left panel
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Frame):  # This is the left panel
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.LabelFrame) and child.cget("text") == "Exclude Profiles":
                            # Clear existing checkboxes
                            for grandchild in child.winfo_children():
                                grandchild.destroy()
                            
                            if not self.analyzer.profile_names:
                                self.results_text.delete(1.0, tk.END)
                                self.results_text.insert(tk.END, f"No profiles found for {self.browser_var.get()}. Please check if the browser is installed and has profiles.")
                                return
                            
                            # Add new checkboxes for each profile
                            for profile_num, profile_name in self.analyzer.profile_names.items():
                                var = tk.BooleanVar()
                                self.profile_vars[profile_num] = var
                                ttk.Checkbutton(
                                    child,
                                    text=f"{profile_name} (Profile {profile_num})",
                                    variable=var
                                ).pack(anchor="w")
                            break
        except Exception as e:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Error updating profiles: {str(e)}")

    def update_charts(self):
        # Clear existing charts
        if self.top_sites_canvas:
            self.top_sites_canvas.get_tk_widget().destroy()
        if self.profile_usage_canvas:
            self.profile_usage_canvas.get_tk_widget().destroy()
            
        # Create new charts
        charts_frame = [f for f in self.root.winfo_children() if isinstance(f, ttk.Frame)][-1]
        
        # Profile usage chart (now first)
        profile_usage_fig = self.analyzer.create_profile_usage_plot(week_offset=self.week_offset.get())
        if profile_usage_fig:
            self.profile_usage_canvas = FigureCanvasTkAgg(profile_usage_fig, master=charts_frame)
            self.profile_usage_canvas.draw()
            self.profile_usage_canvas.get_tk_widget().pack(fill="both", expand=True, pady=5)
        
        # Top sites chart (now second)
        top_sites_fig = self.analyzer.create_top_sites_plot(week_offset=self.week_offset.get())
        if top_sites_fig:
            self.top_sites_canvas = FigureCanvasTkAgg(top_sites_fig, master=charts_frame)
            self.top_sites_canvas.draw()
            self.top_sites_canvas.get_tk_widget().pack(fill="both", expand=True, pady=5)

    def analyze(self):
        try:
            self.results_text.delete(1.0, tk.END)
            
            if not self.browser_var.get():
                self.results_text.insert(tk.END, "Please select a browser first")
                return
            
            self.results_text.insert(tk.END, "Starting analysis...\n")
            self.root.update()
            
            # Set browser and update excluded profiles
            self.analyzer.set_browser(self.browser_var.get())
            excluded = [num for num, var in self.profile_vars.items() if var.get()]
            self.analyzer.set_excluded_profiles(excluded)
            
            self.results_text.insert(tk.END, "Analyzing profiles...\n")
            self.root.update()
            
            # Analyze profiles
            self.analyzer.analyze_all_profiles()
            
            if not self.analyzer.history_data:
                self.results_text.insert(tk.END, "No browsing history found. Please check if:\n")
                self.results_text.insert(tk.END, "1. The selected browser is installed\n")
                self.results_text.insert(tk.END, "2. There are profiles with browsing history\n")
                self.results_text.insert(tk.END, "3. The profiles are not corrupted\n")
                return
            
            self.results_text.insert(tk.END, "Calculating billing distribution...\n")
            self.root.update()
            
            # Calculate and display billing distribution
            billing_dist = self.analyzer.calculate_billing_distribution(
                week_offset=self.week_offset.get()
            )
            
            if billing_dist is not None and not billing_dist.empty:
                billing_dist = billing_dist.reset_index()
                self.results_text.insert(tk.END, "\nBilling Distribution:\n\n")
                self.results_text.insert(tk.END, str(billing_dist[['profile_name', 'hours', 'billing_hours']]))
                
                # Update charts
                self.results_text.insert(tk.END, "\n\nGenerating charts...\n")
                self.root.update()
                self.update_charts()
                
                self.results_text.insert(tk.END, "\nAnalysis complete!")
            else:
                self.results_text.insert(tk.END, "\nNo data found for the selected period")
                
        except Exception as e:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Error during analysis: {str(e)}\n")
            self.results_text.insert(tk.END, "Please make sure:\n")
            self.results_text.insert(tk.END, "1. The selected browser is installed\n")
            self.results_text.insert(tk.END, "2. You have permission to access the browser files\n")
            self.results_text.insert(tk.END, "3. The browser is not currently running\n")

def main():
    gui = BrowserAnalyzerGUI()
    gui.root.mainloop()

if __name__ == "__main__":
    main() 