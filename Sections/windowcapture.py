# Imports
import numpy as np
import win32gui, win32ui, win32con
from threading import Thread, Lock

# This lets us import it into other py files.
class WindowCapture:

    # Thread properties
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

    # Our constructor class so we can provide variables.
    def __init__(self, window_name=None):
        # Creates a thread locked object
        self.lock = Lock()

        # This finds the windows by a specified name. If no name is provided it will record the entire screen.
        if window_name is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            self.hwnd = win32gui.FindWindow(None, window_name)
            if not self.hwnd:
                raise Exception(f'Window not found: {window_name}')

        # These lines get the size of the window.
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]

        # These are used to cut off the window boarder.
        border_pixels = 0
        titlebar_pixels = 30
        self.w = self.w - (border_pixels * 2)
        self.h = self.h - titlebar_pixels - border_pixels
        self.cropped_x = border_pixels
        self.cropped_y = titlebar_pixels

        # Sets the image coordinates to match its position on the desktop.
        self.offset_x = window_rect[0] + self.cropped_x
        self.offset_y = window_rect[1] + self.cropped_y

    # This function takes screenshots and converts them to a bitmap for easy storage.
    def take_ss(self):

        # get the window image data
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

        # Here we convert the raw data into a data type opencv can understand.
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.h, self.w, 4)

        # Here we delete unneeded objects to clear up memory.
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # We drop the alpha channel so we can match OpenCV's template.
        img = img[...,:3]

        # Tuple -> int
        img = np.ascontiguousarray(img)

        return img

    # Gets all the window names and finds the one that matches. Then we store its hex so when the window title changes we can still track the same window.
    @staticmethod
    def list_window_names():
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))
        win32gui.EnumWindows(winEnumHandler, None)

    # This function is used to translate screenshot coordinates to desktop coordinates.
    def get_screen_positions(self, positions):
        pos = []
        for (x, y) in positions:
            pos.append(((x + self.offset_x), (y + self.offset_y)))
        return pos

    # Starts a thread.
    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    # Stops this thread.
    def stop(self):
        self.stopped = True

    # Our loop function for this thread.
    def run(self):
        while not self.stopped:
            # Update the game image.
            screenshot = self.take_ss()
            # This locks the thread so we can update our results. If we dont do this we could run into errors.
            self.lock.acquire()
            self.screenshot = screenshot
            self.lock.release()