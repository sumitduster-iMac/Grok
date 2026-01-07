<p align="center">
  <img src="https://github.com/user-attachments/assets/0fc09487-61e9-41e0-876a-0c7ab32eca53" alt="Grok Logo" width="200"/>
</p>

<h1 align="center">Grok - macOS Overlay</h1>

<p align="center">
  <strong>A simple macOS overlay application for pinning <code>grok.com</code> to a dedicated window</strong>
</p>

<p align="center">
  Quick access to Grok AI with <code>Option + Space</code> keyboard shortcut
</p>

<p align="center">
  <a href="#-preview">Preview</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-how-it-works">How it Works</a> •
  <a href="#-about">About</a>
</p>

---

## 📸 Preview

<p align="center">
  <img width="479" alt="Grok Overlay Screenshot" src="https://github.com/user-attachments/assets/9c7db092-a5eb-4665-99fd-511e525564d4" />
</p>

## 📦 Installation

### Option 1: DMG Installer (Recommended)

The easiest approach is to download and execute the DMG installer (by clicking the image below) to place the program into your Applications folder.

**Compatibility:** The DMG launcher is now built as a universal binary (arm64 + x86_64), so it runs on both modern M-series laptops and older Intel-based Macs (2015/2017 era) provided they are on a supported version of macOS. When creating your own build you can force a specific target by exporting `PY2APP_ARCH` (e.g., `PY2APP_ARCH=x86_64 ./dmg-builder/build.sh`).

### Option 2: Install via pip

Alternatively, you can install the latest stable release from a Terminal with:

```bash
python3 -m pip install macos-grok-overlay
```

Once you've installed the package, you can enable it to be automatically launched at startup with:

```bash
grok --install-startup
```

### 🔐 Accessibility Permission

You will get a request like this to enable Accessibility the first time this launches:

<p align="center">
  <img width="475" alt="Accessibility Permission Request" src="https://github.com/user-attachments/assets/a76ad5ba-5965-4c71-8ee9-6e4d759cf254" />
</p>

The Accessibility access is required for the background task to listen for the `Option+Space` keyboard command. But please don't just take my word for it, look at the [listener code yourself](macos_grok_overlay/listener.py) and see. ;)

Within a few seconds of approving Accessibility access, you should see a little icon like this appear along the top of your screen:

<p align="center">
  <img width="231" alt="Menu Bar Icon" src="https://github.com/user-attachments/assets/9f34b044-6b78-4af4-87fa-5454461aca1d" />
</p>

And you're done! Now this should launch automatically and constantly run in the background. If you ever decide you do not want it, see the uninstall instructions below.

## 🚀 Usage

Once the application is launched, it should immediately open a window dedicated to `grok.com`. You'll need to log in there, but you should only need to do that once. 

**Keyboard Shortcut:** Pressing `Option + Space` while the window is open will hide it, and pressing it again at any point will reveal it and pin it as the top-most window overlay on top of other applications. This enables quick and easy access to Grok on macOS.

**Menu Bar:** There is a dropdown menu with basic options that shows when you click the menubar icon. Personally I find that using `Option + Space` to summon and dismiss the dialogue as needed is the most convenient.

### Uninstallation

If you decide you want to uninstall the application, you can do that by clicking the option in the menubar dropdown, or from the command line with:

```bash
grok --uninstall-startup
```

## 👨‍💻 About

**Developed by Sumit Duster**

A macOS overlay for Grok AI - providing quick access to Grok from anywhere on your Mac.

## ⚙️ How it works

This is a very thin `pyobjc` application written to contain a web view of the current production Grok website. Most of the logic contained in this small application is for stylistic purposes, making the overlay shaped correctly, resizeable, draggable, and able to be summoned anywhere easily with a single (modifiable) keyboard command. There's also a few steps needed to listen specifically for the `Option + Space` keyboard command, which requires Accessibility access to macOS.

## 💭 Final thoughts

This was a small fun weekend project. Please file issues and I'll be happy to adjust, but I also highly recommend you look at the source code yourself if you want to change something. It's a small and simple project, Grok (or similar) could easily help you modify it for your own purposes.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/sumitduster-iMac">Sumit Duster</a>
</p>
