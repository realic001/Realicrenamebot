#!/usr/bin/env python3
"""
Custom Zoro welcome image generator for Telegram Auto-Rename Bot
Creates welcome image with Zoro branding and custom message
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

def create_zoro_welcome_image():
    """Create welcome image with Zoro theme and custom message."""
    
    # Image dimensions
    width = 800
    height = 400
    
    try:
        # Try to load the Zoro image
        if os.path.exists('zoro_image.jpeg'):
            # Load and resize the custom Zoro image
            zoro_img = Image.open('zoro_image.jpeg')
            
            # Create base image with dark background
            img = Image.new('RGB', (width, height), color='#1a1a1a')
            
            # Resize Zoro image to fit nicely (keeping aspect ratio)
            zoro_aspect = zoro_img.width / zoro_img.height
            if zoro_aspect > 1:  # Wide image
                new_width = min(300, width // 3)
                new_height = int(new_width / zoro_aspect)
            else:  # Tall image
                new_height = min(300, height - 100)
                new_width = int(new_height * zoro_aspect)
            
            zoro_resized = zoro_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Position Zoro image on the left side
            zoro_x = 50
            zoro_y = (height - new_height) // 2
            
            # Add subtle blur effect to background
            bg_blur = zoro_resized.copy().filter(ImageFilter.GaussianBlur(radius=10))
            bg_blur = bg_blur.resize((width, height))
            
            # Create gradient overlay
            overlay = Image.new('RGBA', (width, height), (0, 0, 0, 180))
            img = Image.alpha_composite(bg_blur.convert('RGBA'), overlay).convert('RGB')
            
            # Paste the clear Zoro image
            img.paste(zoro_resized, (zoro_x, zoro_y))
            
        else:
            # Fallback: Create gradient background if Zoro image not found
            img = Image.new('RGB', (width, height), color='#1a1a1a')
            draw = ImageDraw.Draw(img)
            
            # Create dark gradient
            for y in range(height):
                ratio = y / height
                r = int(26 + (74 - 26) * ratio)
                g = int(26 + (26 - 26) * ratio)  
                b = int(26 + (46 - 26) * ratio)
                draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    except Exception as e:
        print(f"Error loading image: {e}")
        # Create simple gradient background
        img = Image.new('RGB', (width, height), color='#1a1a1a')
        draw = ImageDraw.Draw(img)
        for y in range(height):
            ratio = y / height
            r = int(26 + (74 - 26) * ratio)
            g = int(26 + (26 - 26) * ratio)
            b = int(26 + (46 - 26) * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    draw = ImageDraw.Draw(img)
    
    # Try to use nice fonts
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        desc_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except OSError:
        try:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()  
            desc_font = ImageFont.load_default()
        except:
            title_font = None
            subtitle_font = None
            desc_font = None
    
    # Custom Zoro text content
    greeting_text = "hlw I am zoro"
    title_text = "AutoRename Bot ⚔️"
    features = [
        "🔥 Master of File Renaming",
        "⚔️ Auto & Manual Modes", 
        "🎯 Custom Format Templates",
        "🖼️ Thumbnail Mastery",
        "👑 Admin Powers"
    ]
    
    # Text positioning (right side if Zoro image exists, center if not)
    text_start_x = 400 if os.path.exists('zoro_image.jpeg') else width // 2
    
    # Draw greeting
    if title_font:
        greeting_bbox = draw.textbbox((0, 0), greeting_text, font=title_font)
        greeting_width = greeting_bbox[2] - greeting_bbox[0]
        if os.path.exists('zoro_image.jpeg'):
            greeting_x = text_start_x
        else:
            greeting_x = (width - greeting_width) // 2
        draw.text((greeting_x, 40), greeting_text, font=title_font, fill='#00ff41')
    
    # Draw title
    if subtitle_font:
        title_bbox = draw.textbbox((0, 0), title_text, font=subtitle_font)
        title_width = title_bbox[2] - title_bbox[0]
        if os.path.exists('zoro_image.jpeg'):
            title_x = text_start_x
        else:
            title_x = (width - title_width) // 2
        draw.text((title_x, 90), title_text, font=subtitle_font, fill='white')
    
    # Draw features
    feature_start_y = 140
    if desc_font:
        for i, feature in enumerate(features):
            if os.path.exists('zoro_image.jpeg'):
                feature_x = text_start_x
            else:
                feature_bbox = draw.textbbox((0, 0), feature, font=desc_font)
                feature_width = feature_bbox[2] - feature_bbox[0]
                feature_x = (width - feature_width) // 2
            
            feature_y = feature_start_y + (i * 28)
            draw.text((feature_x, feature_y), feature, font=desc_font, fill='#cccccc')
    
    # Add decorative sword elements
    sword_color = '#ff6b35'
    # Draw simple sword shapes
    if os.path.exists('zoro_image.jpeg'):
        # Right side decorations
        draw.rectangle([750, 60, 755, 120], fill=sword_color)
        draw.polygon([(750, 60), (760, 50), (755, 55)], fill=sword_color)
        
        draw.rectangle([720, 320, 725, 380], fill=sword_color)
        draw.polygon([(720, 320), (730, 310), (725, 315)], fill=sword_color)
    else:
        # Corner decorations for centered layout
        draw.ellipse([50, 50, 80, 80], fill=(255, 107, 53, 100))
        draw.ellipse([720, 320, 750, 350], fill=(255, 107, 53, 100))
    
    # Save the image
    img.save('bot_welcome.png', 'PNG', quality=95)
    print("✅ Zoro welcome image created: bot_welcome.png")
    
    return True

def update_welcome_message_in_handlers():
    """Update the welcome message in handlers to match Zoro theme."""
    
    # Read the current handlers file
    try:
        with open('bot/handlers.py', 'r') as f:
            content = f.read()
        
        # Update the welcome text to Zoro theme
        old_welcome = '''welcome_text = f"""
