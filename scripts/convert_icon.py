#!/usr/bin/env python3
"""
Icon Downloader and Converter for Grok
Downloads an icon from macosicons.com and converts it to all required formats.
"""

import sys
import os
import subprocess
import urllib.request
import argparse
from pathlib import Path


def download_icon_from_macosicons(icon_id, output_path):
    """
    Attempt to download icon from macosicons.com.
    Note: This may not work due to site restrictions. Manual download may be required.
    
    The URLs below are speculative endpoints - macosicons.com doesn't provide
    a documented public API for direct downloads by icon ID.
    """
    # Possible URL patterns (unverified - may need adjustment based on site structure)
    possible_urls = [
        f"https://macosicons.com/api/icons/{icon_id}/download",
        f"https://cdn.macosicons.com/{icon_id}.png",
        f"https://macosicons.com/downloads/{icon_id}.png",
    ]
    
    for url in possible_urls:
        try:
            print(f"Attempting to download from: {url}")
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read()
                with open(output_path, 'wb') as f:
                    f.write(data)
                print(f"✅ Successfully downloaded icon to {output_path}")
                return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            continue
    
    return False


def convert_icon(input_path, project_root):
    """Convert a PNG icon to all required formats using sips and iconutil."""
    
    input_path = Path(input_path)
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' not found")
        return False
    
    logo_dir = project_root / "macos_grok_overlay" / "logo"
    iconset_dir = logo_dir / "icon.iconset"
    
    print(f"Converting icon: {input_path}")
    print(f"Output directory: {logo_dir}")
    
    # Create iconset directory
    iconset_dir.mkdir(parents=True, exist_ok=True)
    
    # Sizes to generate
    sizes = [16, 32, 64, 128, 256, 512, 1024, 1200]
    
    print("Generating icon sizes...")
    for size in sizes:
        output_file = iconset_dir / f"icon_{size}x{size}.png"
        try:
            result = subprocess.run([
                "sips", "-z", str(size), str(size),
                str(input_path), "--out", str(output_file)
            ], check=True, capture_output=True, text=True)
            print(f"  ✓ {size}x{size}")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Failed to create {size}x{size}")
            print(f"     Error: {e.stderr}")
            return False
    
    print("Converting to ICNS format...")
    try:
        result = subprocess.run([
            "iconutil", "-c", "icns",
            str(iconset_dir), "-o", str(logo_dir / "icon.icns")
        ], check=True, capture_output=True, text=True)
        print("  ✓ icon.icns created")
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed to create ICNS")
        print(f"     Error: {e.stderr}")
        return False
    
    print("Creating menu bar icons...")
    for icon_name in ["logo_black.png", "logo_white.png"]:
        output_file = logo_dir / icon_name
        try:
            result = subprocess.run([
                "sips", "-Z", "961",
                str(input_path), "--out", str(output_file)
            ], check=True, capture_output=True, text=True)
            print(f"  ✓ {icon_name}")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Failed to create {icon_name}")
            print(f"     Error: {e.stderr}")
            return False
    
    print("\n✅ Icon conversion complete!")
    print("\nFiles updated:")
    print(f"  - {logo_dir}/icon.icns")
    print(f"  - {logo_dir}/logo_black.png")
    print(f"  - {logo_dir}/logo_white.png")
    print(f"  - {iconset_dir}/* (8 files)")
    print("\n⚠️  Note: logo_white.png should be inverted for dark mode.")
    print("   You may need to manually create a white version of the icon.")
    print("\nNext steps:")
    print("  1. If needed, create an inverted/white version for dark mode")
    print("  2. Test the application: python3 run.py")
    print("  3. Check About dialog and menu bar icon")
    print("  4. Commit the changes")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Download and convert icons for Grok app"
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        help="Path to input PNG icon file (if already downloaded)"
    )
    parser.add_argument(
        "--download",
        metavar="ICON_ID",
        help="Download icon from macosicons.com using icon ID (e.g., 7PM6rcO2Sj)"
    )
    
    args = parser.parse_args()
    
    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Determine input file
    input_file = None
    
    if args.download:
        print(f"Attempting to download icon: {args.download}")
        temp_file = "/tmp/downloaded_icon.png"
        if download_icon_from_macosicons(args.download, temp_file):
            input_file = temp_file
        else:
            print("\n❌ Automatic download failed.")
            print(f"Please manually download the icon from:")
            print(f"  https://macosicons.com/#/?icon={args.download}")
            print(f"Then run: python3 scripts/convert_icon.py <path_to_downloaded_icon.png>")
            return 1
    elif args.input_file:
        input_file = args.input_file
    else:
        parser.print_help()
        print("\nExamples:")
        print("  # Download and convert:")
        print("  python3 scripts/convert_icon.py --download 7PM6rcO2Sj")
        print("\n  # Convert existing file:")
        print("  python3 scripts/convert_icon.py ~/Downloads/grok_icon.png")
        return 1
    
    # Convert the icon
    if input_file:
        if convert_icon(input_file, project_root):
            return 0
        else:
            return 1
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
