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

# flag for determining if images are loaded
img = False
second_img = False
new_image = False

# flags to indicate state, collection of points
select_pnt1 = False
select_pnt2 = False

# reload image 2 in the event of a type mismatch
img2_path = ""

# to keep x and y coordinates of the points selected in images
g_x = []
g_y = []
g_x2 = []
g_y2 = []


##-------Launching the program-----------------------------------------------##
# For -h argument
def get_args():
    parser = argparse.ArgumentParser(description='Image Registration v1.0')
    parser.add_argument('-- ', default=" ",
                        help='A Graphical User Interface with no arguments.'+
                        '\nA target image and a source image are used in alignment.')
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
    scale = min(1, min(defaultrows / image.shape[0],
                       defaultcolumn / image.shape[1]))

    # Set triangle corners used for affine transformation to top left, top right,
    # and bottom left corners of image
    srcTri = np.array([[0, 0], [image.shape[1] - 1, 0],
                       [0, image.shape[0] - 1]]).astype(np.float32)

    # Set location of top right and bottom left corners of resized image
    dstTri = np.array( [[0, 0], [int(image.shape[1] * scale), 0],
                        [0, int(image.shape[0] * scale)]] ).astype(np.float32)

    # Perform affine transformation to resize image
    warp_mat = cv2.getAffineTransform(srcTri, dstTri)
    image = cv2.warpAffine(image, warp_mat, (image.shape[1], image.shape[0]))

    # Trim black border from resized image
    image = image[0:int(image.shape[0] * scale), 0:int(image.shape[1] * scale)]
    return(image)