🤖 **Welcome to Auto-Rename Bot, {user.first_name}!**

I'm your intelligent file renaming assistant with powerful features:

**🔄 Core Features:**
• Auto & Manual rename modes
• Custom format templates
• File support up to 5GB
• Thumbnail management

**🎨 Advanced Options:**
• Metadata editing
• Word replacement
• Statistics tracking
• Admin broadcasting

Send me a file to get started, or use the menu below!
        """'''
        
        new_welcome = '''welcome_text = f"""
⚔️ **hlw I am zoro AutoRename Bot, {user.first_name}!** 

🔥 Master of file renaming with legendary powers:

**⚔️ Zoro's Arsenal:**
• Auto & Manual rename mastery
• Custom format blade techniques  
• File support up to 5GB
• Thumbnail extraction skills

**🎯 Advanced Abilities:**
• Metadata editing prowess
• Word replacement techniques
• Battle statistics tracking
• Admin command powers

Send me a file to witness my renaming mastery! 👇
        """'''
        
        # Replace the welcome text
        updated_content = content.replace(old_welcome, new_welcome)
        
        # Write back to file
        with open('bot/handlers.py', 'w') as f:
            f.write(updated_content)
        
        print("✅ Updated welcome message in handlers.py")
        return True
        
    except Exception as e:
        print(f"❌ Error updating handlers.py: {e}")
        return False

if __name__ == "__main__":
    print("🎨 Creating Zoro-themed welcome image...")
    
    try:
        # Create the welcome image
        create_zoro_welcome_image()
        
        # Update welcome message in handlers
        update_welcome_message_in_handlers()
        
        print("\n🎉 Zoro theme applied successfully!")
        print("Files updated:")
        print("- bot_welcome.png (Zoro-themed welcome image)")
        print("- bot/handlers.py (Updated welcome message)")
        
    except Exception as e:
        print(f"❌ Error applying Zoro theme: {e}")
        print("Make sure you have Pillow installed: pip install Pillow")