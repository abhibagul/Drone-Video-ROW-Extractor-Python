import cv2
import numpy as np
import statistics
from tqdm import tqdm
import keyboard
import json
from requests import Session
from getpass import getpass
import hashlib
import string
import random
import re

print("===========================================================================")
print("                   Drone-Video-ROW-Extractor-Python                        ")
print("                         By: Abhishek Bagul                                ")
print("===========================================================================")
print("       https://github.com/abhibagul/Drone-Video-ROW-Extractor-Python       ")
print("===========================================================================")

#TODO : import SUBTITLE_LIBRARY


prevpoint_left = [[0,0,0,0]]
prevpoint_right = [[0,0,0,0]]

prevpoint_left2 = []
prevpoint_right2 = []

left_points_exp = []
right_points_exp = []
center_points_exp = []

width = 1920
height = 1080
MaxHLine = 30
MaxCFac = 30

lower = (160, 160, 160) # lower bound for each channel
upper = (255, 255, 255) # upper bound for each channel

last_rgoi = [
    (0, height/3),
        (0, height),
        (width, height),
        (width, height/3)]

in_rgoi = []

LRO = []
RRO = []

#No need to make it false
#toCarry = False
#hold_vid = False



def make_points(image, line):
    if np.isnan(line).any():
        return [[0,0,0,0],[0,0,0,0]]
    else:    
        slope, intercept = line
        y1 = int(image.shape[0])# bottom of the image
        y2 = int(y1*0.6)        # slightly lower than the middle
        x1 = int((y1 - intercept)/slope)
        x2 = int((y2 - intercept)/slope)
        return [[x1, y1, x2, y2]]


def average_slope_intercept(image, lines,prevpoint_right,prevpoint_left):
    left_fit    = []
    right_fit   = []
    no_fit = []
    yes_fit = []
    averaged_lines = []
    center_line = []
    text_c = []
    reSet_RGOI = False
    hold_vid = False
    if lines is None:
        return None
    for line in lines:
        for x1, y1, x2, y2 in line:
            fit = np.polyfit((x1,x2), (y1,y2), 1)
            slope = fit[0]
            intercept = fit[1]

            if intercept > 800 and slope < -0.5: # y is reversed in image
                left_fit.append((slope, intercept))
                yes_fit.append([line,intercept])
            elif intercept < -800 :
                right_fit.append((slope, intercept))                
                yes_fit.append([line,intercept])
            else:
                #draw low level lines
                no_fit.append([line,intercept])
                #no_lines = draw_no_lines(image,[lowpoint])
                #cv2.imshow("noline", no_lines)
                #print(lowpoint)
    # add more weight to longer lines
    left_fit_average  = np.average(left_fit, axis=0)
    right_fit_average = np.average(right_fit, axis=0)

    if left_fit_average is not None:
        left_line  = make_points(image, left_fit_average)

    if right_fit_average is not None:    
        right_line = make_points(image, right_fit_average)

    if len(left_line) > 1:
        left_line = prevpoint_left
        text_c.append("Left Carry")
        reSet_RGOI = True
    else:
        prevpoint_left = left_line
        text_c.append("Left Detected")  

    if len(right_line) > 1:
        right_line = prevpoint_right
        text_c.append("Right Carry")
        reSet_RGOI = True
    else :
        text_c.append("Right Detected")
        prevpoint_right = right_line    

    if np.isnan(left_fit_average).any():
        text_c.append([-99])
    else:
        text_c.append([left_fit_average[0]])

    if np.isnan(right_fit_average).any():  
        text_c.append([99])
    else:        
        text_c.append([right_fit_average[0]])

    if np.isnan(left_fit_average).any():
        text_c.append([-99])
    else:
        text_c.append([left_fit_average[1]])

    if np.isnan(right_fit_average).any():  
        text_c.append([99])
    else:        
        text_c.append([right_fit_average[1]])

    if len(left_line) < 2 and len(right_line) < 2:
        cx1 = int((left_line[0][0] + right_line[0][0]) / 2)
        cy1 = int((left_line[0][1] + right_line[0][1]) / 2)
        cx2 = int((left_line[0][2] + right_line[0][2]) / 2)
        cy2 = int((left_line[0][3] + right_line[0][3]) / 2)

        center_line.append(cx1)
        center_line.append(cy1)
        center_line.append(cx2)
        center_line.append(cy2)
    else:
        center_line.append(0)
        center_line.append(0)
        center_line.append(0)
        center_line.append(0)

    averaged_lines = [left_line, right_line]
    return averaged_lines, no_fit, yes_fit, [[center_line]],prevpoint_right,prevpoint_left,text_c, reSet_RGOI

