from cairosvg import svg2png
from PIL import Image
import io

def convert_svg_to_ico(svg_path, ico_path):
    # Convert SVG to PNG in memory
    png_data = svg2png(url=svg_path, output_width=256, output_height=256)
    
    # Create PIL Image from PNG data
    img = Image.open(io.BytesIO(png_data))
    
    # Convert to ICO
    img.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])

if __name__ == "__main__":
    convert_svg_to_ico("resources/icon.svg", "resources/icon.ico") 