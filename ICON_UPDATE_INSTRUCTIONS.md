# Icon Update Instructions

This guide explains how to update the Grok app icon from macosicons.com.

## Getting the Icon from macosicons.com

1. Visit: https://macosicons.com/#/?icon=7PM6rcO2Sj
2. Click the download button for PNG format (recommended: 512x512 or larger)
3. Also download the ICNS format if available for the app icon

## Icon Files to Update

The app uses three main icon files:

### 1. Menu Bar Icons (Required)
- **Location**: `macos_grok_overlay/logo/logo_black.png`
- **Purpose**: Displayed in the menu bar when using light mode
- **Recommended size**: 961x921 pixels (or similar aspect ratio)
- **Requirements**: Should be a black/dark icon on transparent background

- **Location**: `macos_grok_overlay/logo/logo_white.png`
- **Purpose**: Displayed in the menu bar when using dark mode
- **Recommended size**: 961x921 pixels (or similar aspect ratio)
- **Requirements**: Should be a white/light icon on transparent background

### 2. App Icon (Required)
- **Location**: `macos_grok_overlay/logo/icon.icns`
- **Purpose**: The main application icon shown in Finder, Dock, and About dialog
- **Format**: Apple ICNS format
- **Size**: Multiple sizes embedded (see iconset folder)

### 3. Icon Set for ICNS (Optional, for rebuilding icon.icns)
- **Location**: `macos_grok_overlay/logo/icon.iconset/`
- **Contains**: Multiple PNG sizes for different display contexts
  - icon_16x16.png
  - icon_32x32.png
  - icon_64x64.png
  - icon_128x128.png
  - icon_256x256.png
  - icon_512x512.png
  - icon_1200x1200.png

## Converting PNG to ICNS

If you download a PNG icon from macosicons.com, use the provided helper script to convert it:

```bash
./scripts/convert_icon.sh path/to/downloaded_icon.png
```

Or manually using macOS tools:

```bash
# 1. Create iconset directory
mkdir -p temp.iconset

# 2. Generate different sizes (requires ImageMagick or sips)
sips -z 16 16 icon.png --out temp.iconset/icon_16x16.png
sips -z 32 32 icon.png --out temp.iconset/icon_32x32.png
sips -z 64 64 icon.png --out temp.iconset/icon_64x64.png
sips -z 128 128 icon.png --out temp.iconset/icon_128x128.png
sips -z 256 256 icon.png --out temp.iconset/icon_256x256.png
sips -z 512 512 icon.png --out temp.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out temp.iconset/icon_1024x1024.png

# 3. Convert to ICNS
iconutil -c icns temp.iconset -o icon.icns

# 4. Clean up
rm -rf temp.iconset
```

## Updating the About Dialog

The About dialog automatically uses the `logo_black.png` icon. After replacing the icon files:

1. The icon will appear at the top of the About window (64x64 pixels)
2. No code changes are needed - it's automatically loaded from `LOGO_BLACK_PATH`
3. The icon is displayed in the `showAbout_` method in `macos_grok_overlay/app.py`

## Testing Your Changes

After updating the icon files:

1. **Test Menu Bar Icon**:
   ```bash
   python3 run.py
   ```
   - Check the menu bar icon in both light and dark modes
   - Change system appearance: System Settings → Appearance → Light/Dark

2. **Test About Dialog**:
   - Click the menu bar icon
   - Select "About Grok"
   - Verify the icon displays correctly at the top of the window

3. **Test App Icon** (for DMG builds):
   - Build the app using `./dmg-builder/build.sh`
   - Check the icon in Finder and Dock

## Quick Update Steps

1. Download icon from https://macosicons.com/#/?icon=7PM6rcO2Sj
2. Save as `macos_grok_overlay/logo/icon.png` (temporary)
3. Run the conversion script:
   ```bash
   ./scripts/convert_icon.sh macos_grok_overlay/logo/icon.png
   ```
4. The script will update all necessary files
5. Test the application
6. Commit the changes

## Notes

- The About dialog always uses `logo_black.png` regardless of system theme
- Menu bar automatically switches between `logo_white.png` and `logo_black.png` based on system appearance
- Icon sizes are optimized for retina displays
- Transparent backgrounds are recommended for all PNG files