def canny(img,MaxCFac):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernel = 5
    blur2 = cv2.blur(thresh, (1, 1)) # blur the image
    canny = cv2.Canny(gray, MaxCFac, MaxCFac)
    return canny

def display_lines(img,lines):
    allpoints = []
    newimgc = img.copy()
    line_image = np.zeros_like(img)
    if lines is not None:
        allpoints = []
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image,(x1,y1),(x2,y2),(255,0,0),5)
                allpoints.append([np.uint32(x1),np.uint32(y1)])
                allpoints.append([np.uint32(x2),np.uint32(y2)])

    pts = np.array(allpoints,np.int32)
    blank_image = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)

    blank_image = cv2.polylines(blank_image,[pts], isClosed = True, color = (255, 0, 0), thickness = 3)
    gray = cv2.cvtColor(blank_image, cv2.COLOR_BGR2GRAY)
    contours, hierarchy = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    hull = []
    for i in range(len(contours)):
        # creating convex hull object for each contour
        hull.append(cv2.convexHull(contours[i], False))

    # create an empty black image
    drawing = np.zeros((img.shape[0], img.shape[1], 3), np.uint8)

    # draw contours and hull points
    for i in range(len(contours)):
        color_contours = (0, 0, 0) # green - color for contours
        color = (0, 255, 255) # blue - color for convex hull
        # draw ith contour
        #cv2.drawContours(drawing, contours, i, color_contours, 1, 8, hierarchy)
        # draw ith convex hull object
        cv2.drawContours(drawing, hull, i, color, -1, 1)

    #print([hull2][0][0])

    return drawing, newimgc

def region_of_interest(canny, rgoi):
    height = canny.shape[0]
    width = canny.shape[1]
    mask = np.zeros_like(canny)

    triangle = np.array([rgoi], np.int32)

    cv2.fillPoly(mask, triangle, 255)
    masked_image = cv2.bitwise_and(canny, mask)
    return masked_image

def region_box_of_interest(canny,rgoi):
    canny2 = canny.copy()
    height = canny.shape[0]
    width = canny.shape[1]
    mask = np.zeros_like(canny)

    triangle = np.array([rgoi], np.int32)
    # Bad idea to invert the mask!
    #mask = 255 - mask
    cv2.fillPoly(mask, triangle, 255)
    mask = cv2.bitwise_not(mask)
    mask2 = mask.copy()
    masked_image_inv = cv2.bitwise_and(canny2, mask2)
    return masked_image_inv

def NewRGOIM(image,NewRGOI,factorReg,factorHeg):
    new_rgoi = []
    inside_rgoi = []
    LROM = []
    RROM = []
    #Format of NewRGOI
    #averaged_lines = [left_line, right_line]
    #print(NewRGOI,NewRGOI[1][0][0],'ERGOI')
    if NewRGOI is not None:
        if len(NewRGOI ) > 1:
            nx1 = NewRGOI[0][0][0] - factorReg
            ny1 = NewRGOI[0][0][1] #+ (NewRGOI[0][0][1] * (factorReg/100))
            nx2 = NewRGOI[0][0][2] - factorReg
            ny2 = NewRGOI[0][0][3] #- (NewRGOI[0][0][3] * (factorReg/100))
            nx4 = NewRGOI[1][0][0] + factorReg
            ny4 = NewRGOI[1][0][1] #+ (NewRGOI[1][0][1] * (factorReg/100))
            nx3 = NewRGOI[1][0][2] + factorReg
            ny3 = NewRGOI[1][0][3] #- (NewRGOI[1][0][3] * (factorReg/100))
            new_rgoi.append((nx1,ny1))
            new_rgoi.append((nx2,ny2))
            new_rgoi.append((nx3,ny3))
            new_rgoi.append((nx4,ny4))

            ix1 = NewRGOI[0][0][0] + factorHeg
            iy1 = NewRGOI[0][0][1] #+ (NewRGOI[0][0][1] * (factorHeg/100))
            ix2 = NewRGOI[0][0][2] + factorHeg
            iy2 = NewRGOI[0][0][3] #- (NewRGOI[0][0][3] * (factorHeg/100))
            ix4 = NewRGOI[1][0][0] - factorHeg
            iy4 = NewRGOI[1][0][1] #+ (NewRGOI[1][0][1] * (factorHeg/100))
            ix3 = NewRGOI[1][0][2] - factorHeg
            iy3 = NewRGOI[1][0][3] #- (NewRGOI[1][0][3] * (factorHeg/100))
            inside_rgoi.append((ix1,iy1))
            inside_rgoi.append((ix2,iy2))
            inside_rgoi.append((ix3,iy3))
            inside_rgoi.append((ix4,iy4))

            #inpoints LRO
            LROM.append((nx1,ny1))
            LROM.append((nx2,ny2))
            LROM.append((ix2,iy2))
            LROM.append((ix1,iy1))

            #inpoints RRO
            RROM.append((nx3,ny3))
            RROM.append((nx4,ny4))
            RROM.append((ix4,iy4))
            RROM.append((ix3,iy3))

    return new_rgoi,inside_rgoi, RROM, LROM

