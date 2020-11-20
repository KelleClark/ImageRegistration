# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
from tkinter import Tk, filedialog, Frame, Label, Canvas, Button, simpledialog, filedialog
from PIL import Image, ImageTk
from time import time
from tkinter.messagebox import showinfo, askyesno
import argparse
import cv2
import filetype
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from fractions import Fraction

# Flag for determining if images are loaded
img = False
second_img = False

#To reload image 2 in the event of a type mismatch
img2_path = ""
##-------Launching the program-----------------------------------------------##
# For -h argument
def get_args():
    parser = argparse.ArgumentParser(description='Image Registration v1.0')
    parser.add_argument('-- ', default=" ",
                        help='A Graphical User Interface with no arguments.')
    args = parser.parse_args()
    return(args)


##-------Functions to open/read an image file and rendering in UI------------##

# Read in image referred to by path and conform to fit screen
def opencv_img(path):
    # read and convert image
    image = cv2.imread(path)
    defaultrows = 420
    defaultcolumn = 580
    # Set scale multiplier to the lowest of the following values:
    # 1
    # window row count / image row count
    # window column count / image column count
    scale = min(1, min(defaultrows / image.shape[0], defaultcolumn / image.shape[1]))

    # Set triangle corners used for affine transformation to top left, top right, and bottom left corners of image
    srcTri = np.array([[0, 0], [image.shape[1] - 1, 0], [0, image.shape[0] - 1]]).astype(np.float32)

    # Set location of top right and bottom left corners of resized image
    dstTri = np.array( [[0, 0], [int(image.shape[1] * scale), 0], [0, int(image.shape[0] * scale)]] ).astype(np.float32)

    # Perform affine transformation to resize image
    warp_mat = cv2.getAffineTransform(srcTri, dstTri)
    image = cv2.warpAffine(image, warp_mat, (image.shape[1], image.shape[0]))

    # Trim black border from resized image
    image = image[0:int(image.shape[0] * scale), 0:int(image.shape[1] * scale)]
    return(image)


