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
for size in 16 32 64 128 256 512 1024 1200; do
    output_file="$ICONSET_DIR/icon_${size}x${size}.png"
    if sips -z "$size" "$size" "$INPUT_ICON" --out "$output_file" 2>&1 | grep -q "Error"; then
        echo "Error: Failed to generate ${size}x${size} icon"
        exit 1
    fi
done

echo "Converting to ICNS format..."
if ! iconutil -c icns "$ICONSET_DIR" -o "$LOGO_DIR/icon.icns" 2>&1; then
    echo "Error: Failed to create ICNS file"
    exit 1
fi

echo "Creating menu bar icons..."
# Create a large version for menu bar (keeping aspect ratio)
if ! sips -Z 961 "$INPUT_ICON" --out "$LOGO_DIR/logo_black.png" 2>&1; then
    echo "Error: Failed to create logo_black.png"
    exit 1
fi
if ! sips -Z 961 "$INPUT_ICON" --out "$LOGO_DIR/logo_white.png" 2>&1; then
    echo "Error: Failed to create logo_white.png"
    exit 1
fi

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
