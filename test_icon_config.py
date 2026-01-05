#!/usr/bin/env python3
"""
Test script to verify icon configuration for the About dialog.
"""

import os
import sys

def test_icon_files_exist():
    """Verify that all required icon files exist."""
    print("Testing icon files existence...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_dir = os.path.join(base_dir, "macos_grok_overlay", "logo")
    
    required_files = [
        "logo_black.png",
        "logo_white.png",
        "icon.icns",
    ]
    
    required_iconset_files = [
        "icon.iconset/icon_16x16.png",
        "icon.iconset/icon_32x32.png",
        "icon.iconset/icon_64x64.png",
        "icon.iconset/icon_128x128.png",
        "icon.iconset/icon_256x256.png",
        "icon.iconset/icon_512x512.png",
    ]
    
    all_pass = True
    
    for file in required_files:
        path = os.path.join(logo_dir, file)
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  ✓ {file} exists ({size} bytes)")
        else:
            print(f"  ✗ {file} MISSING")
            all_pass = False
    
    for file in required_iconset_files:
        path = os.path.join(logo_dir, file)
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  ✓ {file} exists ({size} bytes)")
        else:
            print(f"  ✗ {file} MISSING")
            all_pass = False
    
    return all_pass


def test_constants_configuration():
    """Verify that constants are properly configured."""
    print("\nTesting constants configuration...")
    
    # Read constants file directly to avoid macOS-specific imports
    # (Quartz, AppKit modules are only available on macOS)
    constants_file = os.path.join(os.path.dirname(__file__), "macos_grok_overlay", "constants.py")
    
    try:
        with open(constants_file, 'r') as f:
            content = f.read()
        
        # Use a safer approach to extract constants
        import re
        
        # Match LOGO_BLACK_PATH = "..." or LOGO_BLACK_PATH = '...'
        logo_black_match = re.search(r'LOGO_BLACK_PATH\s*=\s*["\']([^"\']+)["\']', content)
        logo_white_match = re.search(r'LOGO_WHITE_PATH\s*=\s*["\']([^"\']+)["\']', content)
        
        if logo_black_match:
            logo_black = logo_black_match.group(1)
            print(f"  ✓ LOGO_BLACK_PATH = {logo_black}")
            if logo_black == "logo/logo_black.png":
                print(f"  ✓ LOGO_BLACK_PATH is correct")
            else:
                print(f"  ⚠ LOGO_BLACK_PATH unexpected value")
        else:
            print(f"  ✗ LOGO_BLACK_PATH not found")
            return False
            
        if logo_white_match:
            logo_white = logo_white_match.group(1)
            print(f"  ✓ LOGO_WHITE_PATH = {logo_white}")
            if logo_white == "logo/logo_white.png":
                print(f"  ✓ LOGO_WHITE_PATH is correct")
            else:
                print(f"  ⚠ LOGO_WHITE_PATH unexpected value")
        else:
            print(f"  ✗ LOGO_WHITE_PATH not found")
            return False
        
        return True
    except Exception as e:
        print(f"  ✗ Error reading constants: {e}")
        return False


def test_about_dialog_code():
    """Verify About dialog code references the correct icon path."""
    print("\nTesting About dialog code...")
    
    app_file = os.path.join(os.path.dirname(__file__), "macos_grok_overlay", "app.py")
    
    try:
        with open(app_file, 'r') as f:
            content = f.read()
        
        # Check for icon loading code
        if "LOGO_BLACK_PATH" in content:
            print("  ✓ About dialog references LOGO_BLACK_PATH")
        else:
            print("  ✗ About dialog does not reference LOGO_BLACK_PATH")
            return False
        
        # Check for icon display code
        if "NSImage.alloc().initWithContentsOfFile_" in content:
            print("  ✓ About dialog loads icon from file")
        else:
            print("  ✗ About dialog does not load icon")
            return False
        
        if "iconView" in content or "NSImageView" in content:
            print("  ✓ About dialog creates image view for icon")
        else:
            print("  ✗ About dialog does not create image view")
            return False
        
        # Check for About menu item
        if 'About' in content and 'showAbout_' in content:
            print("  ✓ About dialog has menu item and handler")
        else:
            print("  ⚠ About menu item or handler may be missing")
        
        return True
    except Exception as e:
        print(f"  ✗ Error reading app.py: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Icon Configuration Tests for Grok About Dialog")
    print("=" * 60)
    
    test1 = test_icon_files_exist()
    test2 = test_constants_configuration()
    test3 = test_about_dialog_code()
    
    print("\n" + "=" * 60)
    if test1 and test2 and test3:
        print("✅ All tests passed!")
        print("\nThe About dialog is correctly configured to display the icon.")
        print("To see it in action:")
        print("  1. Run: python3 run.py")
        print("  2. Click the menu bar icon")
        print("  3. Select 'About Grok'")
        print("  4. The icon should appear at the top of the About window")
        return 0
    else:
        print("⚠️  Some tests failed. Review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
