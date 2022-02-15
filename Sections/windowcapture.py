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
            if not self.hwnd:
                raise Exception(f'Window not found: {window_name}')

        # Get the size of the selected window.
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]

        # Cut off the window border/title and crop them out
        border_pixels = 8
        titlebar_pixels = 30
        self.w = self.w - (border_pixels * 2)
        self.h = self.h - (titlebar_pixels - border_pixels)
        self.cropped_x = border_pixels
        self.cropped_y = titlebar_pixels

        # Calculate the window offset to make taking screenshots easier.
        self.offset_x = window_rect[0] + self.cropped_x
        self.offset_y = window_rect[1] + self.cropped_y

    # Returns the current screenshot
    def current_ss(self):
        return self.screenshot

    # Takes a screenshot of the active/selected window
    def take_ss(self):
        # Get window data and make a bitmap 'image'
        windowContext = win32gui.GetWindowDC(self.hwnd)
        contextObj = win32ui.CreateDCFromHandle(windowContext)
        compatibleContext = contextObj.CreateCompatibleDC()
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(contextObj, self.w, self.h)
        compatibleContext.SelectObject(bitmap)
        compatibleContext.BitBlt((0, 0), (self.w, self.h), contextObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

        # Next we need to convert the data into a format opencv can process
        signedIntsArray = bitmap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype = 'uint8')
        img.shape = (self.h, self.w, 4)

        # Free up computer resources to keep things speedy.
        contextObj.DeleteDC()
        compatibleContext.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, windowContext)
        win32gui.DeleteObject(bitmap.GetHandle())

        # We need to drop the alpha channel or opencv's template match will throw and error.
        img = img[...,:3]

        # Make the image C_CONTIGUOUS to avoid errors.
        # Discussion thread:
        # https://github.com/opencv/opencv/issues/14866#issuecomment-580207109
        img = np.ascontiguousarray(img)

        return img

    # Find the window that has a matching name the update the window capture
    @staticmethod
    def window_names():
        def winEnumHandler(hwnd, ctx):
            print(win32gui.EnumWindows(winEnumHandler, None))
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))
        win32gui.EnumWindows(winEnumHandler, None)

    # This function is used to translate the screenshot image to the pixel position.
    def screen_position(self, pos):
        return (pos[0] + self.offset_x, pos[1] + self.offset_y)