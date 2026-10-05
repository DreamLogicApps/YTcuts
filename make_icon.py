from PIL import Image, ImageDraw

def create_icon():
    # Create transparent background
    img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw rounded black rectangle
    draw.rounded_rectangle((0, 0, 256, 256), radius=64, fill=(0, 0, 0, 255))
    
    # Draw top circle
    draw.ellipse((44, 44, 108, 108), outline="white", width=20)
    # Draw bottom circle
    draw.ellipse((44, 148, 108, 212), outline="white", width=20)
    
    # Draw lines (scissors)
    draw.line((88, 88, 200, 200), fill="white", width=20)
    draw.line((88, 168, 200, 56), fill="white", width=20)
    
    # Save as ICO with multiple sizes for Windows
    img.save('icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])

if __name__ == '__main__':
    create_icon()

