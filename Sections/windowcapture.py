import numpy as np
import win32gui, win32ui, win32con

class WindowCapture(object):
    # Threading properties.
    stopped = True
    lock = None
    screenshot = None
    # Properties
    w = 0
    h = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0
    
    # Constructor
    def __init__(self, window_name = None):
        
        # Create a thread locked object.
        # We also want to find the window title so we can capture the correct window.
        # And if no window is given we will capture the entire screen.
        
        if window_name is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            self.hwnd = win32gui.FindWindow(None, window_name)