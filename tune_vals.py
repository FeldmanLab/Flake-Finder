import cv2 as cv
import numpy as np
import pyautogui
def nothing(x):
	pass

highR = 165
lowR = 160
highG = 129
lowG = 122
highB = 134
lowB = 126

min_size = 50
cv.namedWindow('trackbars', cv.WINDOW_NORMAL)
cv.createTrackbar('High R', 'trackbars',highR,255,nothing)
cv.createTrackbar('Low R', 'trackbars',lowR,255,nothing)
cv.createTrackbar('High G', 'trackbars',highG,255,nothing)
cv.createTrackbar('Low G', 'trackbars',lowG,255,nothing)
cv.createTrackbar('High B', 'trackbars',highB,255,nothing)
cv.createTrackbar('Low B', 'trackbars',lowB,255,nothing)
cv.createTrackbar('Minimum Blob Size', 'trackbars', min_size, 200,nothing)

cv.waitKey(0)

crop_tl = [1101,80]
crop_br = [3200,1830]
cap = pyautogui.screenshot()
img_native = cv.cvtColor(np.array(cap), cv.COLOR_BGR2RGB)
#img_cropped = img_native
#print(np.shape(img_cropped))
img_cropped = img_native[crop_tl[1]:crop_br[1], crop_tl[0]:crop_br[0]]

#cv.namedWindow("Processed")
cv.namedWindow('output')
cv.namedWindow('Binary Thresholded')
#cv.namedWindow('Original Image')
cv.namedWindow('Filtered')

#cv.imshow("Original Image",img_cropped)

kernel = np.ones((5,5),np.uint8)

zoom_vert_travel_dict = {10: 688.0, 20: 344.0, 50: 137.6} 
zoom_horiz_travel_dict = {10: 824.0, 20: 412.0, 50: 164.8}
zoom_focus_dict = {10: 4.75, 20: 1.25, 50: .25}
zoom = 10
area_per_pixel_dict = {10: (zoom_horiz_travel_dict[10]*zoom_vert_travel_dict[10])/((crop_br[1]-crop_tl[1])*(crop_br[0]-crop_tl[0])),
        20: (zoom_horiz_travel_dict[20]*zoom_vert_travel_dict[20])/((crop_br[1]-crop_tl[1])*(crop_br[0]-crop_tl[0])),
        50: (zoom_horiz_travel_dict[50]*zoom_vert_travel_dict[50])/((crop_br[1]-crop_tl[1])*(crop_br[0]-crop_tl[0]))}

def process(cap,lowR,lowG,lowB,highR,highG,highB,min_size):
    img_native = cv.cvtColor(np.array(cap), cv.COLOR_BGR2RGB)
    img_cropped = img_native[crop_tl[1]:crop_br[1], crop_tl[0]:crop_br[0]]

    img_binary = cv.inRange(img_cropped, (lowR, lowG, lowB), (highR,highG,highB))

    img_filtered = cv.morphologyEx(img_binary, cv.MORPH_OPEN,cv.getStructuringElement(cv.MORPH_ELLIPSE,(5,5)))#kernel)
    no,img_filtered = cv.threshold(img_filtered,127,255,cv.THRESH_BINARY)
    img_filtered = cv.dilate(img_filtered, kernel, iterations = 1)

    contours,heirarchy = cv.findContours(img_filtered,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv.contourArea(contour)*area_per_pixel_dict[zoom] > min_size:
            print(cv.contourArea(contour)*area_per_pixel_dict[zoom])
            x,y,w,h = cv.boundingRect(contour)
            cv.rectangle(img_cropped,(x,y),(x+w,y+h),(0,255,0),2)

    return img_cropped
            


while(1):
	highR = cv.getTrackbarPos('High R', 'trackbars')
	lowR = cv.getTrackbarPos('Low R', 'trackbars')
	highG = cv.getTrackbarPos('High G', 'trackbars')
	lowG = cv.getTrackbarPos('Low G', 'trackbars')
	highB = cv.getTrackbarPos('High B', 'trackbars')
	lowB = cv.getTrackbarPos('Low B', 'trackbars')
	min_size = cv.getTrackbarPos('Minimum Blob Size', 'trackbars')
	
	img_binary = cv.inRange(img_cropped, (lowR, lowG, lowB), (highR,highG,highB))
	cv.imshow('Binary Thresholded', img_binary)
	
	output = process(cap,lowR,lowG,lowB,highR,highG,highB,min_size)

	cv.imshow('output', output)

	img_filtered = cv.morphologyEx(img_binary, cv.MORPH_OPEN,cv.getStructuringElement(cv.MORPH_ELLIPSE,(5,5)))#kernel)
	no,img_filtered = cv.threshold(img_filtered,127,255,cv.THRESH_BINARY)
	img_filtered = cv.dilate(img_filtered, kernel, iterations = 1)

	cv.imshow('Filtered', img_filtered)

	breakKey = cv.waitKey(1)
	if breakKey == 27:
		break

cv.destroyAllWindows()
