"""Generate clean, professional placeholder images when no product images found"""
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap
from io import BytesIO
import requests


def generate_professional_placeholder(product_name, creator, output_path, style="modern"):
    """
    Generate a clean, professional placeholder image for the product
    
    Args:
        product_name: Name of the product
        creator: Creator/vendor name
        output_path: Where to save the image
        style: "modern", "gradient", or "minimal"
    
    Returns:
        bool: Success status
    """
    try:
        print(f"\n{'='*60}")
        print(f"🎨 Generating Professional Placeholder Image")
        print(f"📦 Product: {product_name}")
        print(f"👤 Creator: {creator}")
        print(f"🎨 Style: {style}")
        print(f"{'='*60}")
        
        # Image dimensions (standard blog featured image)
        width, height = 1200, 630
        
        if style == "gradient":
            img = create_gradient_placeholder(width, height, product_name, creator)
        elif style == "minimal":
            img = create_minimal_placeholder(width, height, product_name, creator)
        else:  # modern
            img = create_modern_placeholder(width, height, product_name, creator)
        
        # Save as optimized WEBP
        img.save(output_path, "WEBP", quality=85, method=6, optimize=True)
        
        file_size = os.path.getsize(output_path)
        print(f"\n✅ Placeholder generated successfully!")
        print(f"   📁 Size: {file_size / 1024:.1f} KB")
        print(f"   💾 Saved: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Placeholder generation failed: {e}")
        return False


def create_modern_placeholder(width, height, product_name, creator):
    """Create modern, professional placeholder with dark theme"""
    
    # Create base image with dark gradient
    img = Image.new('RGB', (width, height), color=(30, 33, 41))
    draw = ImageDraw.Draw(img)
    
    # Add subtle gradient overlay
    for y in range(height):
        alpha = int(255 * (1 - y / height * 0.3))
        color = (45, 55, 72, alpha)
        draw.rectangle([(0, y), (width, y+1)], fill=(45, 55, 72))
    
    # Add decorative elements (subtle geometric shapes)
    # Top right circle
    draw.ellipse([(width-300, -150), (width+150, 300)], 
                 fill=(59, 130, 246, 30))
    
    # Bottom left circle
    draw.ellipse([(-150, height-300), (300, height+150)], 
                 fill=(139, 92, 246, 30))
    
    # Try to load nice font, fallback to default
    try:
        # Try common system fonts
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "C:\\Windows\\Fonts\\Arial.ttf",
        ]
        
        title_font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                title_font = ImageFont.truetype(font_path, 56)
                subtitle_font = ImageFont.truetype(font_path, 32)
                label_font = ImageFont.truetype(font_path, 24)
                break
        
        if not title_font:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
            
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        label_font = ImageFont.load_default()
    
    # Wrap product name if too long
    max_chars = 35
    if len(product_name) > max_chars:
        words = product_name.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            if len(' '.join(current_line)) > max_chars:
                if len(current_line) > 1:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(' '.join(current_line))
                    current_line = []
        
        if current_line:
            lines.append(' '.join(current_line))
        
        product_lines = lines[:2]  # Max 2 lines
    else:
        product_lines = [product_name]
    
    # Calculate vertical centering
    total_height = len(product_lines) * 70 + 50 + 40 + 60
    start_y = (height - total_height) // 2
    
    # Draw "PRODUCT REVIEW" label at top
    label_text = "PRODUCT REVIEW"
    label_bbox = draw.textbbox((0, 0), label_text, font=label_font)
    label_width = label_bbox[2] - label_bbox[0]
    label_x = (width - label_width) // 2
    
    draw.text((label_x, start_y), label_text, 
              fill=(156, 163, 175), font=label_font)
    
    # Draw product name (centered, multi-line if needed)
    current_y = start_y + 50
    for line in product_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        text_width = bbox[2] - bbox[0]
        text_x = (width - text_width) // 2
        
        # Draw text with slight shadow for depth
        draw.text((text_x+2, current_y+2), line, fill=(0, 0, 0, 128), font=title_font)
        draw.text((text_x, current_y), line, fill=(255, 255, 255), font=title_font)
        current_y += 70
    
    # Draw creator name
    if creator and creator not in ["Unknown Creator", ""]:
        creator_text = f"by {creator}"
        creator_bbox = draw.textbbox((0, 0), creator_text, font=subtitle_font)
        creator_width = creator_bbox[2] - creator_bbox[0]
        creator_x = (width - creator_width) // 2
        
        draw.text((creator_x, current_y + 20), creator_text, 
                  fill=(156, 163, 175), font=subtitle_font)
    
    # Add bottom accent line
    accent_y = height - 40
    draw.rectangle([(width//2 - 100, accent_y), (width//2 + 100, accent_y + 4)],
                   fill=(59, 130, 246))
    
    return img


def create_gradient_placeholder(width, height, product_name, creator):
    """Create vibrant gradient placeholder"""
    
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    # Create blue-purple gradient
    for y in range(height):
        r = int(59 + (139 - 59) * y / height)
        g = int(130 + (92 - 130) * y / height)
        b = int(246 + (246 - 246) * y / height)
        draw.rectangle([(0, y), (width, y+1)], fill=(r, g, b))
    
    # Add overlay pattern
    for x in range(0, width, 100):
        for y in range(0, height, 100):
            draw.ellipse([(x, y), (x+50, y+50)], fill=(255, 255, 255, 10))
    
    # Load fonts
    try:
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "C:\\Windows\\Fonts\\Arial.ttf",
        ]
        
        title_font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                title_font = ImageFont.truetype(font_path, 60)
                subtitle_font = ImageFont.truetype(font_path, 36)
                break
        
        if not title_font:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Draw text
    wrapped_title = textwrap.fill(product_name, width=30)
    lines = wrapped_title.split('\n')[:2]
    
    y_offset = height // 2 - len(lines) * 35
    
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 70
    
    if creator and creator not in ["Unknown Creator", ""]:
        creator_text = f"by {creator}"
        bbox = draw.textbbox((0, 0), creator_text, font=subtitle_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y_offset + 20), creator_text, 
                  fill=(255, 255, 255, 200), font=subtitle_font)
    
    return img


