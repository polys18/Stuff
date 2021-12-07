import random

class Simba:

    def __init__(self, canvas, x, y, color):
        """
        The constructor creates the variables below for each pixel (canvas pixels are
        called pixes).
        """
        self.x = x
        self.y = y
        self.color = color
        self.pix = canvas.create_rectangle(self.x, self.y, self.x, self.y, fill = self.color, outline = self.color)
        self.change_x = random.randint(-10, 10)
        self.change_y = random.randint(-10, 10)


    def disappear(self, canvas):
        """
        This method makes a pix (canvas pixel) move in a random direction.
        """
        canvas.move(self.pix, self.change_x, self.change_y)


    def appear(self, canvas):
        """
        This method makes the pix move in the opposite direction.
        """
        canvas.move(self.pix, -self.change_x, -self.change_y)