def draw_no_lines(img,lines):
    line_image = np.zeros_like(img)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image,(x1,y1),(x2,y2),(255,0,0),10)
    return line_image

def display_lines_final(img,lines):
    line_image = np.zeros_like(img)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image,(x1,y1),(x2,y2),(255,255,255),5)
    return line_image

def display_lines_notinc(img,lines):
    line_image = np.zeros_like(img)
    if lines is not None:
        for line in lines:
            #print(line[1],'l')
            for x1, y1, x2, y2 in line[0]:
                cv2.line(line_image,(x1,y1),(x2,y2),(0,0,255),3)
                cv2.putText(line_image,str(round(line[1], 2)), (x1,y1), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255),thickness = 1)
    return line_image

def display_lines_yesinc(img,lines):
    line_image = np.zeros_like(img)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line[0]:
                cv2.line(line_image,(x1,y1),(x2,y2),(0,255,0),3)                
                cv2.putText(line_image,str(round(line[1], 2)), (x1,y1), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),thickness = 1)
    return line_image

def display_lines_center(img,lines):
    line_image = np.zeros_like(img)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image,(x1,y1),(x2,y2),(0,255,255),5)
    return line_image

def region_of_interest_new(canny):
    height = canny.shape[0]
    width = canny.shape[1]
    mask = np.zeros_like(canny)

    triangle = np.array([[
    (0, height/3),
        (0, height),
        (width, height),
        (width, height/3)]], np.int32)

    cv2.fillPoly(mask, triangle, 255)
    masked_image = cv2.bitwise_and(canny, mask)
    return masked_image

def slope_intercept(x1,y1,x2,y2):

    if (x2-x1) < 0.5 and (x2-x1) > -0.5 :
        a = 0
        b = x1
        dnc = True
    else:
        a = (y2 - y1) / (x2 - x1)
        b = y1 - a * x1
        dnc = True     

    #if b > 1920:
    #    a = 0
    #    b = x1

    return [dnc,a,b]

def make_points_new(image, line):
    #print('line',line)
    if np.isnan(line).any():
        #print("isNan",line)
        return []
    else:    
        slope, intercept = line
        y1 = int(image.shape[0]) # bottom of the image
        y2 = int(y1*0.6) 

        if slope == 0:
            x1 = intercept
            x2 = intercept
        else:
            x1 = int((y1 - intercept)/slope)
            x2 = int((y2 - intercept)/slope)

        x1 = int(x1)
        y1 = int(y1)
        x2 = int(x2)
        y2 = int(y2)
        return [[x1, y1, x2, y2]]

def avgline_intercept(image, lines):
    all_line    = []
    slopes = []
    intercepts = []
    zeroslopes = []
    zerointercepts = []
    if lines is None:
        return None
    for line in lines:
        for x1, y1, x2, y2 in line:

            if (x2-x1) == 0:
                zerointercepts.append(x1)
                continue

            fit = np.polyfit((x1,x2), (y1,y2), 1)
            #fit = slope_intercept(x1,y1,x2,y2)
            #if fit[0]:
            slope = fit[0]
            intercept = fit[1]
            all_line.append((slope, intercept))
            slopes.append(slope)
            intercepts.append(intercept)

    # add more weight to longer lines

    if len(slopes) < 1:
        slopes.append(0)

    if len(intercepts) < 1:
        intercepts = zerointercepts 

    if len(zerointercepts) > len(intercepts):
        intercepts = zerointercepts
        zeroslopes.append(0)
        slopes = zeroslopes
    
    #print(slopes,intercepts,'si')

    all_fit_average = [statistics.mean(slopes),statistics.mean(intercepts)]
    all_line_pt  = make_points_new(image, all_fit_average)

    return all_line_pt, all_fit_average

