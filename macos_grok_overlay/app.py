# Python libraries
import os
import sys

# Apple libraries
import objc
from AppKit import *
from WebKit import *
from Quartz import *
from Foundation import NSObject, NSURL, NSURLRequest, NSDate
import AVFoundation


def request_microphone_permission():
    """Request microphone permission from macOS."""
    auth_status = AVFoundation.AVCaptureDevice.authorizationStatusForMediaType_(
        AVFoundation.AVMediaTypeAudio
    )
    if auth_status == AVFoundation.AVAuthorizationStatusNotDetermined:
        # Request permission
        AVFoundation.AVCaptureDevice.requestAccessForMediaType_completionHandler_(
            AVFoundation.AVMediaTypeAudio,
            lambda granted: print(f"Microphone permission {'granted' if granted else 'denied'}")
        )
    elif auth_status == AVFoundation.AVAuthorizationStatusAuthorized:
        print("Microphone permission already granted")
    else:
        print("Microphone permission denied. Please enable in System Settings > Privacy & Security > Microphone")


# UI Delegate to handle permission requests (microphone, camera, etc.)
class WebViewUIDelegate(NSObject):
    # Handle media capture permission requests (microphone, camera)
    # This method is called when a webpage requests access to microphone/camera
    def webView_requestMediaCapturePermissionForOrigin_initiatedByFrame_type_decisionHandler_(
        self, webView, origin, frame, mediaType, decisionHandler
    ):
        # WKPermissionDecision: 1 = Grant
        # Call the decision handler to grant permission
        decisionHandler(1)

# Local libraries
from .constants import (
    APP_TITLE,
    CORNER_RADIUS,
    DRAG_AREA_HEIGHT,
    LOGO_BLACK_PATH,
    LOGO_WHITE_PATH,
    FRAME_SAVE_NAME,
    STATUS_ITEM_CONTEXT,
    WEBSITE,
)
from .launcher import (
    install_startup,
    uninstall_startup,
)
from .listener import (
    global_show_hide_listener,
    load_custom_launcher_trigger,
    set_custom_launcher_trigger,
)


# Custom window (contains entire application).
class AppWindow(NSWindow):
    # Explicitly allow key window status
    def canBecomeKeyWindow(self):
        return True

    # Required to capture "Command+..." sequences.
    def keyDown_(self, event):
        self.delegate().keyDown_(event)


# Custom traffic light button (shows icon on hover)
class TrafficLightButton(NSButton):
    def initWithFrame_color_icon_(self, frame, color, icon):
        self = objc.super(TrafficLightButton, self).initWithFrame_(frame)
        if self:
            self._color = color
            self._icon = icon
            self._hovered = False
            self.setTitle_("")
            self.setBordered_(False)
            self.setButtonType_(NSButtonTypeMomentaryChange)
            self.setWantsLayer_(True)
            self.layer().setBackgroundColor_(color.CGColor())
            self.layer().setCornerRadius_(7)
            self.setFont_(NSFont.boldSystemFontOfSize_(9))
            self.setAlignment_(NSTextAlignmentCenter)
            # Add tracking area for mouse hover
            trackingArea = NSTrackingArea.alloc().initWithRect_options_owner_userInfo_(
                self.bounds(),
                NSTrackingMouseEnteredAndExited | NSTrackingActiveAlways,
                self,
                None
            )
            self.addTrackingArea_(trackingArea)
        return self
    
    def mouseEntered_(self, event):
        self._hovered = True
        self.setTitle_(self._icon)
        self.setNeedsDisplay_(True)
    
    def mouseExited_(self, event):
        self._hovered = False
        self.setTitle_("")
        self.setNeedsDisplay_(True)


# Custom view (contains click-and-drag area on top sliver of overlay).
class DragArea(NSView):
    def initWithFrame_(self, frame):
        objc.super(DragArea, self).initWithFrame_(frame)
        self.setWantsLayer_(True)
        return self
    
    # Used to update top-bar background to (roughly) match app color.
    def setBackgroundColor_(self, color):
        self.layer().setBackgroundColor_(color.CGColor())

    # Used to capture the click-and-drag event.
    def mouseDown_(self, event):
        self.window().performWindowDragWithEvent_(event)


