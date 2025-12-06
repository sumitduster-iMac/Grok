#!/bin/zsh

# Build script for creating an unsigned DMG (for local testing only)
# For distribution, use build.sh with proper signing credentials

APP_NAME="Grok"

# Get the directory of this script
SCRIPT_DIR=${0:a:h}
cd "$SCRIPT_DIR"

echo "Building Grok (unsigned, for local testing)..."

# Create a build environment
touch temp.egg-info
rm -rf env dist build *.egg-info
python3 -m venv env
source env/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install setuptools==70.3.0 py2app pyobjc

# Get the build directory name
build_dir_name=${0:a:h:t}

# Build the '.app' with 'py2app'
pushd ..
touch temp.egg-info
rm -rf dist build *.egg-info
python setup.py py2app --dist-dir="$build_dir_name"/dist --bdist-base="$build_dir_name"/build
popd

# Deactivate the python building environment
deactivate

# Check if create-dmg is installed
if ! command -v create-dmg &> /dev/null; then
    echo ""
    echo "create-dmg not found. Installing via Homebrew..."
    brew install create-dmg
fi

# Remove old DMG if it exists
rm -f $APP_NAME.dmg

# Create a DMG that provides an easy-installer
create-dmg \
    --volname "$APP_NAME" \
    --window-size 600 300 \
    --icon-size 100 \
    --app-drop-link 400 150 \
    $APP_NAME.dmg \
    dist/$APP_NAME.app

echo ""
echo "Done! DMG created at: $SCRIPT_DIR/$APP_NAME.dmg"
echo ""
echo "NOTE: This DMG is unsigned and will show security warnings."
echo "To run: Right-click the app → Open → Open"

