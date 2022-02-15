# Main file for the project.
import cv2 as cv
from cv2 import rectangle
import numpy as np
import os
from time import time
from Sections.windowcapture import WindowCapture
from Sections.vision import Vision
from time import time
from multiprocessing import Process, Manager
from multiprocessing.managers import BaseManager
import multiprocessing


def process1(queue):
    wincap = WindowCapture('opsu!')
    cascade_circles = cv.CascadeClassifier('cascade/cascade.xml')
    vision_circles = Vision(None)

    loop_time = time()
    while(True):

        # Captures the current frame of the game for analysis
        screenshot = wincap.take_ss()

        # Old template matching code
        #points = vision_circles.find(screenshot, 0.5, 'rectangles')

        # Detects possible objects in the screenshot.
        rectangles = cascade_circles.detectMultiScale(screenshot)

        # Highlights said objects.
        detection_image = vision_circles.draw_rectangles(screenshot, rectangles)

        # Displays the screenshot after the possible objects have been highlighted.
        cv.imshow('osuML', detection_image)

        # debug the loop rate
        print('FPS {}'.format(1 / (time() - loop_time)))
        loop_time = time()

        # press 'q' with the output window focused to exit.
        # waits 1 ms every loop to process key presses
        key = cv.waitKey(1)
        if key == ord('q'):
            cv.destroyAllWindows()
            break
        elif key == ord('d'):
            cv.imwrite(f'Sections/positive/{loop_time}.jpg', screenshot)
        elif key == ord('f'):  
            cv.imwrite(f'Sections/negative/{loop_time}.jpg', screenshot)
    while True:
        queue.put(wincap.take_ss())

def process2(queue,display_queue):
    cascade = cv.CascadeClassifier(cv.data.haarcascades + 'cascade.xml')
    # assert not cascade.empty()
    # vision = Vision()
    flip = 0
    rectangles = []
    while True:
        while not queue.empty():
            screenshot = queue.get()
            flip += 1
            if flip % 15 == 0:
                rectangles = cascade.detectMultiScale(
                    screenshot,
                    scaleFactor=1.1
                    #minNeighbors=3
                    #minSize=(40,40)
                    #flags=cv.CASCADE_SCALE_IMAGE
                )
            
            if len(rectangles) > 0:
                detection_image = vision.draw_rectangles(screenshot, rectangles)
            else:
                detection_image = screenshot
            display_queue.put(detection_image)

def process3(display_queue):
    while True:
        while not display_queue.empty():
            screenshot = display_queue.get()
            cv.imshow('Matches', screenshot)
            key = cv.waitKey(1)

if __name__ == "__main__":
    queue = multiprocessing.Queue()
    display_queue = multiprocessing.Queue()
    p1 = Process(target=process1, args=(queue,))
    p2 = Process(target=process2, args=(queue,display_queue,))
    p3 = Process(target=process3, args=(display_queue,))
    
    p1.start()
    p2.start()
    p3.start()