# The main delegate for running the overlay app.
class AppDelegate(NSObject):
    # The main application setup.
    def applicationDidFinishLaunching_(self, notification):
        # Run as regular app (shows in Dock)
        NSApp.setActivationPolicy_(NSApplicationActivationPolicyRegular)
        # Create a borderless, resizable, miniaturizable window
        self.window = AppWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(500, 200, 550, 580),
            NSWindowStyleMaskBorderless | NSWindowStyleMaskResizable | NSWindowStyleMaskMiniaturizable,
            NSBackingStoreBuffered,
            False
        )
        self.window.setLevel_(NSNormalWindowLevel)
        self.window.setCollectionBehavior_(
            NSWindowCollectionBehaviorCanJoinAllSpaces
            | NSWindowCollectionBehaviorStationary
        )
        # Save the last position and size
        self.window.setFrameAutosaveName_(FRAME_SAVE_NAME)
        # Create the webview for the main application.
        config = WKWebViewConfiguration.alloc().init()
        config.preferences().setJavaScriptCanOpenWindowsAutomatically_(True)
        # Enable media capture (microphone and camera) without user action
        # Setting to 0 means no media types require user action (allows all media types)
        config.setMediaTypesRequiringUserActionForPlayback_(0)  # Allow all media without user action
        # Initialize the WebView with a frame
        self.webview = WKWebView.alloc().initWithFrame_configuration_(
            ((0, 0), (800, 600)),  # Frame: origin (0,0), size (800x600)
            config
        )
        self.webview.setAutoresizingMask_(NSViewWidthSizable | NSViewHeightSizable)  # Resizes with window
        # Set UI delegate for handling permission requests (microphone, camera)
        self.ui_delegate = WebViewUIDelegate.alloc().init()
        self.webview.setUIDelegate_(self.ui_delegate)
        # Set a custom user agent
        safari_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
        self.webview.setCustomUserAgent_(safari_user_agent)
        # Make window transparent so that the corners can be rounded
        self.window.setOpaque_(False)
        self.window.setBackgroundColor_(NSColor.clearColor())
        # Set up content view with rounded corners
        content_view = NSView.alloc().initWithFrame_(self.window.contentView().bounds())
        content_view.setWantsLayer_(True)
        content_view.layer().setCornerRadius_(CORNER_RADIUS)
        content_view.layer().setBackgroundColor_(NSColor.whiteColor().CGColor())
        self.window.setContentView_(content_view)
        # Set up drag area (top sliver, full width)
        content_bounds = content_view.bounds()
        self.drag_area = DragArea.alloc().initWithFrame_(
            NSMakeRect(0, content_bounds.size.height - DRAG_AREA_HEIGHT, content_bounds.size.width, DRAG_AREA_HEIGHT)
        )
        content_view.addSubview_(self.drag_area)
        # Add close button to the drag area (red circle, shows X on hover)
        red_color = NSColor.colorWithCalibratedRed_green_blue_alpha_(1.0, 0.38, 0.36, 1.0)
        close_button = TrafficLightButton.alloc().initWithFrame_color_icon_(NSMakeRect(8, 8, 14, 14), red_color, "✕")
        close_button.setTarget_(self)
        close_button.setAction_("hideWindow:")
        self.drag_area.addSubview_(close_button)
        # Add minimize button to the drag area (yellow circle, shows - on hover)
        yellow_color = NSColor.colorWithCalibratedRed_green_blue_alpha_(1.0, 0.78, 0.23, 1.0)
        minimize_button = TrafficLightButton.alloc().initWithFrame_color_icon_(NSMakeRect(28, 8, 14, 14), yellow_color, "−")
        minimize_button.setTarget_(self)
        minimize_button.setAction_("minimizeWindow:")
        self.drag_area.addSubview_(minimize_button)
        # Add zoom button to the drag area (green circle, shows + on hover)
        green_color = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.15, 0.78, 0.37, 1.0)
        zoom_button = TrafficLightButton.alloc().initWithFrame_color_icon_(NSMakeRect(48, 8, 14, 14), green_color, "+")
        zoom_button.setTarget_(self)
        zoom_button.setAction_("zoomWindow:")
        self.drag_area.addSubview_(zoom_button)
        # Update the webview sizing and insert it below drag area.
        content_view.addSubview_(self.webview)
        self.webview.setFrame_(NSMakeRect(0, 0, content_bounds.size.width, content_bounds.size.height - DRAG_AREA_HEIGHT))
        # Set up script message handler for background color changes
        configuration = self.webview.configuration()
        user_content_controller = configuration.userContentController()
        user_content_controller.addScriptMessageHandler_name_(self, "backgroundColorHandler")
        # Inject JavaScript to monitor background color changes
        script = """
            function _post(bg){try{const h=window.webkit?.messageHandlers?.backgroundColorHandler;h&&h.postMessage(bg);}catch(e){}}
            function _getColor(el){if(!el) return null; const c=getComputedStyle(el).backgroundColor; return (!c||c==='rgba(0, 0, 0, 0)'||c==='transparent')?null:c;}
            function sendBackgroundColor(){
                const bg=_getColor(document.body)||_getColor(document.documentElement)||'rgb(255,255,255)';
                _post(bg);
            }
            document.addEventListener('DOMContentLoaded', sendBackgroundColor);
            window.addEventListener('load', sendBackgroundColor);
            new MutationObserver(sendBackgroundColor).observe(document.documentElement,{attributes:true,attributeFilter:['style'],subtree:true,childList:true});
        """
        user_script = WKUserScript.alloc().initWithSource_injectionTime_forMainFrameOnly_(script, WKUserScriptInjectionTimeAtDocumentEnd, True)
        user_content_controller.addUserScript_(user_script)
        # Create status bar item with logo
        self.status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(NSSquareStatusItemLength)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_white_path = os.path.join(script_dir, LOGO_WHITE_PATH)
        self.logo_white = NSImage.alloc().initWithContentsOfFile_(logo_white_path)
        self.logo_white.setSize_(NSSize(22, 22))
        logo_black_path = os.path.join(script_dir, LOGO_BLACK_PATH)
        self.logo_black = NSImage.alloc().initWithContentsOfFile_(logo_black_path)
        self.logo_black.setSize_(NSSize(22, 22))
        # Set the initial logo image based on the current appearance
        self.updateStatusItemImage()
        # Observe system appearance changes
        self.status_item.button().addObserver_forKeyPath_options_context_(
            self, "effectiveAppearance", NSKeyValueObservingOptionNew, STATUS_ITEM_CONTEXT
        )
        # Create the main application menu bar
        mainMenu = NSMenu.alloc().init()
        # Create the application menu (appears under "Grok" in menu bar)
        appMenuItem = NSMenuItem.alloc().init()
        mainMenu.addItem_(appMenuItem)
        appMenu = NSMenu.alloc().init()
        # About Grok
        aboutMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(f"About {APP_TITLE}", "showAbout:", "")
        aboutMenuItem.setTarget_(self)
        appMenu.addItem_(aboutMenuItem)
        appMenu.addItem_(NSMenuItem.separatorItem())
        # Hide Grok
        hideMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(f"Hide {APP_TITLE}", "hide:", "h")
        appMenu.addItem_(hideMenuItem)
        # Hide Others
        hideOthersMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Hide Others", "hideOtherApplications:", "h")
        hideOthersMenuItem.setKeyEquivalentModifierMask_(NSEventModifierFlagCommand | NSEventModifierFlagOption)
        appMenu.addItem_(hideOthersMenuItem)
        # Show All
        showAllMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Show All", "unhideAllApplications:", "")
        appMenu.addItem_(showAllMenuItem)
        appMenu.addItem_(NSMenuItem.separatorItem())
        # Quit Grok
        quitMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(f"Quit {APP_TITLE}", "terminate:", "q")
        appMenu.addItem_(quitMenuItem)
        appMenuItem.setSubmenu_(appMenu)
        NSApp.setMainMenu_(mainMenu)
        
        # Create status bar menu
        menu = NSMenu.alloc().init()
        # Create and configure menu items with explicit targets
        show_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Show "+APP_TITLE, "showWindow:", "")
        show_item.setTarget_(self)
        menu.addItem_(show_item)
        hide_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Hide "+APP_TITLE, "hideWindow:", "h")
        hide_item.setTarget_(self)
        menu.addItem_(hide_item)
        home_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Home", "goToWebsite:", "g")
        home_item.setTarget_(self)
        menu.addItem_(home_item)
        clear_data_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Clear Web Cache", "clearWebViewData:", "")
        clear_data_item.setTarget_(self)
        menu.addItem_(clear_data_item)
        set_trigger_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Set New Trigger", "setTrigger:", "")
        set_trigger_item.setTarget_(self)
        menu.addItem_(set_trigger_item)
        install_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Install Autolauncher", "install:", "")
        install_item.setTarget_(self)
        menu.addItem_(install_item)
        uninstall_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Uninstall Autolauncher", "uninstall:", "")
        uninstall_item.setTarget_(self)
        menu.addItem_(uninstall_item)
        menu.addItem_(NSMenuItem.separatorItem())
        about_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("About Grok", "showAbout:", "")
        about_item.setTarget_(self)
        menu.addItem_(about_item)
        menu.addItem_(NSMenuItem.separatorItem())
        quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Quit Grok", "terminate:", "q")
        quit_item.setTarget_(NSApp)
        menu.addItem_(quit_item)
        # Set the menu for the status item
        self.status_item.setMenu_(menu)
        # Add resize observer
        NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(
            self, 'windowDidResize:', NSWindowDidResizeNotification, self.window
        )
        # Add local mouse event monitor for left mouse down
        self.local_mouse_monitor = NSEvent.addLocalMonitorForEventsMatchingMask_handler_(
            NSEventMaskLeftMouseDown,  # Monitor left mouse-down events
            self.handleLocalMouseEvent  # Handler method
        )
        # Create the event tap for key-down events
        tap = CGEventTapCreate(
            kCGSessionEventTap, # Tap at the session level
            kCGHeadInsertEventTap, # Insert at the head of the event queue
            kCGEventTapOptionDefault, # Actively filter events
            CGEventMaskBit(kCGEventKeyDown), # Capture key-down events
            global_show_hide_listener(self), # Your callback function
            None # Optional user info (refcon)
        )
        if tap:
            # Integrate the tap into the run loop
            source = CFMachPortCreateRunLoopSource(None, tap, 0)
            CFRunLoopAddSource(CFRunLoopGetCurrent(), source, kCFRunLoopCommonModes)
            CGEventTapEnable(tap, True)
            # CFRunLoopRun() # Start the run loop (causes HANG as of Tahoe)
        else:
            print("Failed to create event tap. Check Accessibility permissions.")
        # Load the custom launch trigger if the user set it.
        load_custom_launcher_trigger()
        # Set the delegate of the window to this parent application.
        self.window.setDelegate_(self)
        # Make sure this window is shown and focused.
        self.showWindow_(None)
        # Defer website loading until after window is visible (improves startup time)
        self.performSelector_withObject_afterDelay_("loadWebsite:", None, 0.1)
        # Request microphone permission after a short delay (non-blocking)
        self.performSelector_withObject_afterDelay_("requestMicrophonePermissionDeferred:", None, 1.0)

    # Deferred website loading to improve startup performance
    def loadWebsite_(self, sender):
        url = NSURL.URLWithString_(WEBSITE)
        request = NSURLRequest.requestWithURL_(url)
        self.webview.loadRequest_(request)

    # Deferred microphone permission request (non-blocking)
    def requestMicrophonePermissionDeferred_(self, sender):
        request_microphone_permission()

    # Logic to show the overlay, make it the key window, and focus on the typing area.
    def showWindow_(self, sender):
        self.window.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)
        # Execute the JavaScript to focus the textarea in the WKWebView
        self.webview.evaluateJavaScript_completionHandler_(
            "document.querySelector('textarea').focus();", None
        )

    # Hide the overlay and allow focus to return to the next visible application.
    def hideWindow_(self, sender):
        # Close About window if it's open
        if hasattr(self, 'aboutWindow') and self.aboutWindow:
            self.aboutWindow.close()
            self.aboutWindow = None
        NSApp.hide_(None)
    
    # Minimize the window to the dock with animation.
    def minimizeWindow_(self, sender):
        # Standard macOS minimize animation to Dock
        self.window.miniaturize_(self)
    
    # Zoom/maximize the window.
    def zoomWindow_(self, sender):
        self.window.zoom_(None)
    
    # Go to the default landing website for the overlay (in case accidentally navigated away).
    def goToWebsite_(self, sender):
        url = NSURL.URLWithString_(WEBSITE)
        request = NSURLRequest.requestWithURL_(url)
        self.webview.loadRequest_(request)
    
    # Clear the webview cache data (in case cookies cause errors).
    def clearWebViewData_(self, sender):
        dataStore = self.webview.configuration().websiteDataStore()
        dataTypes = WKWebsiteDataStore.allWebsiteDataTypes()
        dataStore.removeDataOfTypes_modifiedSince_completionHandler_(
            dataTypes,
            NSDate.distantPast(),
            lambda: print("Data cleared")
        )

    # Go to the default landing website for the overlay (in case accidentally navigated away).
    def install_(self, sender):
        if install_startup():
            # Exit the current process since a new one will launch.
            print("Installation successful, exiting.", flush=True)
            NSApp.terminate_(None)
        else:
            print("Installation unsuccessful.", flush=True)

    # Go to the default landing website for the overlay (in case accidentally navigated away).
    def uninstall_(self, sender):
        if uninstall_startup():
            NSApp.hide_(None)

    # Handle the 'Set Trigger' menu item click.
    def setTrigger_(self, sender):
        set_custom_launcher_trigger(self)

    # Handle the 'About' menu item click.
    def showAbout_(self, sender):
        # Read version from about/version.txt
        script_dir = os.path.dirname(os.path.abspath(__file__))
        version = "1.0"
        try:
            with open(os.path.join(script_dir, "about", "version.txt"), "r") as f:
                version = f.read().strip()
        except:
            pass
        
        # Create modern Tahoe-style About window
        aboutWindow = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(0, 0, 280, 340),
            NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskFullSizeContentView,
            NSBackingStoreBuffered,
            False
        )
        aboutWindow.setTitle_("")
        aboutWindow.setTitlebarAppearsTransparent_(True)
        aboutWindow.setMovableByWindowBackground_(True)
        aboutWindow.center()
        
        contentView = aboutWindow.contentView()
        contentView.setWantsLayer_(True)
        
        # App Icon
        logo_path = os.path.join(script_dir, LOGO_BLACK_PATH)
        icon = NSImage.alloc().initWithContentsOfFile_(logo_path)
        if icon:
            icon.setSize_(NSSize(64, 64))
            iconView = NSImageView.alloc().initWithFrame_(NSMakeRect(108, 248, 64, 64))
            iconView.setImage_(icon)
            iconView.setImageScaling_(NSImageScaleProportionallyUpOrDown)
            contentView.addSubview_(iconView)
        
        # App Name
        appNameLabel = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 215, 280, 28))
        appNameLabel.setStringValue_(APP_TITLE)
        appNameLabel.setBezeled_(False)
        appNameLabel.setDrawsBackground_(False)
        appNameLabel.setEditable_(False)
        appNameLabel.setSelectable_(False)
        appNameLabel.setAlignment_(NSTextAlignmentCenter)
        appNameLabel.setFont_(NSFont.boldSystemFontOfSize_(21))
        contentView.addSubview_(appNameLabel)
        
        # Version
        versionLabel = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 193, 280, 18))
        versionLabel.setStringValue_(f"Version {version}")
        versionLabel.setBezeled_(False)
        versionLabel.setDrawsBackground_(False)
        versionLabel.setEditable_(False)
        versionLabel.setSelectable_(False)
        versionLabel.setAlignment_(NSTextAlignmentCenter)
        versionLabel.setTextColor_(NSColor.secondaryLabelColor())
        versionLabel.setFont_(NSFont.systemFontOfSize_(11))
        contentView.addSubview_(versionLabel)
        
        # Description
        descLabel = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 145, 240, 40))
        descLabel.setStringValue_("A native macOS overlay for Grok AI.\nPress ⌥ Space to summon anywhere.")
        descLabel.setBezeled_(False)
        descLabel.setDrawsBackground_(False)
        descLabel.setEditable_(False)
        descLabel.setSelectable_(False)
        descLabel.setAlignment_(NSTextAlignmentCenter)
        descLabel.setFont_(NSFont.systemFontOfSize_(11))
        descLabel.setTextColor_(NSColor.secondaryLabelColor())
        contentView.addSubview_(descLabel)
        
        # Developer Card Background
        devCard = NSView.alloc().initWithFrame_(NSMakeRect(20, 50, 240, 85))
        devCard.setWantsLayer_(True)
        devCard.layer().setBackgroundColor_(NSColor.quaternaryLabelColor().CGColor())
        devCard.layer().setCornerRadius_(10)
        contentView.addSubview_(devCard)
        
        # Developer Name
        devNameLabel = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 55, 240, 20))
        devNameLabel.setStringValue_("Sumit Duster")
        devNameLabel.setBezeled_(False)
        devNameLabel.setDrawsBackground_(False)
        devNameLabel.setEditable_(False)
        devNameLabel.setSelectable_(False)
        devNameLabel.setAlignment_(NSTextAlignmentCenter)
        devNameLabel.setFont_(NSFont.boldSystemFontOfSize_(13))
        devCard.addSubview_(devNameLabel)
        
        # Developer Role
        devRoleLabel = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 35, 240, 18))
        devRoleLabel.setStringValue_("Developer")
        devRoleLabel.setBezeled_(False)
        devRoleLabel.setDrawsBackground_(False)
        devRoleLabel.setEditable_(False)
        devRoleLabel.setSelectable_(False)
        devRoleLabel.setAlignment_(NSTextAlignmentCenter)
        devRoleLabel.setFont_(NSFont.systemFontOfSize_(11))
        devRoleLabel.setTextColor_(NSColor.secondaryLabelColor())
        devCard.addSubview_(devRoleLabel)
        
        # Developer Bio
        bioLabel = NSTextField.alloc().initWithFrame_(NSMakeRect(10, 8, 220, 28))
        bioLabel.setStringValue_("macOS & iOS Developer\nBuilding intuitive apps")
        bioLabel.setBezeled_(False)
        bioLabel.setDrawsBackground_(False)
        bioLabel.setEditable_(False)
        bioLabel.setSelectable_(False)
        bioLabel.setAlignment_(NSTextAlignmentCenter)
        bioLabel.setFont_(NSFont.systemFontOfSize_(10))
        bioLabel.setTextColor_(NSColor.tertiaryLabelColor())
        devCard.addSubview_(bioLabel)
        
        # Copyright
        copyrightLabel = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 20, 280, 16))
        copyrightLabel.setStringValue_("© 2025 Sumit Duster")
        copyrightLabel.setBezeled_(False)
        copyrightLabel.setDrawsBackground_(False)
        copyrightLabel.setEditable_(False)
        copyrightLabel.setSelectable_(False)
        copyrightLabel.setAlignment_(NSTextAlignmentCenter)
        copyrightLabel.setFont_(NSFont.systemFontOfSize_(10))
        copyrightLabel.setTextColor_(NSColor.tertiaryLabelColor())
        contentView.addSubview_(copyrightLabel)
        
        # Show the window
        self.aboutWindow = aboutWindow
        self.aboutWindow.setReleasedWhenClosed_(False)
        self.aboutWindow.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)

    # For capturing key commands while the key window (in focus).
    def keyDown_(self, event):
        modifiers = event.modifierFlags()
        key_command = modifiers & NSEventModifierFlagCommand
        key_alt = modifiers & NSEventModifierFlagOption
        key_shift = modifiers & NSEventModifierFlagShift
        key_control = modifiers & NSEventModifierFlagControl
        key = event.charactersIgnoringModifiers()
        # Command (NOT alt)
        if (key_command or key_control) and (not key_alt):
            # Select all
            if key == 'a':
                self.window.firstResponder().selectAll_(None)
            # Copy
            elif key == 'c':
                self.window.firstResponder().copy_(None)
            # Cut
            elif key == 'x':
                self.window.firstResponder().cut_(None)
            # Paste
            elif key == 'v':
                self.window.firstResponder().paste_(None)
            # Hide
            elif key == 'h':
                self.hideWindow_(None)
            # Quit
            elif key == 'q':
                NSApp.terminate_(None)
            # # Undo (causes crash for some reason)
            # elif key == 'z':
            #     self.window.firstResponder().undo_(None)

    # Handler for capturing a click-and-drag event when not already the key window.
    @objc.python_method
    def handleLocalMouseEvent(self, event):
        if event.window() == self.window:
            # Get the click location in window coordinates
            click_location = event.locationInWindow()
            # Use hitTest_ to determine which view receives the click
            hit_view = self.window.contentView().hitTest_(click_location)
            # Check if the hit view is the drag area
            if hit_view == self.drag_area:
                # Bring the window to the front and make it key
                self.showWindow_(None)
                # Initiate window dragging with the event
                self.window.performWindowDragWithEvent_(event)
                return None  # Consume the event
        return event  # Pass unhandled events along

    # Handler for when the window resizes (adjusts the drag area).
    def windowDidResize_(self, notification):
        bounds = self.window.contentView().bounds()
        w, h = bounds.size.width, bounds.size.height
        self.drag_area.setFrame_(NSMakeRect(0, h - DRAG_AREA_HEIGHT, w, DRAG_AREA_HEIGHT))
        self.webview.setFrame_(NSMakeRect(0, 0, w, h - DRAG_AREA_HEIGHT))

    # Handler for setting the background color based on the web page background color.
    def userContentController_didReceiveScriptMessage_(self, userContentController, message):
        if message.name() == "backgroundColorHandler":
            bg_color_str = message.body()
            # Convert CSS color to NSColor (assuming RGB for simplicity)
            if bg_color_str.startswith("rgb") and ("(" in bg_color_str) and (")" in bg_color_str):
                rgb_values = [float(val) for val in bg_color_str[bg_color_str.index("(")+1:bg_color_str.index(")")].split(",")]
                r, g, b = [val / 255.0 for val in rgb_values[:3]]
                color = NSColor.colorWithCalibratedRed_green_blue_alpha_(r, g, b, 1.0)
                self.drag_area.setBackgroundColor_(color)

    # Logic for checking what color the logo in the status bar should be, and setting appropriate logo.
    def updateStatusItemImage(self):
        appearance = self.status_item.button().effectiveAppearance()
        if appearance.bestMatchFromAppearancesWithNames_([NSAppearanceNameAqua, NSAppearanceNameDarkAqua]) == NSAppearanceNameDarkAqua:
            self.status_item.button().setImage_(self.logo_white)
        else:
            self.status_item.button().setImage_(self.logo_black)

    # Observer that is triggered whenever the color of the status bar logo might need to be updated.
    def observeValueForKeyPath_ofObject_change_context_(self, keyPath, object, change, context):
        if context == STATUS_ITEM_CONTEXT and keyPath == "effectiveAppearance":
            self.updateStatusItemImage()

    # System triggered appearance changes that might affect logo color.
    def appearanceDidChange_(self, notification):
        # Update the logo image when the system appearance changes
        self.updateStatusItemImage()