# Convert image to ImageTK
# necessary to use cvtColor taking from BGR to expected RGB color
def convert_img(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # To proper format for tk
    im = Image.fromarray(image)
    imgtk = ImageTk.PhotoImage(image=im)
    return(imgtk)


##----------User Controls for the UI-----------------------------------------##

# Select the image to align
def select_img1(event):
    global img, second_img

    # Prompt user
    path = filedialog.askopenfilename(title="Please Select Image")

    # if there is a path and it is readable
    if len(path) > 0 and cv2.haveImageReader(path):
        update_img1(path)
        img = True
        print("Image to be aligned is :"+path)
    else:
        showinfo("Error", "No Image was found at path or it is not readable.")

# Select the image used to align
def select_img2(event):
    global second_img

    # Prompt the user
    path = filedialog.askopenfilename(title="Please Select Image 2")
    # if there is a path and it is readable
    if len(path) > 0 and cv2.haveImageReader(path):
        update_img2(path)
        second_img = True
        print("\nImage used in the alignment of Image 1"+path)
    else:
        showinfo("Error", "No image was found at path or it is not readable.")


# To exit the program
def quit_img(event):
    root.destroy() #Kill the display
    sys.exit(0)

# To save the image to the main given path appending the name of aligned
def save_img(event):
    global new, image_to_save

    #Check an image is loaded
    if not is_new():
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
    cv2.imwrite(name, image_to_save)


##---------GUI update image formating ---------------------------------------##
# User given path to image, open, format image return disp_img into img1 canvas

def update_img(disp_img, loc):
    loc.image = disp_img
    updated_img1 = loc.create_image(0, 0, image=disp_img, anchor="nw")
    loc.config(height=image.shape[0], width=image.shape[1])
    loc.itemconfig(updated_img1)

def update_img1(path):
    global img1, image, updated_img1

    # reset the points
    resetpts()

    #Load the image
    image = opencv_img(path)

    #Convert and display
    disp_img = convert_img(image)
    update_img(disp_img, img1)
    return disp_img

# The auto generated points on image 1 are displayed
def update_img1auto(img):
    global img1, image

    #Convert and display
    update_img(convert_img(img), img1)


# User given path to image, open, format image return disp_img into img2 canvas
def update_img2(path):
    global img2, image2, img2_path, updated_img

    # reset the points
    resetpts()

    #Load the image
    img2_path = path
    image2 = opencv_img(path)

    #Convert and display
    disp_img = convert_img(image2)
    update_img(disp_img, img2)
    return disp_img

# The auto generated points on image 2 are displayed
def update_img2auto(img):
    global img2, image

    #Convert and display
    update_img(convert_img(img), img2)

# A newly transformed image, new, is formatted for display
def update_new(img):
    global new, new_image, image2, image_to_save

    image_to_save = img


    #Convert and display
    update_img(convert_img(img), new)
    #set the flag
    new_image = True


# Check if images are loaded, required for registration
def are_images():
    global img, second_img

    #Check that images are loaded
    if not img:
        if not second_img:
            showinfo("Error", "Images have not been selected.")
            return False
        else:
            showinfo("Error", "Image 1 has not been selected.")
            return False
    elif not second_img:
        showinfo("Error", "Image 2 has not been selected.")
        return False
    else:
        return True

# Check if image 1 is loaded, required for select points image 1
def is_image():
    global img

    if not img:
        showinfo("Error", "Image 1 has not been selected.")
        return False
    return True

# Check if image 2 is loaded, required for select points image 2
def is_image2():
    global second_img

    if not img:
        showinfo("Error", "Image 2 has not been selected.")
        return False
    return True

# Check if there is a new image, required for save
def is_new():
    global new_image

    if not new_image:
        showinfo("Error", "There is no new image currently")
        return False
    return True

##---------Pixel Transformations---------------------------------------------##

# when select points image 1 button pressed, starts collecting points
# from mouse clicks on img1
def setpoint1(event):
    global image, g_x, g_y, img1, select_pnt1

    #Check that image 1 is loaded
    if not is_image():
        return


    if select_pnt1:
        x1 = event.x
        y1 = event.y
        if len(g_x) < 4:
            g_x.append(x1)
            g_y.append(y1)
            img1.create_oval(x1-5, y1-5, x1+5, y1+5, outline="red",
                             tags="point1")
        else:
            showinfo("Alert", "Four points have been set. Press Reset to begin again.")

# When button for select points image 1 is pressed, instructions given and
# flag set to receive mouse clicks on img1
def select_points1(event):
    global select_pnt1, image, img1

    if not is_image():
        return False
    else:
        update_img(convert_img(image), img1)
        showinfo("To Begin",
                 "Use mouse to click on 4 pts in Image 1 that you wish to use.")
        select_pnt1 = True

# when select points image 2 button pressed, starts collecting points
# from mouse clicks on img2
def setpoint2(event):
    global image, g_x2, g_y2, img2, select_pnt2

    #Check that image 2 is loaded
    if not is_image2():
        return

    if select_pnt2:
        x2 = event.x
        y2 = event.y
        if len(g_x2) < 4:
            g_x2.append(x2)
            g_y2.append(y2)
            img2.create_oval(x2-5, y2-5, x2+5, y2+5, outline="red",
                             tags="point2")
        else:
            showinfo("Alert", "Four points have been set. Press Reset to begin again.")

# When button for select points image 2 is pressed, instructions given and
# flag set to receive mouse clicks on img2
def select_points2(event):
    global select_pnt2, image2, img2

    if not is_image2():
        return False
    else:
        update_img(convert_img(image2), img2)
        showinfo("To Begin",
                 "Use mouse to click on 4 points in Image 2 that you wish to use.")
        select_pnt2 = True

# Reset the manual points that have been selected
def reset(event):
    resetpts()

# Reset the chosen points
def resetpts():
    global g_x, g_y, g_x2, g_y2, img1, img2, image, image2
    if len(g_x) > 1 or len(g_x2) > 1:
        g_x = []
        g_y = []
        g_x2 = []
        g_y2 = []
        img1.delete("point1")
        img2.delete("point2")
    if new_image:
        update_img(convert_img(image), img1)
        update_img(convert_img(image2), img2)

# Use harris corner detection to get keypoints
def get_corners(img):
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    gray2 = np.float32(gray)
    dst = cv2.cornerHarris(gray2,2,3,0.04)

    res = img.copy()
    res[dst>0.01*dst.max()]=[0,0,255]
    
    #identify key points
    kp = np.argwhere(dst > 0.01 * dst.max())
    kp = kp.astype("float32")
    kp = [cv2.KeyPoint(x[1], x[0], 4) for x in kp]
    return (gray, kp, res)

# Match the points across both images
def get_matches(decp1, decp2):
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
    matches = bf.match(decp1, decp2)
    matches.sort(key=lambda x: x.distance, reverse=False)
    return matches

# Print the current manually selected points
def print_points(event):
    global g_x, g_y, g_x2, g_y2
    print(list(zip(g_x,g_y)))
    print(list(zip(g_x2,g_y2)))

#Partially from
#https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials
#/py_feature2d/py_features_harris/py_features_harris.html
def reg_automatic(event):
    global image, imj1, new

    #Requires two images
    if not are_images():
        return

    # -- Image 1
    gray, kp1, res = get_corners(image)
    sift = cv2.SIFT_create()
    dcp1 = sift.compute(gray, kp1)[1]
    # -- Image 2
    gray2, kp2, res2 = get_corners(image2)
    dcp2 = sift.compute(gray2, kp2)[1]
    # -- Matching
    matches = get_matches(dcp1, dcp2)
    src_pts = np.int32([ kp1[m.queryIdx].pt for m in matches]).reshape(-1,1,2)
    dst_pts = np.int32([ kp2[m.trainIdx].pt for m in matches]).reshape(-1,1,2)

    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC)
    height, width, channels = image2.shape
    im1_reg = cv2.warpPerspective(image, M, (width, height))

    #Convert and display
    update_new(im1_reg)

    #Convert and display
    update_img1auto(res)
    update_img2auto(res2)



