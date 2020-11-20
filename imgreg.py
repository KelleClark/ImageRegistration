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

# keep the x and y coordinates of the points selected in both images
g_x = []
g_y = []
g_x2 = []
g_y2 = []

select_pnt1 = False
select_pnt2 = False

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
    global img1, image, imj1, updated_img1
    #Load the image
    image = opencv_img(path)
   
    #Convert and display
    disp_img = convert_img(image)
    imj1 = disp_img
    img1.image = disp_img
    updated_img1 = img1.create_image(0, 0, image=disp_img, anchor="nw")
    img1.config(height=image.shape[0], width=image.shape[1])
    img1.itemconfig(updated_img1)
    return disp_img

def update_img2(path):
    global img2, image2, img2_path, imj2, updated_img
    #Load the image
    img2_path = path
    image2 = opencv_img(path)
   
    #Convert and display
    disp_img = convert_img(image2)
    imj2 = disp_img
    img2.image = disp_img
    updated_img2 = img2.create_image(0, 0, image=disp_img, anchor="nw")
    img2.config(height=image2.shape[0], width=image2.shape[1])
    img2.itemconfig(updated_img2)
    return disp_img


# A newly transformed image, new, is formatted for display
def update_new(img):
    global new, new_img
    new_img = img
    disp_img = convert_img(img)
    
    #Convert and display
    new.image = disp_img
    updated_new = new.create_image(0, 0, image=disp_img, anchor="nw")
    new.config(height=new_img.shape[0], width=new_img.shape[1])
    new.itemconfig(updated_new)


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
    global image, g_x, g_y, img1, select_pnt1
    #Check that image 1 is loaded
    if not is_image():
        return

    if select_pnt1:
        print(select_pnt1)
        x1 = event.x
        y1 = event.y
        print("pic 1:",x1, y1)
        if len(g_x) < 4:
            g_x.append(x1)
            g_y.append(y1)
            img1.create_oval(x1-10, y1-10, x1+10, y1+10, outline="red", 
                             tags="point1")
        else:
            print("warning and don't save")
        

def select_points1(event):
    global select_pnt1
    print("Put a pop up box telling user what to do perhaps?")
    select_pnt1 = True

# point2
def setpoint2(event):
    global image, g_x2, g_y2, img2, select_pnt2
    #Check that image 1 is loaded
    if not is_image():
        return

    if select_pnt2:
        print(select_pnt2)
        x2 = event.x
        y2 = event.y
        print("pic 2:", x2, y2)
        if len(g_x2) < 4:
            g_x2.append(x2)
            g_y2.append(y2)
            img2.create_oval(x2-10, y2-10, x2+10, y2+10, outline="red",
                             tags="point2")
        else:
            print("warning and don't save")

def select_points2(event):
    global select_pnt2
    print("Put a pop up box telling user what to do perhaps?")
    select_pnt2 = True

# Reset the manual points that have been selected  
def reset(event):
    global g_x, g_y, g_x2, g_y2, img1, updated_img1
    g_x = []
    g_y = []
    g_x2 = []
    g_y2 = []
    img1.delete("point1")
    img2.delete("point2")
    
  
def print_points(event):
    global g_x, g_y, g_x2, g_y2
    print(g_x,g_y)
    print(g_x2,g_y2)

#Partially from 
#https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials
#/py_feature2d/py_features_harris/py_features_harris.html
def reg_automatic(event):
    global image1, imj1, new
    
    #Requires two images
    if not second_img:
        showinfo("Error", "Image Registration require two images.  Load 2 images and try again")
        return
    
    gray = cv2.cvtColor(image1,cv2.COLOR_BGR2GRAY)
    gray2 = np.float32(gray)
    dst = cv2.cornerHarris(gray2,2,3,0.04)

    res = imj1.copy()
    res[dst>0.01*dst.max()]=[0,0,255]
    kp1 = np.argwhere(dst > 0.01 * dst.max())
    kp1 = kp1.astype("float32")
    kp1 = [cv2.KeyPoint(x[1], x[0], 4) for x in kp1]
        
    sift = cv2.SIFT_create()
    dcp1 = sift.compute(gray, kp1)
        
    #img 2?
     
    #Convert and display
    disp_img = convert_img(dcp1)
    new.image = disp_img
    updated_new = new.create_image(0, 0, image=disp_img, anchor="nw")
    new.config(height=image2.shape[0], width=image2.shape[1])
    new.itemconfig(updated_new)
        
    
    
