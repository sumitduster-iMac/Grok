<p align="center">
  <h1 align="center"><code>Grok</code></h1>
</p>

<p align="center">
A simple macOS overlay application for pinning <code>grok.com</code> to a dedicated window and key command <code>option+space</code>.
</p>

<img width="479" height="968" alt="Screenshot 2026-01-07 at 7 03 53 PM" src="https://github.com/user-attachments/assets/9c7db092-a5eb-4665-99fd-511e525564d4" />



## Installation:

  The easiest approach is to download and execute the DMG installer (by clicking the image below) to place the program into your Applications folder.

**Compatibility:** The DMG launcher is now built as a universal binary (arm64 + x86_64), so it runs on both modern M-series laptops and older Intel-based Macs (2015/2017 era) provided they are on a supported version of macOS. When creating your own build you can force a specific target by exporting `PY2APP_ARCH` (e.g., `PY2APP_ARCH=x86_64 ./dmg-builder/build.sh`).



  Otherwise, you can install the latest stable release from a Terminal with:

```bash
python3 -m pip install macos-grok-overlay
```

  Once you've installed the package, you can enable it to be automatically launched at startup with:

```bash
grok --install-startup
```

  You will get a request like this to enable Accessibility the first time this launches.

<img width="231" height="284" alt="Screenshot 2026-01-07 at 7 04 08 PM" src="https://github.com/user-attachments/assets/2e68bcb2-133c-4bbb-83e1-ec39d5528cfe" />


  The Accessibility access is required for the background task to listen for the `Option+Space` keyboard command. But please don't just take my word for it, look at the [listener code yourself](macos_grok_overlay/listener.py) and see. ;)

  Within a few seconds of approving Accessibility access, you should see a little icon like this appear along the top of your screen.


![Menu Sample](images/macos-grok-overlay-menu.png)
  And you're done! Now this should launch automatically and constantly run in the background. If you ever decide you do not want it, see the uninstall instructions below.


## Usage

  Once the application is launched, it should immediately open a window dedicated to `grok.com`. You'll need to log in there, but you should only need to do that once. After installing, pressing `Option + Space` while the window is open will hide it, and pressing it again at any point will reveal it and pin it as the top-most window overlay on top of other applications. This enables quick and easy access to Grok on macOS.

  There is a dropdown menu with basic options that shows when you click the menubar icon. Personally I find that using `Option + Space` to summon and dismiss the dialogue as needed is the most convenient.

  If you decide you want to uninstall the application, you can do that by clicking the option in the menubar dropdown, or from the command line with:

```bash
grok --uninstall-startup
```


## About

Developed by **Sumit Duster**

A macOS overlay for Grok AI - providing quick access to Grok from anywhere on your Mac.


## How it works

  This is a very thin `pyobjc` application written to contain a web view of the current production Grok website. Most of the logic contained in this small application is for stylistic purposes, making the overlay shaped correctly, resizeable, draggable, and able to be summoned anywhere easily with a single (modifiable) keyboard command. There's also a few steps needed to listen specifically for the `Option + Space` keyboard command, which requires Accessibility access to macOS.


## Final thoughts

  This was a small fun weekend project. Please file issues and I'll be happy to adjust, but I also highly recommend you look at the source code yourself if you want to change something. It's a small and simple project, Grok (or similar) could easily help you modify it for your own purposes.
