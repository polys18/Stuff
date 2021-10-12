"""
This program maps an image onto a canvas and makes it cinematically disappear when the mouse
is on the canvas. When the mouse is off the canvas the image reforms.

The smaller the picture the faster the program!

*Its called simba because the first picture I used was the picture of simba.
"""
from simpleimage import SimpleImage
import tkinter
from graphics import Canvas
from simba import Simba
import time
IMAGE = '/Users/polys/Downloads/Assignment3_starter_code_simba/images/simba.jpg'

def rgb_to_hex(rgb):
    """
    This function converts rgb values to a hexadecimal that canvas can understand
    """
    hex_red = "%02x" % rgb[0]
    hex_green = "%02x" % rgb[1]
    hex_blue = "%02x" % rgb[2]
    hex_color = "#" + hex_red + hex_green + hex_blue
    return hex_color


def main():
    """
    The main function creates instances of pixels that are at the same position and color as
     in the image in the canvas. Then, in the animation loop each pixel moves in a random
     direction if the mouse is over the canvas. The pixels move back to their original
     positions when the mouse is not on the canvas.
    """
    directory = input("Enter image directory: ")
    image = SimpleImage(directory)
    canvas = Canvas(image.width, image.height, 'simba')
    pixes = []
    for pixel in image:
        rgb = (pixel.red, pixel.green, pixel.blue)
        hex = rgb_to_hex(rgb)
        pix = Simba(canvas, pixel.x, pixel.y, hex)
        pixes.append(pix)

    count = 0
    while True:

        if mouse_on_canvas(canvas, image):
            for pix in pixes:
                pix.disappear(canvas)
            count += 1
        elif mouse_on_canvas(canvas, image) == False and count > 0:
            for i in range(count):
                for pix in pixes:
                    pix.appear(canvas)
                canvas.update()
                time.sleep(1/50)
                count -= 1
        canvas.update()
        time.sleep(1/50)


def mouse_on_canvas(canvas, image):
    """
    This function returns true if the mouse is over the canvas.
    """
    mouse_x = canvas.get_mouse_x()
    mouse_y = canvas.get_mouse_y()
    if 0 <= mouse_x <= image.width and 0 <= mouse_y <= image.height:
        return True
    else:
        return False


if __name__ == "__main__":
    main()