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
import subprocess
from PIL import Image

# Icon sizes for each platform
ICON_SIZES = {
    'windows': [256, 48, 32, 24, 16],
    'mac': [1024, 512, 256, 128, 64, 32, 16],
    'linux': [256, 128, 64, 48, 32, 24, 16]
}

def ensure_package(pkg):
    """Ensure a required Python package is installed"""
    try:
        __import__(pkg)
    except ImportError:
        print(f"⚙ Installing missing package: {pkg}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

def create_directories():
    """Create output directories for each platform"""
    for platform in ICON_SIZES.keys():
        os.makedirs(f'./{platform}', exist_ok=True)
    print("✓ Directories created")

def resize_image(source_path, output_dir, sizes):
    try:
        img = Image.open(source_path).convert("RGBA")

        # fully clean the base image first (remove ALL metadata)
        base = Image.new("RGBA", img.size)
        base.paste(img, (0,0))

        for size in sizes:
            resized = base.resize((size, size), Image.Resampling.LANCZOS)

            # force a metadata-free PNG
            clean = Image.new("RGBA", (size, size))
            clean.paste(resized, (0,0))

            clean.save(
                f"{output_dir}/icon-{size}.png",
                format="PNG",
                optimize=False
            )

            print(f"  ✓ Clean PNG created for {size}x{size}")

        return True
    except Exception as e:
        print(f"✗ Error resizing image: {e}")
        return False

def create_windows_ico(output_dir):
    try:
        sizes = ICON_SIZES['windows']
        images = []

        for size in sizes:
            images = [Image.open(f'{output_dir}/icon-{size}.png') for size in sizes]
            img = Image.open(f'{output_dir}/icon-{size}.png').convert("RGBA")
            clean = Image.new("RGBA", img.size)
            clean.paste(img)
            images.append(clean)

        images[0].save(
            f'{output_dir}/appIcon.ico',
            format='ICO',
            sizes=[(size, size) for size in sizes]
        )

        print("✓ Windows ICO file created: ./windows/appIcon.ico")
        return True

    except Exception as e:
        print(f"✗ Error creating ICO: {e}")
        return False


def create_mac_icns(output_dir):
    """Create macOS ICNS file from PNGs (native + cross-platform fallback)"""
    import platform, shutil

    try:
        sizes = ICON_SIZES['mac']
        iconset_dir = f'{output_dir}/appIcon.iconset'
        icns_path = f'{output_dir}/appIcon.icns'
        os.makedirs(iconset_dir, exist_ok=True)

        for size in sizes:
            img_path = f'{output_dir}/icon-{size}.png'
            scale = 2 if size > 256 else 1
            icon_name = f'icon_{size // scale}x{size // scale}'
            if scale == 2:
                icon_name += '@2x'
            output_path = f'{iconset_dir}/{icon_name}.png'
            shutil.copyfile(img_path, output_path)

        # Try native iconutil on macOS
        if platform.system() == "Darwin":
            try:
                subprocess.run(
                    ['iconutil', '-c', 'icns', '-o', icns_path, iconset_dir],
                    check=True, capture_output=True
                )
                print("✓ macOS ICNS file created: ./mac/appIcon.icns (via iconutil)")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠ iconutil not found or failed. Falling back to cross-platform method...")

        # Cross-platform fallback using icnsutil
        try:
            ensure_package("icnsutil")
            from icnsutil import IcnsFile
            icns = IcnsFile()

            for size in sizes:
                # Skip sizes not directly supported by ICNS
                if size not in [16, 32, 128, 256, 512, 1024]:
                    continue
                png_path = f'{output_dir}/icon-{size}.png'
                if not os.path.exists(png_path):
                    continue
                try:
                    with open(png_path, "rb") as f:
                        data = f.read()
                    icns.add_media(data=data)
                except Exception as e:
                    print(f"⚠ Skipping {png_path}: {e}")

            icns.write(icns_path)
            print("✓ Cross-platform ICNS file created: ./mac/appIcon.icns (via icnsutil)")
            return True
        except Exception as e:
            print(f"✗ ICNS creation failed (fallback): {e}")
            return False

    except Exception as e:
        print(f"✗ Error creating ICNS: {e}")
        return False

def create_svg_copy(source_path, output_dir):
    """Create SVG copy for Linux (optional)"""
    try:
        import shutil
        svg_path = source_path.replace('.png', '.svg')
        if os.path.exists(svg_path):
            shutil.copy(svg_path, f'{output_dir}/appIcon.svg')
            print(f"✓ SVG icon copied: ./linux/appIcon.svg")
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

    source_image = 'appLogo.png'
    if not os.path.exists(source_image):
        print(f"✗ Error: {source_image} not found in current directory")
        sys.exit(1)

    print(f"Source: {source_image}\n")
    create_directories()
    print()

    for platform, sizes in ICON_SIZES.items():
        print(f"Generating {platform.upper()} icons...")
        output_dir = f'./{platform}'
        if not resize_image(source_image, output_dir, sizes):
            sys.exit(1)
        print()

    print("Creating platform-specific formats...\n")

    if not create_windows_ico('./windows'):
        print("⚠ Continuing despite ICO creation issue\n")

    if not create_mac_icns('./mac'):
        print("⚠ Continuing despite ICNS creation issue\n")

    if not create_svg_copy(source_image, './linux'):
        print("⚠ Continuing despite SVG copy issue\n")

    print("✅ Icon generation complete!")
    print("\nOutput structure:")
    print("  ./")
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