def smart_line_detect(LROI,RROI,prevpoint_left2,prevpoint_right2):
    lines = []
    dct = []
    isNone = False
    left_lines = cv2.HoughLinesP(LROI, 2, np.pi/180, 50, np.array([]), minLineLength=50,maxLineGap=5)
    right_lines = cv2.HoughLinesP(RROI, 2, np.pi/180, 50, np.array([]), minLineLength=50,maxLineGap=5)

    #RM: DEBUG
    #print("L1",left_lines,'<< left \n',right_lines,'<< Right \n',prevpoint_left2,'<< prevpoint_left2 \n',prevpoint_right2,'<< prevpoint_right2 \n============================\n')

    if left_lines is None:
        left_lines = prevpoint_left2
        dct.append("Carry")        
        isNone = True
    else:
        prevpoint_left2 = left_lines
        dct.append("Detected")
        isNone = False

    if right_lines is None:
        right_lines = prevpoint_right2
        dct.append("Carry")
        isNone = True
    else:
        prevpoint_right2 = right_lines
        dct.append("Detected")
        isNone = False  

    #RM: DEBUG
    #print(dct,'<< dct \n', left_lines, '<< Left \n', right_lines,'<< Right \n')
    #print("L2",left_lines,'<< left \n',right_lines,'<< Right \n',prevpoint_left2,'<< prevpoint_left2 \n',prevpoint_right2,'<< prevpoint_right2 \n============================\n')
    #print(left_lines,'<< left \n',right_lines,'<< Right \n')
    left_pt,leftsdi = avgline_intercept(LROI, left_lines)
    right_pt,rightsdi = avgline_intercept(LROI, right_lines)


    left_pt1 = left_pt
    right_pt1 = right_pt

    if(left_pt[0][0] < right_pt[0][0]):
        left_pt = left_pt1
        right_pt = right_pt1
    else:
        right_pt = left_pt1
        left_pt = right_pt1
    #RM: DEBUG
    #print(left_lines, right_lines, left_pt,right_pt,prevpoint_left,prevpoint_right,'lpt')

    cx1 = (left_pt[0][0] + right_pt[0][0])/2
    cy1 =(left_pt[0][1] + right_pt[0][1])/2
    cx2 = (left_pt[0][2] + right_pt[0][2])/2
    cy2 =(left_pt[0][3] + right_pt[0][3])/2

    inpoint_c = []
    inpoint_c.append(int(cx1))
    inpoint_c.append(int(cy1))
    inpoint_c.append(int(cx2))
    inpoint_c.append(int(cy2))

    

    lines.append(left_pt)
    lines.append(right_pt)
    #print(lines,'pt')

    return lines, [[inpoint_c]],prevpoint_left2,prevpoint_right2,dct,leftsdi,rightsdi,left_lines,right_lines, isNone

# image = cv2.imread('test_image.jpg')
# lane_image = np.copy(image)
# lane_canny = canny(lane_image)
# cropped_canny = region_of_interest(lane_canny)
# lines = cv2.HoughLinesP(cropped_canny, 2, np.pi/180, 100, np.array([]), minLineLength=40,maxLineGap=5)
# averaged_lines = average_slope_intercept(image, lines)
# line_image = display_lines(lane_image, averaged_lines)
# combo_image = cv2.addWeighted(lane_image, 0.8, line_image, 1, 0)

def draw_on_frame(img,lines):
    line_image = img.copy()
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                line_image = cv2.line(line_image,(x1,y1),(x2,y2),(0,255,255),5)
    return line_image

def draw_on_frame_c(img,lines):
    line_image = img.copy()
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                line_image = cv2.line(line_image,(x1,y1),(x2,y2),(255,255,255),5)
    return line_image

def region_of_interest_det(canny_image_det, new_m_region):
    height = canny_image_det.shape[0]
    width = canny_image_det.shape[1]
    mask = np.zeros_like(canny)

    triangle = np.array([new_m_region], np.int32)

    cv2.fillPoly(mask, triangle, 255)
    masked_image = cv2.bitwise_and(canny_image_det, mask)
    return masked_image

def display_lines_notinc_or(img,lines):
    line_image = img.copy()

    #print('lines',lines)
    if lines is not None:
        for line in lines:
            #print(line[1],'l')
            for x1, y1, x2, y2 in line:
                line_image = cv2.line(line_image,(x1,y1),(x2,y2),(0,0,255),3)
                #cv2.putText(line_image,str(round(line[1], 2)), (x1,y1), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255),thickness = 1)
    return line_image

