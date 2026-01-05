#!/bin/bash

# Icon Conversion Script for Grok
# Converts a downloaded PNG icon to all required formats

set -e

# Check if input file is provided
if [ -z "$1" ]; then
    echo "Usage: ./scripts/convert_icon.sh <path_to_icon.png>"
    echo "Example: ./scripts/convert_icon.sh ~/Downloads/grok_icon.png"
    exit 1
fi

INPUT_ICON="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOGO_DIR="$PROJECT_ROOT/macos_grok_overlay/logo"
ICONSET_DIR="$LOGO_DIR/icon.iconset"

# Check if input file exists
if [ ! -f "$INPUT_ICON" ]; then
    echo "Error: Input file '$INPUT_ICON' not found"
    exit 1
fi

echo "Converting icon: $INPUT_ICON"
echo "Output directory: $LOGO_DIR"

# Create iconset directory
mkdir -p "$ICONSET_DIR"

# Generate different sizes for iconset
echo "Generating icon sizes..."
sips -z 16 16 "$INPUT_ICON" --out "$ICONSET_DIR/icon_16x16.png" > /dev/null 2>&1
sips -z 32 32 "$INPUT_ICON" --out "$ICONSET_DIR/icon_32x32.png" > /dev/null 2>&1
sips -z 64 64 "$INPUT_ICON" --out "$ICONSET_DIR/icon_64x64.png" > /dev/null 2>&1
sips -z 128 128 "$INPUT_ICON" --out "$ICONSET_DIR/icon_128x128.png" > /dev/null 2>&1
sips -z 256 256 "$INPUT_ICON" --out "$ICONSET_DIR/icon_256x256.png" > /dev/null 2>&1
sips -z 512 512 "$INPUT_ICON" --out "$ICONSET_DIR/icon_512x512.png" > /dev/null 2>&1
sips -z 1024 1024 "$INPUT_ICON" --out "$ICONSET_DIR/icon_1024x1024.png" > /dev/null 2>&1
sips -z 1200 1200 "$INPUT_ICON" --out "$ICONSET_DIR/icon_1200x1200.png" > /dev/null 2>&1

echo "Converting to ICNS format..."
iconutil -c icns "$ICONSET_DIR" -o "$LOGO_DIR/icon.icns"

echo "Creating menu bar icons..."
# Create a large version for menu bar (keeping aspect ratio)
sips -Z 961 "$INPUT_ICON" --out "$LOGO_DIR/logo_black.png" > /dev/null 2>&1
sips -Z 961 "$INPUT_ICON" --out "$LOGO_DIR/logo_white.png" > /dev/null 2>&1

echo ""
echo "✅ Icon conversion complete!"
echo ""
echo "Files updated:"
echo "  - $LOGO_DIR/icon.icns"
echo "  - $LOGO_DIR/logo_black.png"
echo "  - $LOGO_DIR/logo_white.png"
echo "  - $ICONSET_DIR/* (8 files)"
echo ""
echo "⚠️  Note: logo_white.png should be inverted for dark mode."
echo "   You may need to manually create a white version of the icon."
echo ""
echo "Next steps:"
echo "  1. If needed, create an inverted/white version for dark mode"
echo "  2. Test the application: python3 run.py"
echo "  3. Check About dialog and menu bar icon"
echo "  4. Commit the changes"
