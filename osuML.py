# Main file for the project.

# Imports
from multiprocessing.dummy import Process
import cv2 as cv
from Sections.windowcapture import WindowCapture
from Sections.vision import Vision
from Sections.bot import Bot
import multiprocessing
from Sections.cascadedetect import Detection


def process1(queue):
    # Selects the window we want to capture.
    wincap = WindowCapture('opsu!')
    # Loads our cascade file for use in detection.
    detect = Detection('cascade/cascade.xml')
    # Starts a Vision thread we can use to draw.
    vision = Vision()
    bot = Bot()

    # Starts screen capturing.
    wincap.start()
    # Starts our detection thread.
    detect.start()
    # Starts or bot thread.
    bot.start()

    # This is the loop that updates, detects, and draw our squares.
    while(True):
        # If theres no screenshot this won't run. Again to save resources.
        if wincap.screenshot is None:
            continue
        # Captures the current frame of the game for analysis.
        detect.update(wincap.screenshot)
        bot.update_points(vision.get_click_points(detect.rectangles))
        # Draws the rectangles on the current screenshot.
        detection_image = vision.draw_rectangles(wincap.screenshot, detect.rectangles)
        # Displays the edited screenshot.
        cv.imshow('osuML!', detection_image)

        # Commands to close the window/bot.
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            wincap.stop()
            detect.stop()
            bot.stop()
            break

# Main func later will have other functions for reacting to the inputs
if __name__ == "__main__":
    queue = multiprocessing.Queue()
    display_queue = multiprocessing.Queue()
    p1 = Process(target=process1, args=(queue,))  
    p1.start()
