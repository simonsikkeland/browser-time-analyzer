# Browser Time Analyzer

A Python application that analyzes browser history across multiple profiles to help with time tracking and billing distribution. Supports Chrome, Edge, Vivaldi, and Brave browsers.

## Features

- Analyze browsing history across multiple browser profiles
- Support for Chrome, Edge, Vivaldi, and Brave browsers
- View time spent per domain and profile
- Calculate billing hours based on 40-hour week proportional to usage
- Exclude specific profiles from billing calculations
- Analyze historical data from previous weeks
- Interactive charts showing top sites and profile usage
- User-friendly GUI interface

## Installation

### Prerequisites

- Python 3.7 or higher
- Windows operating system (for browser profile access)

### Method 1: Using the Installer

1. Download the latest release from the [Releases](https://github.com/yourusername/browser-time-analyzer/releases) page
2. Extract the "Browser Time Analyzer Installer" folder
3. Run `install.bat` as administrator
4. Launch the application from the desktop shortcut

### Method 2: Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/browser-time-analyzer.git
cd browser-time-analyzer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python src/main.py
```

## Usage

1. Launch the application
2. Select your browser from the list
3. Use the "Weeks ago" spinbox to select which week to analyze (0 for current week)
4. Select any profiles you want to exclude from billing calculations
5. Click "Analyze" to see:
   - Billing distribution across profiles
   - Top sites by time spent
   - Profile usage breakdown

## Development

### Building the Installer

To create a new installer:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Run the build script:
```bash
.\make_installer.bat
```

The installer will be created in the "Browser Time Analyzer Installer" folder.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Uses browser history data from Chrome-based browsers
- Built with Python, tkinter, and matplotlib 