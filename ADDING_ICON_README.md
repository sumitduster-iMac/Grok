# Adding Icon from macosicons.com

## Task Overview
This guide helps you add the icon from https://macosicons.com/#/?icon=7PM6rcO2Sj to the Grok app.

## Quick Start (3 Steps)

### Step 1: Download the Icon
1. Visit https://macosicons.com/#/?icon=7PM6rcO2Sj
2. Click the download button
3. Choose PNG format (512x512 or larger recommended)
4. Save the file to your Downloads folder

### Step 2: Convert and Install
Run one of these commands:

**Using bash (recommended for macOS):**
```bash
./scripts/convert_icon.sh ~/Downloads/[icon-filename].png
```

**Using Python:**
```bash
python3 scripts/convert_icon.py ~/Downloads/[icon-filename].png
```

The script will automatically:
- Generate all required icon sizes
- Create the ICNS file for the app icon
- Update menu bar icons (logo_black.png and logo_white.png)
- Update iconset for different display resolutions

### Step 3: Test the Changes
```bash
python3 run.py
```

Then verify:
1. **Menu bar icon**: Check the icon in the top menu bar (test both light and dark mode)
2. **About dialog**: Click menu bar icon → "About Grok" → Verify icon shows at top
3. **App icon** (optional): Build DMG to see icon in Finder/Dock

## What Gets Updated

The conversion script updates these files:
- ✅ `macos_grok_overlay/logo/icon.icns` - Main app icon
- ✅ `macos_grok_overlay/logo/logo_black.png` - Menu bar (light mode) & About dialog
- ✅ `macos_grok_overlay/logo/logo_white.png` - Menu bar (dark mode)
- ✅ `macos_grok_overlay/logo/icon.iconset/*` - Icon sizes (16px to 1200px)

## About Dialog Icon Display

The About dialog automatically displays the icon:
- **Source**: `logo_black.png` file
- **Size**: 64x64 pixels
- **Location**: Top center of About window
- **Code**: Located in `app.py` lines 430-438

No code changes are needed - just replace the icon files!

## Troubleshooting

**If the conversion script fails:**
- Ensure you're running on macOS (requires `sips` and `iconutil`)
- Check that the input PNG file is valid
- Make sure you have write permissions to the logo directory

**If icons don't update after running:**
- Quit the app completely and restart
- Clear any cached app icons: `sudo rm -rf /var/folders/*/-Caches-/`
- Rebuild if using DMG: `./dmg-builder/build.sh`

**For white/inverted icon (dark mode):**
The script creates a copy of the original for `logo_white.png`. You may want to manually create an inverted/white version for better visibility in dark mode:
- Use an image editor (Preview, Photoshop, GIMP)
- Invert colors or create a white outline version
- Save as `logo_white.png`

## What's Already Done

✅ About dialog code is correctly configured
✅ Icon loading from LOGO_BLACK_PATH works
✅ Icon displays at proper size (64x64)
✅ Conversion scripts created and tested
✅ Documentation created

## What You Need to Do

⏳ Download icon from macosicons.com
⏳ Run conversion script with downloaded icon
⏳ Test the app to verify icon appears correctly
⏳ Commit the updated icon files

## Alternative: Manual Icon Update

If you prefer not to use the scripts, you can manually:

1. **For menu bar icons**: Replace `logo_black.png` and `logo_white.png` with your icon (recommended size: ~961x921)
2. **For app icon**: 
   - Create folder: `icon.iconset`
   - Generate sizes: 16, 32, 64, 128, 256, 512, 1024, 1200 (square)
   - Run: `iconutil -c icns icon.iconset -o icon.icns`
3. **Test**: Run the app and check all icon appearances

## Need Help?

See [ICON_UPDATE_INSTRUCTIONS.md](ICON_UPDATE_INSTRUCTIONS.md) for comprehensive documentation.
