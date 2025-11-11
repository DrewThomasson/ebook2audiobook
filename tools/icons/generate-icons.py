#!/usr/bin/env python3
"""
Multi-platform icon generator
Converts appLogo.png into platform-specific formats and sizes
Requires: Pillow (PIL), cairosvg (optional for SVG)

Installation:
    pip install Pillow cairosvg
"""

import os
import sys
from PIL import Image

# Icon sizes for each platform
ICON_SIZES = {
    'windows': [16, 24, 32, 48, 256],
    'mac': [16, 32, 64, 128, 256, 512, 1024],
    'linux': [16, 24, 32, 48, 64, 128, 256]
}

def create_directories():
    """Create output directories for each platform"""
    for platform in ICON_SIZES.keys():
        os.makedirs(f'icons/{platform}', exist_ok=True)
    print("✓ Directories created")

def resize_image(source_path, output_dir, sizes):
    """Resize image to multiple sizes"""
    try:
        img = Image.open(source_path)
        # Convert to RGBA to ensure transparency support
        img = img.convert('RGBA')
        
        for size in sizes:
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            output_path = f'{output_dir}/icon-{size}.png'
            resized.save(output_path, 'PNG')
            print(f"  ✓ Generated {size}x{size} icon")
        
        return True
    except Exception as e:
        print(f"✗ Error resizing image: {e}")
        return False

def create_windows_ico(output_dir):
    """Create Windows ICO file from PNGs"""
    try:
        sizes = ICON_SIZES['windows']
        images = []
        
        for size in sizes:
            img_path = f'{output_dir}/icon-{size}.png'
            images.append(Image.open(img_path))
        
        # Save as ICO with multiple sizes
        images[0].save(
            f'{output_dir}/appIcon.ico',
            format='ICO',
            sizes=[(size, size) for size in sizes]
        )
        print("✓ Windows ICO file created: icons/windows/appIcon.ico")
        return True
    except Exception as e:
        print(f"✗ Error creating ICO: {e}")
        return False

def create_mac_icns(output_dir):
    """Create macOS ICNS file from PNGs (requires imagemagick or online conversion)"""
    try:
        import subprocess
        sizes = ICON_SIZES['mac']
        
        # Create iconset directory
        iconset_dir = f'{output_dir}/appIcon.iconset'
        os.makedirs(iconset_dir, exist_ok=True)
        
        for size in sizes:
            img_path = f'{output_dir}/icon-{size}.png'
            # macOS uses specific naming conventions
            scale = 2 if size > 256 else 1
            icon_name = f'icon_{size // scale}x{size // scale}'
            if scale == 2:
                icon_name += '@2x'
            
            output_path = f'{iconset_dir}/{icon_name}.png'
            os.system(f'cp {img_path} {output_path}')
        
        # Try to create ICNS using iconutil (macOS only) or convert
        try:
            subprocess.run(['iconutil', '-c', 'icns', '-o', 
                          f'{output_dir}/appIcon.icns', iconset_dir], 
                         check=True, capture_output=True)
            print("✓ macOS ICNS file created: icons/mac/appIcon.icns")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠ Note: iconutil not found. ICNS not created.")
            print("  On macOS, run: iconutil -c icns -o icons/mac/appIcon.icns icons/mac/appIcon.iconset")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Error creating ICNS: {e}")
        return False

def create_svg_copy(source_path, output_dir):
    """Create SVG copy for Linux (optional, requires vector source)"""
    try:
        import shutil
        svg_path = source_path.replace('.png', '.svg')
        
        if os.path.exists(svg_path):
            shutil.copy(svg_path, f'{output_dir}/appIcon.svg')
            print(f"✓ SVG icon copied: icons/linux/appIcon.svg")
            return True
        else:
            print("⚠ No SVG source found (optional for Linux)")
            return True
    except Exception as e:
        print(f"✗ Error copying SVG: {e}")
        return False

def main():
    """Main execution"""
    print("🎨 Multi-Platform Icon Generator\n")
    
    # Find source image
    source_image = 'appLogo.png'
    if not os.path.exists(source_image):
        print(f"✗ Error: {source_image} not found in current directory")
        sys.exit(1)
    
    print(f"Source: {source_image}\n")
    
    # Create directories
    create_directories()
    print()
    
    # Generate icons for each platform
    for platform, sizes in ICON_SIZES.items():
        print(f"Generating {platform.upper()} icons...")
        output_dir = f'icons/{platform}'
        
        if not resize_image(source_image, output_dir, sizes):
            sys.exit(1)
        print()
    
    # Create platform-specific formats
    print("Creating platform-specific formats...\n")
    
    if not create_windows_ico('icons/windows'):
        print("⚠ Continuing despite ICO creation issue\n")
    
    if not create_mac_icns('icons/mac'):
        print("⚠ Continuing despite ICNS creation issue\n")
    
    if not create_svg_copy(source_image, 'icons/linux'):
        print("⚠ Continuing despite SVG copy issue\n")
    
    print("✅ Icon generation complete!")
    print("\nOutput structure:")
    print("  icons/")
    print("  ├── windows/")
    print("  │   ├── appIcon.ico")
    print("  │   └── icon-*.png")
    print("  ├── mac/")
    print("  │   ├── appIcon.icns (if created)")
    print("  │   └── icon-*.png")
    print("  └── linux/")
    print("      ├── appIcon.svg (if available)")
    print("      └── icon-*.png")

if __name__ == '__main__':
    main()