def create_minimal_placeholder(width, height, product_name, creator):
    """Create clean, minimal placeholder"""
    
    # White background
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Add subtle border
    border_color = (229, 231, 235)
    draw.rectangle([(10, 10), (width-10, height-10)], 
                   outline=border_color, width=3)
    
    # Load fonts
    try:
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "C:\\Windows\\Fonts\\Arial.ttf",
        ]
        
        title_font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                title_font = ImageFont.truetype(font_path, 54)
                subtitle_font = ImageFont.truetype(font_path, 30)
                label_font = ImageFont.truetype(font_path, 22)
                break
        
        if not title_font:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        label_font = ImageFont.load_default()
    
    # Add subtle icon/shape at top
    center_x = width // 2
    draw.rectangle([(center_x - 50, 120), (center_x + 50, 130)],
                   fill=(59, 130, 246))
    
    # Draw label
    label = "PRODUCT REVIEW"
    bbox = draw.textbbox((0, 0), label, font=label_font)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) // 2, 160), label,
              fill=(107, 114, 128), font=label_font)
    
    # Draw product name
    wrapped_title = textwrap.fill(product_name, width=35)
    lines = wrapped_title.split('\n')[:2]
    
    y_offset = 240
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        text_width = bbox[2] - bbox[0]
        draw.text(((width - text_width) // 2, y_offset), line,
                  fill=(17, 24, 39), font=title_font)
        y_offset += 65
    
    # Draw creator
    if creator and creator not in ["Unknown Creator", ""]:
        creator_text = f"by {creator}"
        bbox = draw.textbbox((0, 0), creator_text, font=subtitle_font)
        text_width = bbox[2] - bbox[0]
        draw.text(((width - text_width) // 2, y_offset + 30), creator_text,
                  fill=(107, 114, 128), font=subtitle_font)
    
    return img


def try_generate_placeholder_image(product_name, creator, output_path):
    """
    Try to generate a professional placeholder image
    
    Returns:
        bool: Success status
    """
    try:
        # Try modern style first (looks best)
        return generate_professional_placeholder(
            product_name, 
            creator, 
            output_path, 
            style="modern"
        )
    except Exception as e:
        print(f"❌ Placeholder generation failed: {e}")
        return False


if __name__ == "__main__":
    # Test the generator
    print("Testing Placeholder Image Generator...")
    
    test_cases = [
        ("Amazing AI Suite Pro", "John Smith", "test_modern.webp", "modern"),
        ("Super Marketing Tool", "Tech Corp", "test_gradient.webp", "gradient"),
        ("Simple CRM Software", "Jane Doe", "test_minimal.webp", "minimal"),
    ]
    
    for product, creator, filename, style in test_cases:
        print(f"\n{'='*60}")
        print(f"Testing: {product} ({style})")
        success = generate_professional_placeholder(product, creator, filename, style)
        
        if success:
            print(f"✅ Generated: {filename}")
        else:
            print(f"❌ Failed: {filename}")