# Convert it to ImageTK
# necessary to use cvtColor taking from BGR to expected RGB color
def convert_img(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # To proper format for tk
    im = Image.fromarray(image)
    imgtk = ImageTk.PhotoImage(image=im)
    return(imgtk)


##----------User Controls for the UI-----------------------------------------##

# Select the image to load
def select_img1(event):
    global img, second_img
    # Prompt the user
    path = filedialog.askopenfilename(title="Please Select Image")
    # if there is a path and it is readable
    if len(path) > 0 and cv2.haveImageReader(path): 
        update_img1(path)
        img = True
    else:
        showinfo("Error", "No Image was found at path or it is not readable.")

def select_img2(event):
    global second_img

    if img == False:
        showinfo("Error", "Load Image 1 First")
        return
    # Prompt the user
    path = filedialog.askopenfilename(title="Please Select Image 2")
    # if there is a path and it is readable
    if len(path) > 0 and cv2.haveImageReader(path):
        update_img2(path)
        second_img = True
    else:
        showinfo("Error", "No image was found at path or it is not readable.")


#Exit the program
def quit_img(event):
    root.destroy() #Kill the display
    sys.exit(0)

# Save the image to the main given path appending the name of any transformation
def save_img(event):

    #Check an image is loaded
    if not is_image():
        return

    name = filedialog.asksaveasfilename(confirmoverwrite=True)

    # If no name or an invalid name is given, cancel
    if name == "":
        return
    elif name[0] == ".":
        return
    #Default file type if none is given
    if "." not in name:
        name = name+".png"
    cv2.imwrite(name, new_img)




##---------GUI update image formating ---------------------------------------##
# User given path to image, open and format image return disp_img
def update_img1(path):
    global img1, image
    #Load the image
    image = opencv_img(path)
   
    #Convert and display
    disp_img = convert_img(image)
    img1.configure(image=disp_img)
    img1.image = disp_img
    return disp_img

def update_img2(path):
    global img2, image2, img2_path
    #Load the image
    img2_path = path
    image2 = opencv_img(path)
   
    #Convert and display
    disp_img = convert_img(image2)
    img2.configure(image=disp_img)
    img2.image = disp_img
    return disp_img


# A newly transformed image, new, is formatted for display
def update_new(img):
    global new, new_img
    new_img = img
    disp_img = convert_img(img)
    new.configure(image=disp_img)
    new.image = disp_img


# Check if the first image is loaded
def is_image():
    global img
    #Check that image 1 is loaded
    if not img:
        showinfo("Error", "Image 1 has not been selected. Please select image 1.")
        return False
    return True

##---------Pixel Transformations---------------------------------------------##


# point1
def setpoint1(event):
    global image, x1, y1, image1_points
    #Check that image 1 is loaded
    if not is_image():
        return

    x1 = event.x
    y1 = event.y
    print(x1, y1)

    #put a dot at the chosen point
    max_rad = max(image.shape[0], image.shape[1])
    radius = int(max_rad * (1/10))
    center = (x1, y1)
    
    new_image = np.copy(image)
    halo_filter = np.zeros((new_image.shape[0], new_image.shape[1], 3))
    halo_filter[:,:,:] = 0.80
    
    dot = cv2.circle(halo_filter, center, radius, (1,1,1), -1)
    new_image = np.uint8(new_image * dot)
    update_new(new_image)
   # img1.bind("<Button 1>",getextentx)

def setpoint2(event):
    global image, x1, y1, image2_points
    # Check that image 1 is loaded
    if not is_image():
        return

    x1 = event.x
    y1 = event.y
    print(x1, y1)

    # put a dot at the chosen point
    max_rad = max(image.shape[0], image.shape[1])
    radius = int(max_rad * (1 / 10))
    center = (x1, y1)

    new_image = np.copy(image)
    halo_filter = np.zeros((new_image.shape[0], new_image.shape[1], 3))
    halo_filter[:, :, :] = 0.80

    #dot = cv2.circle(halo_filter, center, radius, (1, 1, 1), -1)
    #new_image = np.uint8(new_image * dot)
    #update_new(new_image)
    #img1.bind("<Button 1>",getextentx)
   

##---------------------------------------------------------------------------##
def main():
    global root, img1, img2, new, image, image2new, image, image1_points, image2_points

    #Get the command arguments
    get_args()
    if len(sys.argv) != 1:
        print('Image Registration v1.0 is a GUI program without arguments')
        sys.exit(0)

    root = Tk()
    root.title("Image Registration.")
    
    # The original loaded images 
    img1 = Label(image=None)
    img1.pack(side="left", padx=10, pady=10)

    img2 = Label(image=None)
    img2.pack(side="left", padx=10, pady=10)

    # The new modifed image
    new = Label(image=None)
    new.pack(side="right", padx=10, pady=10)
    
    #mouseclick event
    img1.bind("<Button 1>",setpoint1)
    img2.bind("<Button 1>",setpoint2)

    # Frame to display navigation buttons at bottom of window
    frame = Frame()
    frame.pack()

    # Button for select image
    btn_select_img1 = Button(
        master = frame,
        text = "Select image 1",
        underline = 13
    )
    btn_select_img1.grid(row = 0, column = 1)
    btn_select_img1.bind('<ButtonRelease-1>', select_img1)

    btn_select_img2 = Button(
        master=frame,
        text="Select image 2",
        underline=13
    )
    btn_select_img2.grid(row=14, column=1)
    btn_select_img2.bind('<ButtonRelease-1>', select_img2)

 
  
    # Button for save_img image
    btn_save = Button(
        master = frame,
        text = "Save",
        underline = 0
    )
    btn_save.grid(row = 18, column = 1)
    btn_save.bind('<ButtonRelease-1>', save_img)

    # Bind all the required keys to functions
    root.bind("<q>", quit_img)
    root.bind("<s>", save_img)
    
    

    root.mainloop() # Start the GUI

if __name__ == "__main__":
    main()