def display_lines_yesinc_or(img,lines):
    line_image = img.copy()

    #print('lines',lines)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                line_image = cv2.line(line_image,(x1,y1),(x2,y2),(0,255,0),3)                
                #cv2.putText(line_image,str(round(line[1], 2)), (x1,y1), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),thickness = 1)
    return line_image

def mouseClick(events, x, y, flags, params):
    if events == cv2.EVENT_LBUTTONDOWN:
        LRO.append([x,y])
    #    for i2, pos2 in enumerate(RList):
    #        RList.append(pos2)
        
    if events == cv2.EVENT_RBUTTONDOWN:
        RRO.append([x,y])
        #for i, pos in enumerate(posList):
        #    posList.append(pos)
        #posList = []


vid_file_path = input("Enter video file path: ")
# TODO : Add srt support for lat long text & map
# fpt = input("Enter SRT file path: ")
json_file_path = input("Enter Json output file path: ")
cap = cv2.VideoCapture(vid_file_path)

i=0

_, frame = cap.read()

width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH ))  # float `width`
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # float `height`

print(width,height)

size = (width, height)
fourcc = cv2.VideoWriter_fourcc(*'XVID')

fps = cap.get(cv2.CAP_PROP_FPS)


#out = cv2.VideoWriter('D:\\lines\\r\\output_master.avi', fourcc, fps, size)

#out2 = cv2.VideoWriter('D:\\lines\\r\\output_raw.avi', fourcc, fps, size)

#out3 = cv2.VideoWriter('D:\\PROW\\Git\\outputROW.avi', fourcc, fps, size)

total_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

#get frame 0


#reset frame to 0
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

def ParseTimeSec(st):
    #get to sec
    st = re.findall("[:0-9]{1,}", st)
    st = re.findall("[0-9]{1,}", st[0])

    # st [0 => hr, 1 => min, 2=> sec]

    timeS = (int(st[0]) * 60 * 60) + (int(st[1]) * 60) + int(st[2]) 
    return timeS

# TODO : SRT READING
def sort_srt(lines):
    maxL = len(lines) / 6
    #print('maxL' , maxL)
    stri = 0

    frameWise = []
    while stri < maxL:
        lri = stri * 6
        t = lines[lri+1]
        d = lines[lri+2]

        print(lines[lri])
        #Regex
        t = re.findall("[:0-9,]{1,}", t)
        d = re.findall("\S{1,}", d)

        d[0] = re.findall("[0-9.]{1,}",d[0])

        subSt = ParseTimeSec(t[0])
        subEt = ParseTimeSec(t[1])

        startFrame = subSt * fps
        endFrame = subEt * fps

        frameBetween = endFrame - startFrame 
        inb = 1
        while inb <= frameBetween:
            frameWise.append(d)
            inb += 1


        # structure
        # d => [['75.3213', '19.8288'], '2021.12.16', '12:04:22']
        # t => ['00:06:39,000', '00:06:40,000']
        #print(d,t,subSt,subEt, frameBetween)
        stri += 1
    return frameWise

def getLines(file_path):
    with open(file_path) as file_in:
        #print(file_in)
        lines = []
        for line in file_in:
            lines.append(line)

    return sort_srt(lines)



#SRTD = getLines(fpt)

imgy = frame.copy()

#try asking for LRO and RRO
cv2.imshow("Select both lines", imgy)
#cv2.setWindowProperty("Select both lines", cv2.WND_PROP_TOPMOST, 1)
while cv2.getWindowProperty('Select both lines', 0) >= 0:

    imgy = frame.copy()


    inpl = []
    inrl = []
    for pos in LRO:
        inpl.append(pos)
        cv2.circle(imgy, pos, radius=5, color=(0, 0, 255), thickness=-1)

    for pos in RRO:
        inrl.append(pos)
        cv2.circle(imgy, pos, radius=5, color=(255, 0, 0), thickness=-1)

    if len(LRO) > 1:
        #print(inpl,'inpl')
        inpl = np.array(inpl,np.int32)
        imgy = cv2.polylines(imgy, [inpl],isClosed=True, color=(0, 0, 255))

    if len(RRO) > 1:
        inrl = np.array(inrl,np.int32)
        imgy = cv2.polylines(imgy, [inrl],isClosed=True, color=(255, 0, 0))
 
    cv2.imshow("Select both lines", imgy)
    cv2.setMouseCallback("Select both lines", mouseClick)

    if keyboard.is_pressed('r'):
        RRO = []
        LRO = []
        inpl = []
        inrl = []
        print('inside r')

    if cv2.getWindowProperty("Select both lines", cv2.WND_PROP_VISIBLE) <1:
        break

    if len(LRO) > 3 and len(RRO) > 3:
        break

    if cv2.waitKey(1) & 0xFF == ord('w'):
        MaxHLine = 10
        MaxCFac = 10

        break

