
import cv2 
import numpy as np
  
g_x = []
g_y = []
g_x2 = []
g_y2 = []
  
# read image 
img = cv2.imread('/Users/elizabeth/pic_test/cleo.jpg') 
  
#define the events for the mouse_click. 
def ref_click(event, x, y,  flags, param): 
    global g_x, g_y  
    
    if event == cv2.EVENT_LBUTTONDOWN or event == cv2.EVENT_RBUTTONDOWN:
        #cap at 4 for testing
        if len(g_x) < 4:
            g_x.append(x) 
            g_y.append(y)
        else:
            print("Selected 4 points, press r to reset")
        print(x,y)
        
def other_click(event, x, y, flags, param): 
    global g_x2, g_y2 
    
    if event == cv2.EVENT_LBUTTONDOWN or event == cv2.EVENT_RBUTTONDOWN:
        #cap at 4 for testing
        if len(g_x2) < 4:
            g_x2.append(x) 
            g_y2.append(y)
        else:
            print("Selected 4 points, press r to reset or h to continue")
        print(x,y)
          
cv2.imshow('image',img)  
cv2.imshow('wrongimage',img)       
cv2.setMouseCallback('image', ref_click) 
cv2.setMouseCallback('wrongimage', other_click) 


while(True):
    cv2.imshow('image',img)
    cv2.imshow('wrongimage',img)  
    k = cv2.waitKey(0)
    if k == ord('e'):
        print(g_x,g_y)
        print(g_x2,g_y2)
    elif k == ord("q"):
        break
    elif k == ord("r"):
        g_x = []
        g_y = []
        g_x2 = []
        g_y2 = []
    elif k == ord("a"):
        #Partially from https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_features_harris/py_features_harris.html
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        gray2 = np.float32(gray)
        dst = cv2.cornerHarris(gray2,2,3,0.04)

        res = img.copy()
        res[dst>0.01*dst.max()]=[0,0,255]
        kp1 = np.argwhere(dst > 0.01 * dst.max())
        kp1 = kp1.astype("float32")
        kp1 = [cv2.KeyPoint(x[1], x[0], 4) for x in kp1]
        
        sift = cv2.SIFT_create()
        dcp1 = sift.compute(gray, kp1)
        
        #img 2?
        
        
        cv2.imshow('dst',dst)
        

    elif k == ord("m"):
        pass
        
# close all the opened windows. 
cv2.destroyAllWindows() 