def reg_manual(event):
    global image, imj1, new, g_x, g_y, g_x2, g_y2

    #Requires two images
    if not are_images():
        return
    if len(g_x)<4:
        showinfo("Alert", "You need to select 4 points on Image 1")
        return
    if len(g_x2)< 4:
        showinfo("Alert", "You need to select 4 points on Image 2")

    srcQuad = np.float32([list(xy) for xy in zip(g_x, g_y)])
    dstQuad = np.float32([list(x2y2) for x2y2 in zip(g_x2, g_y2)])
    warp_mat = cv2.getPerspectiveTransform(srcQuad, dstQuad)
    res = cv2.warpPerspective(image, warp_mat, (image.shape[1], image.shape[0]))


    #Convert and display
    update_new(res)
    # disp_img = convert_img(res)
    # new.image = disp_img
    # updated_new = new.create_image(0, 0, image=disp_img, anchor="nw")
    # new.config(height=image2.shape[0], width=image2.shape[1])
    # new.itemconfig(updated_new)



##---------------------------------------------------------------------------##
def main():
    global root, img1, img2, new, image, image2, new

    #Get the command arguments
    get_args()
    if len(sys.argv) != 1:
        print('Image Registration v1.0 is a GUI program without arguments')
        sys.exit(0)

    root = Tk()
    root.title("Image Registration. You will need to load two Images. Img 1 is the target")

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
    btn_select_img2.grid(row=2, column=1)
    btn_select_img2.bind('<ButtonRelease-1>', select_img2)

    # Button for select points on image 1
    btn_select_pts_img1 = Button(
        master = frame,
        text = "Select Points Image 1"
    )
    btn_select_pts_img1.grid(row = 0, column = 2)
    btn_select_pts_img1.bind('<ButtonRelease-1>', select_points1)

    # Button for select points on image 2
    btn_select_pts_img2 = Button(
        master = frame,
        text = "Select Points Image 2"
    )
    btn_select_pts_img2.grid(row = 2, column = 2)
    btn_select_pts_img2.bind('<ButtonRelease-1>',  select_points2 )

    # Button for reset
    btn_save = Button(
        master = frame,
        text = "Reset Points",
        underline = 0
    )
    btn_save.grid(row = 3, column = 1)
    btn_save.bind('<ButtonRelease-1>', reset)

    # Button for Auto Align
    btn_reg_auto = Button(
        master = frame,
        text = "Align Automatically",
        underline = 0
    )
    btn_reg_auto.grid(row = 4, column = 2)
    btn_reg_auto.bind('<ButtonRelease-1>', reg_automatic)

    # Button for Manual Align
    btn_reg_man = Button(
        master = frame,
        text = "Align Manually"
    )
    btn_reg_man.grid(row = 4, column = 1)
    btn_reg_man.bind('<ButtonRelease-1>', reg_manual)

    # Button for save_img image
    btn_save = Button(
        master = frame,
        text = "Save",
        underline = 0
    )
    btn_save.grid(row = 6, column = 2)
    btn_save.bind('<ButtonRelease-1>', save_img)

    # Button for print points
    btn_printpts = Button(
        master = frame,
        text = "Print Pts",
        underline = 0
    )
    btn_printpts.grid(row = 5, column = 1)
    btn_printpts.bind('<ButtonRelease-1>', print_points)

    # Bind all the required keys to functions
    root.bind("<q>", quit_img)
    root.bind("<S>", save_img)
    root.bind("<s>", save_img)
    root.bind("<R>", reset)
    root.bind("<r>", reset)
    root.bind("<P>", print_points)
    root.bind("<p>", print_points)
    root.bind("<a>", reg_automatic)
    root.bind("<A>", reg_automatic)






    root.mainloop() # Start the GUI

if __name__ == "__main__":
    main()
