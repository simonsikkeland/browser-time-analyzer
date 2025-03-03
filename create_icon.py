from PIL import Image, ImageDraw

def create_clock_icon(size=256):
    # Create a new image with a white background
    img = Image.new('RGB', (size, size), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw outer circle
    margin = size // 10
    draw.ellipse([margin, margin, size - margin, size - margin], outline='#4285f4', fill='#4285f4', width=2)
    
    # Draw inner circle
    inner_margin = size // 4
    draw.ellipse([inner_margin, inner_margin, size - inner_margin, size - inner_margin], outline='white', fill='white', width=2)
    
    # Draw clock hands
    center = size // 2
    # Hour hand
    draw.line([center, center, center, center - size//4], fill='#4285f4', width=6)
    # Minute hand
    draw.line([center, center, center + size//3, center], fill='#4285f4', width=4)
    
    return img

def create_icon():
    # Create icons of different sizes
    sizes = [16, 32, 64, 128, 256]
    icons = []
    
    for size in sizes:
        icon = create_clock_icon(size)
        icons.append(icon)
    
    # Save as ICO file with multiple sizes
    icons[0].save('resources/icon.ico', format='ICO', sizes=[(s,s) for s in sizes], append_images=icons[1:])

if __name__ == '__main__':
    create_icon() 