# Import libraries

import tkinter as tk
from PIL import Image, ImageDraw
import cv2
import matplotlib.pyplot as plt
from skimage import color,io
import inflect
import numpy as np

from keras.models import model_from_json

# Import keras model and weights trained from Google Colab on MNIST dataset
# Model reconstruction from JSON file

with open('model_mnist.json', 'r') as f:
    model = model_from_json(f.read())

# Load weights into the new model
model.load_weights('model_mnist.h5')

# Save model architecture to image

from keras.utils import plot_model
plot_model(model, to_file='model_arch.png')


p = inflect.engine()
p.number_to_words(99)


def image_resize(image, width=28, height=28, inter=cv2.INTER_AREA):
    '''
    Resizes a image to specified dimension.
    '''
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)

    else:
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized


class ImageGenerator:
    def __init__(self, parent, posx, posy, *kwargs):
        '''
        Opens a canvas and allows user to write.
        '''
        self.parent = parent
        self.posx = posx
        self.posy = posy
        self.sizex = 150
        self.sizey = 150
        self.b1 = "up"
        self.xold = None
        self.yold = None
        self.drawing_area = tk.Canvas(
            self.parent, width=self.sizex, height=self.sizey)
        self.drawing_area.place(x=self.posx, y=self.posy)
        self.drawing_area.bind("<Motion>", self.motion)
        self.drawing_area.bind("<ButtonPress-1>", self.b1down)
        self.drawing_area.bind("<ButtonRelease-1>", self.b1up)
        self.button = tk.Button(
            self.parent, text="Done!", width=10, bg='white', command=self.save)
        self.button.place(x=self.sizex / 7, y=self.sizey + 20)
        self.button1 = tk.Button(
            self.parent,
            text="Clear!",
            width=10,
            bg='white',
            command=self.clear)
        self.button1.place(x=(self.sizex / 7) + 80, y=self.sizey + 20)

        
        self.image = Image.new("RGB", (150, 150), (0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)

    def save(self):
        '''
        Saves the canvas to an image and resize to 28*28.
        Feeds 28*28 image to the CNN model.
        Make predictions from the model.
        '''
        filename = "temp.jpg"
        self.image.save(filename)
        img = cv2.imread('temp.jpg')
        img = color.rgb2gray(img)

        img = image_resize(img)

        img *= (255.0 / img.max())

        plt.imshow(img,cmap='gray')
        img = img.reshape(1, 28, 28, 1)
        label = int(model.predict_classes(img))
        prob = np.max(model.predict_proba(img))
        
        if prob < 0.5:
            self.drawing_area.create_text(
            80,
            20,
            fill="red",
            font=("Purisa", 16),
            text="Can't understand please write properly")

        print('Entered',label)
        label = p.number_to_words(label)
        self.drawing_area.create_text(
            80,
            20,
            fill="red",
            font=("Purisa", 16),
            text="Entered :" + label + '!')

    def clear(self):
        '''
        Clears the canvas
        '''
        self.drawing_area.delete("all")
        self.image = Image.new("RGB", (150, 150), (0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)

    def b1down(self, event):
        '''
        Mouse butoon is clicked to write
        '''
        self.b1 = "down"

    def b1up(self, event):
        '''
        Mouse butoon is released after writing
        '''
        self.b1 = "up"
        self.xold = None
        self.yold = None

    def motion(self, event):
        '''
        In between mouse button pressed and released.
        '''
        if self.b1 == "down":
            if self.xold is not None and self.yold is not None:
                event.widget.create_line(
                    self.xold,
                    self.yold,
                    event.x,
                    event.y,
                    smooth='true',
                    width=6,
                    fill='#003cb3')
                self.draw.line(((self.xold, self.yold), (event.x, event.y)),
                               (0, 0, 255),
                               width=20)

        self.xold = event.x
        self.yold = event.y


if __name__ == "__main__":
    root = tk.Tk()
    root.wm_geometry("%dx%d+%d+%d" % (500, 500, 10, 10))
    root.config(bg='white')
    print('Entered Numbers are')
    ImageGenerator(root, 10, 10)
    root.mainloop()
