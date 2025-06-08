#!/usr/bin/env python3
"""
Welcome image generator for Telegram Auto-Rename Bot
Creates a professional welcome image with bot branding
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_welcome_image():
    """Create a professional welcome image for the bot."""
    
    # Image dimensions
    width = 800
    height = 400
    
    # Create image with gradient background
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Create gradient background (blue to purple)
    for y in range(height):
        # Calculate color transition
        ratio = y / height
        r = int(74 + (138 - 74) * ratio)    # 74 -> 138
        g = int(144 + (43 - 144) * ratio)   # 144 -> 43
        b = int(226 + (226 - 226) * ratio)  # 226 -> 226
        
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Try to use a nice font, fallback to default if not available
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        desc_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except OSError:
        # Fallback to default font
        try:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            desc_font = ImageFont.load_default()
        except:
            title_font = None
            subtitle_font = None
            desc_font = None
    
    # Text content
    title_text = "🤖 Auto-Rename Bot"
    subtitle_text = "Intelligent File Renaming Assistant"
    features = [
        "✨ Auto & Manual Rename Modes",
        "🎨 Custom Format Templates", 
        "🖼️ Thumbnail Management",
        "📊 Statistics & Leaderboard",
        "👑 Admin Controls & Broadcasting"
    ]
    
    # Draw title
    if title_font:
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        draw.text((title_x, 40), title_text, font=title_font, fill='white')
    
    # Draw subtitle
    if subtitle_font:
        subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (width - subtitle_width) // 2
        draw.text((subtitle_x, 100), subtitle_text, font=subtitle_font, fill='white')
    
    # Draw features
    feature_start_y = 160
    if desc_font:
        for i, feature in enumerate(features):
            feature_bbox = draw.textbbox((0, 0), feature, font=desc_font)
            feature_width = feature_bbox[2] - feature_bbox[0]
            feature_x = (width - feature_width) // 2
            feature_y = feature_start_y + (i * 30)
            draw.text((feature_x, feature_y), feature, font=desc_font, fill='white')
    
    # Add decorative elements
    # Draw some circles for decoration
    draw.ellipse([50, 50, 100, 100], fill=(255, 255, 255, 50))
    draw.ellipse([700, 300, 750, 350], fill=(255, 255, 255, 50))
    draw.ellipse([20, 320, 70, 370], fill=(255, 255, 255, 50))
    
    # Save the image
    img.save('bot_welcome.png', 'PNG', quality=95)
    print("✅ Welcome image created successfully: bot_welcome.png")
    
    return True

def create_bot_icon():
    """Create a simple bot icon."""
    size = 512
    img = Image.new('RGB', (size, size), color='#4A90E2')
    draw = ImageDraw.Draw(img)
    
    # Draw robot face
    # Head circle
    head_margin = size // 8
    draw.ellipse([head_margin, head_margin, size - head_margin, size - head_margin], 
                fill='white', outline='#2E5A87', width=8)
    
    # Eyes
    eye_size = size // 12
    eye_y = size // 3
    left_eye_x = size // 3 - eye_size // 2
    right_eye_x = 2 * size // 3 - eye_size // 2
    
    draw.ellipse([left_eye_x, eye_y, left_eye_x + eye_size, eye_y + eye_size], fill='#2E5A87')
    draw.ellipse([right_eye_x, eye_y, right_eye_x + eye_size, eye_y + eye_size], fill='#2E5A87')
    
    # Mouth
    mouth_width = size // 4
    mouth_height = size // 16
    mouth_x = (size - mouth_width) // 2
    mouth_y = size // 2
    
    draw.ellipse([mouth_x, mouth_y, mouth_x + mouth_width, mouth_y + mouth_height], fill='#2E5A87')
    
    # Antennas
    antenna_height = size // 8
    antenna_width = 8
    
    # Left antenna
    left_antenna_x = size // 3
    draw.rectangle([left_antenna_x - antenna_width//2, head_margin - antenna_height, 
                   left_antenna_x + antenna_width//2, head_margin], fill='#2E5A87')
    draw.ellipse([left_antenna_x - antenna_width, head_margin - antenna_height - antenna_width, 
                 left_antenna_x + antenna_width, head_margin - antenna_height + antenna_width], fill='#E74C3C')
    
    # Right antenna
    right_antenna_x = 2 * size // 3
    draw.rectangle([right_antenna_x - antenna_width//2, head_margin - antenna_height, 
                   right_antenna_x + antenna_width//2, head_margin], fill='#2E5A87')
    draw.ellipse([right_antenna_x - antenna_width, head_margin - antenna_height - antenna_width, 
                 right_antenna_x + antenna_width, head_margin - antenna_height + antenna_width], fill='#E74C3C')
    
    img.save('generated-icon.png', 'PNG', quality=95)
    print("✅ Bot icon created successfully: generated-icon.png")
    
    return True

if __name__ == "__main__":
    print("🎨 Creating welcome image and bot icon...")
    
    try:
        # Create welcome image
        create_welcome_image()
        
        # Create bot icon
        create_bot_icon()
        
        print("\n🎉 All images created successfully!")
        print("Files created:")
        print("- bot_welcome.png (Welcome image for bot)")
        print("- generated-icon.png (Bot profile icon)")
        
    except Exception as e:
        print(f"❌ Error creating images: {e}")
        print("Make sure you have Pillow installed: pip install Pillow")