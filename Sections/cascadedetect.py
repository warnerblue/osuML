# Imports
import cv2 as cv
from threading import Thread, Lock
import numpy as np
import time

# This lets us import it into other py files.
class Detection:

    # Thread properties
    stopped = True
    lock = None
    rectangles = []
    # Placeholders
    cascade = None
    screenshot = None

    def __init__(self, model_file_path):
        # Creates a thread and locks it
        self.lock = Lock()
        # Loads our cascade model
        self.cascade = cv.CascadeClassifier(model_file_path)

    # This function lets us update the screenshot variable outside of the thread for use in the thread.
    def update(self, screenshot):
        self.lock.acquire()
        self.screenshot = screenshot
        self.lock.release()

    # Starts our detection thread
    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True
    
    # This function loops our thread.
    def run(self):
        # As long as the thread isn't stopped this code will continue looping.
        while not self.stopped:
            # This makes sure a screenshot is set because if not we are wasting resources.
            if not self.screenshot is None:
                # This does our object detection using our cascade model.
                rectangles = self.cascade.detectMultiScale(self.screenshot)
                # This combines our detects that are small and close together.
                rectList = cv.groupRectangles(np.concatenate((rectangles, rectangles)), 1, eps=.1)[0]
                # This locks the thread so we can update our results. If we dont do this we could run into errors.
                self.lock.acquire()
                self.rectangles = rectList
                self.lock.release()