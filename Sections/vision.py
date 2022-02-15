# Imports
import cv2 as cv

# This lets us import it into other py files.
class Vision:

    # This function takes all of our rectangles and finds the center of them so we know where we'll have to click in the future.
    # It then saves them to points. This is unused at the moment just a placeholder for how things might be done.
    def get_click_points(self, rectangles):
        points = []

        # Loop over all the rectangles
        for (x, y, w, h) in rectangles:
            # Determine the center position
            center_x = x + int(w/2)
            center_y = y + int(h/2)
            # Save the points
            points.append((center_x, center_y))

        return points

    # This function get provided with the rectangles list so it can then draw them to our screenshot for viewing. Might change this to circles in the future.
    def draw_rectangles(self, haystack_img, rectangles):
        # Sets the color to lime green (R, G, B)
        line_color = (0, 255, 0)
        # Sets our line type to a solid line.
        line_type = cv.LINE_4

        for (x, y, w, h) in rectangles:
            # determine the box positions
            top_left = (x, y)
            bottom_right = (x + w, y + h)
            # draw the box
            cv.rectangle(haystack_img, top_left, bottom_right, line_color, lineType=line_type)

        return haystack_img