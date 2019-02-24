# -*- coding: utf-8 -*-
"""
Created on Sun Feb  25 1:19:10 2019

@author: Deepanjan Chakraborti
Working well with little error. 
Need to change parameters as per requirements.
"""

import numpy as np
import math
import cv2
import tkinter as tk
from tkinter import filedialog   

print("\n\nPlease select an lane video ...")
root = tk.Tk()
root.withdraw()
#reference_file_name = filedialog.askopenfilename()
file_name = filedialog.askopenfilename()
cap = cv2.VideoCapture(file_name)
# fgbg = cv2.createBackgroundSubtractorMOG2(history=5, varThreshold=150)
fgbg = cv2.bgsegm.createBackgroundSubtractorMOG(history=150, backgroundRatio=0.3)

def line1(x,y):
    return y - (29*x)/96.0 - 300

def line2(x,y):
    return y - (29*x)/96.0 - 500

crossedAbove = 0
crossedBelow = 0
points = set()
pointFromAbove = set()
pointFromBelow = set()
H = 1080
W = 1980
OffsetRefLines = 50  #Adjust ths value according to your usage


fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('test_output.avi',fourcc, 20.0, (W, H))
font = cv2.FONT_HERSHEY_SIMPLEX
while(1):
    pointInMiddle = set()
    prev = points
    points = set()
    ret, frame1 = cap.read()
    frame = cv2.resize(frame1,(W, H))
    height = np.size(frame,0)
    width = np.size(frame,1)
    #print(height)
    #print(width)
    fgmask = frame
    fgmask = cv2.blur(frame, (10,10))
    fgmask = fgbg.apply(fgmask)
    fgmask = cv2.medianBlur(fgmask, 7)
    oldFgmask = fgmask.copy()
    image, contours, hierarchy = cv2.findContours(fgmask, cv2.RETR_EXTERNAL,1)
    for contour in contours:
        if  2000 <= cv2.contourArea(contour) <= 200000:
            #QttyOfContours = QttyOfContours+1   
            x,y,w,h = cv2.boundingRect(contour)
            if 30<w<500 and 70<h<700:
                cv2.drawContours(frame, contour, -1, (0, 0, 255), 2)
                # cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2, lineType=cv2.LINE_AA)
                point = (int(x+w/2.0), int(y+h/2.0))
                points.add(point)
    for point in points:
        (xnew, ynew) = point
        # if line1(xnew, ynew) > 0 and line2(xnew, ynew) < 0:
        #     pointInMiddle.add(point)
        for prevPoint in prev:
            (xold, yold) = prevPoint
            dist = cv2.sqrt((xnew-xold)*(xnew-xold)+(ynew-yold)*(ynew-yold))
            if dist[0] <= 120:
                if line1(xnew, ynew) >= 0 and line2(xnew, ynew) <= 0:
                    if line1(xold, yold) < 0: # Point entered from line above
                        pointFromAbove.add(point)
                    elif line2(xold, yold) > 0: # Point entered from line below
                        pointFromBelow.add(point)
                    else:   # Point was inside the block
                        if prevPoint in pointFromBelow:
                            pointFromBelow.remove(prevPoint)
                            pointFromBelow.add(point)

                        elif prevPoint in pointFromAbove:
                            pointFromAbove.remove(prevPoint)
                            pointFromAbove.add(point)

                if line1(xnew, ynew) < 0 and prevPoint in pointFromBelow: # Point is above the line
                    print('One Crossed Above')
                    print(point)
                    crossedAbove += 1
                    pointFromBelow.remove(prevPoint)

                if line2(xnew, ynew) > 0 and prevPoint in pointFromAbove: # Point is below the line
                    print('One Crossed Below')
                    print(point)
                    crossedBelow += 1
                    pointFromAbove.remove(prevPoint)


    for point in points:
        if point in pointFromBelow:
            cv2.circle(frame, point, 3, (255,0,255),6)
        elif point in pointFromAbove:
            cv2.circle(frame, point, 3, (0,255,255),6)
        else:
            cv2.circle(frame, point, 3, (0,0,255),6)

    #plot reference lines (entrance and exit lines) 
    # CoorYEntranceLine = int((height / 2)-OffsetRefLines)
    # CoorYExitLine = int((height / 2)+OffsetRefLines)
    # #print(CoorYEntranceLine)
    # #print(CoorYExitLine)
    # cv2.line(frame, (0,CoorYEntranceLine), (width,CoorYEntranceLine), (255, 0, 0), 4)
    # cv2.line(frame, (0,CoorYExitLine), (width,CoorYExitLine), (0, 0, 255), 4)

    cv2.line(frame, (0,300), (width,height-200), (255, 0, 0), 4)
    cv2.line(frame, (0,500), (width,height), (255, 0, 0), 4)


    # cv2.line(frame, (0,300), (1920,880), (255, 0, 0), 4)
    # cv2.line(frame, (0,500), (1920,1080), (255, 0, 0), 4)
    cv2.putText(frame,'Above = '+str(crossedAbove),(100,50), font, 1,(0,0,0),2,cv2.LINE_AA)
    cv2.putText(frame,'Below = '+str(crossedBelow),(100,100), font, 1,(0,0,0),2,cv2.LINE_AA)
    cv2.putText(frame, "To be served = "+format(str(crossedAbove-crossedBelow)),(100,150),font, 1,(0,0,0),2,cv2.LINE_AA)
    cv2.imshow('a',oldFgmask)
    cv2.imshow('frame',frame)
    out.write(frame)
    l = cv2.waitKey(1) & 0xff
    if l == 27:
        break
cap.release()
cv2.destroyAllWindows()