##---------------------------------------------------------------------------##
def main():
    global root, img1, img2, new, image, image2, new

    #Get the command arguments
    get_args()
    if len(sys.argv) != 1:
        print('Image Registration v1.0 is a GUI program without arguments')
        sys.exit(0)

    root = Tk()
    root.title("Image Registration.")
    
    #setting up a tkinter canvas
    img1 = Canvas(root, width=100, height=100)
    img1.create_image(0, 0, image=None, anchor="nw")
    img1.pack(side="left", padx=10, pady=10)
      
    img2 = Canvas(root, width=100, height=100)
    img2.create_image(0, 0, image=None, anchor="nw")
    img2.pack(side="left", padx=10, pady=10)
    
    new = Canvas(root, width=100, height=100)
    new.create_image(0, 0, image=None, anchor="nw")
    new.pack(side="right", padx=10, pady=10)
    
    
    #mouseclick event
    img1.bind("<Button 1>",setpoint1)
    img2.bind("<Button 1>",setpoint2)

    # Frame to display navigation buttons at bottom of window
    frame = Frame()
    frame.pack()

    # Button for select image 1
    btn_select_img1 = Button(
        master = frame,
        text = "Select image 1",
        underline = 13
    )
    btn_select_img1.grid(row = 0, column = 1)
    btn_select_img1.bind('<ButtonRelease-1>', select_img1)

     # Button for select image 2
    btn_select_img2 = Button(
        master=frame,
        text="Select image 2",
        underline=13
    )
    btn_select_img2.grid(row=14, column=1)
    btn_select_img2.bind('<ButtonRelease-1>', select_img2)

    # Button for select points on image 1
    btn_select_pts_img1 = Button(
        master = frame,
        text = "Select Points Image 1",
        underline = 13
    )
    btn_select_pts_img1.grid(row = 0, column = 2)
    btn_select_pts_img1.bind('<ButtonRelease-1>', select_points1)
  
    # Button for select points on image 2
    btn_select_pts_img2 = Button(
        master = frame,
        text = "Select Points Image 2",
        underline = 13
    )
    btn_select_pts_img2.grid(row = 14, column = 2)
    btn_select_pts_img2.bind('<ButtonRelease-1>',  select_points2 )
   
    # Button for save_img image
    btn_save = Button(
        master = frame,
        text = "Save",
        underline = 0
    )
    btn_save.grid(row = 18, column = 1)
    btn_save.bind('<ButtonRelease-1>', save_img)
    
    # Button for reset
    btn_save = Button(
        master = frame,
        text = "Reset Points",
        underline = 0
    )
    btn_save.grid(row = 15, column = 1)
    btn_save.bind('<ButtonRelease-1>', reset)
    
    # Button for print points
    btn_reg_auto = Button(
        master = frame,
        text = "Align Automatically",
        underline = 0
    )
    btn_reg_auto.grid(row = 15, column = 2)
    btn_reg_auto.bind('<ButtonRelease-1>', reg_automatic)

    # Bind all the required keys to functions
    root.bind("<q>", quit_img)
    root.bind("<s>", save_img)
    root.bind("<r>", reset)
    root.bind("<e>", print_points)
    root.bind("<a>", reg_automatic)

    
    

    root.mainloop() # Start the GUI

if __name__ == "__main__":
    main()