with tqdm(total=total_frame,unit='frames',colour='#00ff00') as pbar:
    while(cap.isOpened()):



        ccd = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

        if total_frame < (ccd + 1):
            break

        # if len(SRTD) < ccd:
        #     CSRT = SRTD[ccd]
        # else:
        #     sLN = len(SRTD)
        #     CSRT = SRTD[sLN]    

        _, frame = cap.read()

        #print('\nAUD',LRO, RRO, cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if cv2.waitKey(1) & 0xFF == ord('u'):

            #print('\nBUD',LRO,RRO, cap.get(cv2.CAP_PROP_FRAME_COUNT))

            #print('Request update')
            LRO = []
            RRO = []
            imgu = frame.copy()

            #try asking for LRO and RRO

            cv2.destroyAllWindows()
            cv2.imshow("Select both line", imgu)
            #cv2.setWindowProperty("Select both line", cv2.WND_PROP_TOPMOST, 1)
            while cv2.getWindowProperty('Select both line', 0) >= 0:

                imgu = frame.copy()

                inpl = []
                inrl = []
                for pos in LRO:
                    inpl.append(pos)
                    cv2.circle(imgu, pos, radius=5, color=(0, 0, 255), thickness=-1)

                for pos in RRO:
                    inrl.append(pos)
                    cv2.circle(imgu, pos, radius=5, color=(255, 0, 0), thickness=-1)

                if len(LRO) > 1:
                    #print(inpl,'inpl')
                    inpl = np.array(inpl,np.int32)
                    imgu = cv2.polylines(imgu, [inpl],isClosed=True, color=(0, 0, 255))

                if len(RRO) > 1:
                    inrl = np.array(inrl,np.int32)
                    imgu = cv2.polylines(imgu, [inrl],isClosed=True, color=(255, 0, 0))

                cv2.imshow("Select both line", imgu)
                cv2.setMouseCallback("Select both line", mouseClick)

                if cv2.getWindowProperty("Select both line", cv2.WND_PROP_VISIBLE) <1:
                    break

                if keyboard.is_pressed('r'):
                    RRO = []
                    LRO = []
                    inpl = []
                    inrl = []
                    print('i i r')


                if len(LRO) > 3 and len(RRO) > 3:
                    break

                if cv2.waitKey(1) & 0xFF == ord('w'):
                    MaxHLine = 20
                    MaxCFac = 20

                    break

            #print('\nAUD',LRO,RRO, cap.get(cv2.CAP_PROP_FRAME_COUNT))

        

        #print('\nOUD',LRO,RRO, cap.get(cv2.CAP_PROP_FRAME_COUNT))

        #print('\n===========================\n\n')
        pbar.update(1)

        #lower = (130, 130, 130) # lower bound for each channel
        #upper = (255, 255, 255) # upper bound for each channel

        image = frame.copy()
        imageee = frame.copy()

        #cropped_prl2 = frame.copy()
        canny_new_image = cv2.Canny(frame,MaxCFac,MaxCFac,apertureSize = 3)

        blur7 = cv2.GaussianBlur(image,(3,3),0) # blur the image

        # create the mask and use it to change the colors
        mask = cv2.inRange(blur7, lower, upper)
        image[mask == 0] = [0,0,0]
        image[mask != 0] = [255,255,255]
        image2 = image.copy()

        image3 = cv2.GaussianBlur(image2,(1,1),0)

        #image[mask != 0] = [255,255,255]
        canny_image = cv2.Canny(image3,MaxCFac,MaxCFac,apertureSize = 3)
        #canny_image = canny(image)
        cropped_canny = region_of_interest(canny_image,last_rgoi)
        cropped_prl = region_of_interest(image,last_rgoi)
        cropped_canny2 = cropped_canny
        cropped_prl2 = cropped_prl

        LROI = cropped_prl.copy()
        RROI = cropped_prl.copy()

        if len(LRO) > 1:
            LROI = region_of_interest(canny_image, LRO)        
            PLROI = region_of_interest(image, LRO)
        if len(RRO) > 1:
            RROI = region_of_interest(canny_image, RRO)
            PRROI = region_of_interest(image, RRO)

        if len(LRO) > 1 and len(RRO) > 1:

            MaxHLine = 10
            MaxCFac = 10

            #print(RRO, LRO, 'Regions')
            #cv2.imwrite('D:\\lines\\r\\LROI-'+str(i)+'.jpg',LROI)
            #cv2.imwrite('D:\\lines\\r\\RROI-'+str(i)+'.jpg',RROI)  

            Best_Lines,center_line, prevpoint_left2, prevpoint_right2, dct,leftsdi,rightsdi,left_lines,right_lines,isNone = smart_line_detect(LROI,RROI,prevpoint_left2,prevpoint_right2)
            #print(Best_Lines,'BL')
            #if isNone:
            #    cv2.waitKey(5000)
                #break
            #if dct[0] == "Carry" or dct[1] == "Carry":


            left_points_exp.append(Best_Lines[0])
            right_points_exp.append(Best_Lines[1])
            center_points_exp.append(center_line)         
                

            line_image_final = draw_on_frame(frame, Best_Lines)
            line_image_final = draw_on_frame_c(line_image_final, center_line)
            no_line_image = display_lines_notinc_or(line_image_final, left_lines)
            yes_line_image = display_lines_yesinc_or(no_line_image, right_lines)
            cv2.putText(line_image_final,"Slope : "+ str(leftsdi[0]) + " / " + str(rightsdi[0]), (50,50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),thickness = 1)
            cv2.putText(line_image_final,"Intercept:" + str(leftsdi[1]) + " / " + str(rightsdi[1]), (50,100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),thickness = 1)
            cv2.putText(line_image_final,str(dct[0]) + " / " + str(dct[1]), (50,150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),thickness = 1)
            # cv2.putText(line_image_final,"LatLong" + str(CSRT[0][0]) + " / " + str(CSRT[0][1]), (50,200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),thickness = 1)
            new_rgoi,inside_rgoi,LRO,RRO = NewRGOIM(frame, Best_Lines,15,15)
            both_roi = cv2.addWeighted(LROI, 1, RROI, 1, 1)
            #im22 = cv2.resize(line_image_final, (750, 0), fx = 0.3, fy = 0.3)
            #im222 = cv2.resize(yes_line_image, (750, 0), fx = 0.3, fy = 0.3)
            #both_roi = cv2.addWeighted(im22, 1, both_roi, 1, 1)
            #cv2.imshow("LROI", both_roi)
            #cv2.imshow("RROI", image)
            #print("Adding frame")
            #out3.write(yes_line_image)
            cv2.imshow("Output", line_image_final)
            #out.write(line_image_final)
            #out2.write(both_roi)
            #out3.write(image)


            #cv2.imwrite('D:\\lines\\r\\oldPLROI.jpg',PLROI)
            #cv2.imwrite('D:\\lines\\r\\oldPRROI.jpg',PRROI) 

            #if dct[0] == "Carry" or dct[1] == "Carry":            
            #    cv2.imwrite('D:\\lines\\r\\newLROI.jpg',LROI)
            #    cv2.imwrite('D:\\lines\\r\\newRROI.jpg',RROI) 
            #    cv2.imwrite('D:\\lines\\r\\newPLROI.jpg',PLROI)
            #    cv2.imwrite('D:\\lines\\r\\newPRROI.jpg',PRROI) 
            #    cv2.imwrite('D:\\lines\\r\\frame.jpg',frame)
            #    cv2.imwrite('D:\\lines\\r\\line_image_final.jpg',line_image_final)
            #    cv2.imwrite('D:\\lines\\r\\no_line_image.jpg',no_line_image)
            #    cv2.imwrite('D:\\lines\\r\\yes_line_image.jpg',yes_line_image)
            #    i+=1
                #break;


            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            continue

        #else:
        if len(in_rgoi) > 1:
            cropped_prl2 = region_box_of_interest(cropped_prl, in_rgoi)
            cropped_canny2 = region_box_of_interest(cropped_canny, in_rgoi)
            lines = cv2.HoughLinesP(cropped_canny2, 2, np.pi/180, 100, np.array([]), minLineLength=MaxHLine,maxLineGap=1)
        else:
            lines = cv2.HoughLinesP(cropped_canny, 2, np.pi/180, 100, np.array([]), minLineLength=MaxHLine,maxLineGap=1)
        

        #averaged_lines = average_slope_intercept(image, lines)
        line_image, newimgc = display_lines(cropped_canny2, lines)

        canny_image1 = canny(line_image,MaxCFac)    
        cropped_canny = region_of_interest_new(canny_image1)    
        lines = cv2.HoughLinesP(canny_image1, 2, np.pi/180, 100, np.array([]), minLineLength=MaxHLine,maxLineGap=1)
        averaged_lines, no_lines, yes_lines, center_line_p, prevpoint_right, prevpoint_left,pcd, reSet_RGOI = average_slope_intercept(image, lines,prevpoint_right,prevpoint_left)
        new_rgoi,inside_rgoi,LRO,RRO = NewRGOIM(image, averaged_lines,10,10)
        #print(last_rgoi,new_rgoi,'rgoi')

        #newRGOIIMG = cv2.polylines(frame,[new_rgoi], isClosed = True, color = (255, 0, 0), thickness = 2)
        if len(new_rgoi) > 1:
            last_rgoi = new_rgoi


        if len(new_rgoi) > 1:
            in_rgoi = inside_rgoi

        if reSet_RGOI:
            
            last_rgoi = [(0, height/3),
                    (0, height),
                    (width, height),
                    (width, height/3)]
            in_rgoi = []

        line_image_final = display_lines_final(image, averaged_lines)
        no_line_image = display_lines_notinc(image, no_lines)
        yes_line_image = display_lines_yesinc(image, yes_lines)

        center_line_image = display_lines_center(image, center_line_p)



        #combo_image = cv2.addWeighted(frame, 0.8, line_image, 0.1, 1)
        combo_image = cv2.addWeighted(frame, 0.8, line_image_final, 1, 1)
        combo_image2 = cv2.addWeighted(frame, 0.8, no_line_image, 1, 1)
        combo_image2 = cv2.addWeighted(combo_image2, 0.8, yes_line_image, 1, 1)

        combo_image = cv2.addWeighted(combo_image, 0.8, center_line_image, 1, 1)

        cv2.putText(combo_image2,str(pcd[0]) + " / " + str(pcd[1]), (50,50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),thickness = 1)
        if len(pcd) > 2:
            cv2.putText(combo_image2,str(round(pcd[2][0],3)) + " / " + str(round(pcd[3][0],3)), (50,100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),thickness = 1)
        if len(pcd) > 4:
            cv2.putText(combo_image2,str(round(pcd[4][0],3)) + " / " + str(round(pcd[5][0],3)), (50,150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),thickness = 1)
        hlci = cv2.resize(combo_image, (30, 0), fx = 0.4, fy = 0.4)
        lci = cv2.resize(line_image, (750, 0), fx = 0.3, fy = 0.3)
        #lcim = cv2.resize(canny_image1, (750, 0), fx = 0.3, fy = 0.3)

        MaxHLine = 10
        MaxCFac = 10
        
        if reSet_RGOI:
            MaxHLine = 50
            MaxCFac = 50
            lower = (210, 210, 210) # lower bound for each channel
            upper = (255, 255, 255) # upper bound for each channel
            LRO = []
            RRO = []
        else:
            lower = (140, 140, 140) # lower bound for each channel
            upper = (255, 255, 255) # upper bound for each channel

        #if len(in_rgoi) > 1:
            #ca1 = cv2.resize(cropped_canny2, (750, 0), fx = 0.3, fy = 0.3)
            #cv2.imshow("Canny", cropped_prl2)    

        ca2 = cv2.resize(cropped_prl, (750, 0), fx = 0.3, fy = 0.3)
        im22 = cv2.resize(RROI, (750, 0), fx = 0.3, fy = 0.3)
        im222 = cv2.resize(LROI, (750, 0), fx = 0.3, fy = 0.3)
        #cv2.imshow("Combo", hlci)
        #cv2.imshow("Shape", newimgc)    
        #cv2.imshow("LROI", im222)    
        #cv2.imshow("Canny 1", combo_image2)  
        #cv2.imshow("RROI", im22)
        #out.write(combo_image)
        #out3.write(combo_image2)
        #out3.write(cropped_prl2)
        #cv2.imwrite('D:\\lines\\r\\frame-'+str(i)+'.jpg',combo_image)
        i+=1

        if 0xFF == ord('p'):
            cv2.waitKey()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
cap.release()

#write PROW file
#out3.release()

with open(json_file_path, 'w', encoding='utf-8') as f:
    json.dump([left_points_exp,right_points_exp, center_points_exp], f, ensure_ascii=False, indent=4)

cv2.destroyAllWindows()