import cv2 as cv
import numpy as np
import pyautogui
import tkinter as tk
import math
import keyboard
import mouse
import time
from statistics import mode

def nothing(x):
	pass

RGBbounds = np.zeros((5,3,3,6),dtype=int) #array which contains all information about bounds
#dimensions are material, thickness, zoom, then values
RGBbounds[0][0][0][:] = [20,8,16,7,20,7] #in order highR, lowR, highG, lowG, highB, lowB
RGBbounds[0][0][1][:] = [165,160,129,122,134,126] #in order highR, lowR, highG, lowG, highB, lowB
RGBbounds[0][0][2][:] = [165,142,140,126,157,140] #in order highR, lowR, highG, lowG, highB, lowB

snap_loc = [450,168]
crop_tl = [1101,80]
crop_br = [3200,1830]

material_dict = {"Graphene":0,"hBN":1,"WSe2":2,"WTe2":3,"CrI3":4}
zoom_RGB_dict = {10: 0, 20: 1, 50: 2}
zoom_vert_travel_dict = {10: 688.0, 20: 344.0, 50: 137.6} 
zoom_horiz_travel_dict = {10: 824.0, 20: 412.0, 50: 164.8}
zoom_focus_dict = {10: 4.75, 20: 1.25, 50: .25}
area_per_pixel_dict = {10: (zoom_horiz_travel_dict[10]*zoom_vert_travel_dict[10])/((crop_br[1]-crop_tl[1])*(crop_br[0]-crop_tl[0])),
        20: (zoom_horiz_travel_dict[20]*zoom_vert_travel_dict[20])/((crop_br[1]-crop_tl[1])*(crop_br[0]-crop_tl[0])),
        50: (zoom_horiz_travel_dict[50]*zoom_vert_travel_dict[50])/((crop_br[1]-crop_tl[1])*(crop_br[0]-crop_tl[0]))}


pyautogui.moveTo(snap_loc[0],snap_loc[1], duration = .25) 

min_size = 50

bonus_range = 0


cv.namedWindow('trackbars')
cv.createTrackbar('Bonus Range', 'trackbars',bonus_range,10,nothing)
cv.createTrackbar('Minimum Blob Size', 'trackbars', min_size, 200,nothing)

kernel = np.ones((5,5),np.uint8)

coords = tk.Tk()
coords.title("Corners and zooms")
tk.Label(coords, text="TL X").grid(row=0, column = 0)
tk.Label(coords, text="TL Y").grid(row=0, column = 2)
tk.Label(coords, text="TL F").grid(row=0, column = 4)

tk.Label(coords, text="TR X").grid(row=1, column = 0)
tk.Label(coords, text="TR Y").grid(row=1, column = 2)
tk.Label(coords, text="TR F").grid(row=1, column = 4)

tk.Label(coords, text="BR X").grid(row=2, column = 0)
tk.Label(coords, text="BR Y").grid(row=2, column = 2)
tk.Label(coords, text="BR F").grid(row=2, column = 4)

tlx = tk.Entry(coords)
tly = tk.Entry(coords)
tlf = tk.Entry(coords)

tlx.grid(row=0, column=1)
tly.grid(row=0, column=3)
tlf.grid(row=0, column=5)
tlx.insert(0, 0)
tly.insert(0, 0)
tlf.insert(0, 0)

trx = tk.Entry(coords)
tr_y = tk.Entry(coords)
trf = tk.Entry(coords)

trx.grid(row=1, column=1)
tr_y.grid(row=1, column=3)
trf.grid(row=1, column=5)
trx.insert(0, 0)
tr_y.insert(0, 0)
trf.insert(0, 0)

brx = tk.Entry(coords)
bry = tk.Entry(coords)
brf = tk.Entry(coords)

brx.grid(row=2, column=1)
bry.grid(row=2, column=3)
brf.grid(row=2, column=5)
brx.insert(0, 0)
bry.insert(0, 0)
brf.insert(0, 0)

tk.Label(coords, text="Material").grid(row=3, column = 0)
material_select = tk.Spinbox(coords, values=("Graphene","hBN","WSe2","WTe2","CrI3"))
material_select.grid(row=3, column = 1)

tk.Label(coords, text="Desired Thickness").grid(row=3, column = 2)
thickness_select = tk.Spinbox(coords, values=("Monolayer","Bilayer","Trilayer","Other"))
thickness_select.grid(row=3, column = 3)

tk.Label(coords, text="Zoom").grid(row=3, column = 4)
zoom_select = tk.Spinbox(coords, values=(10,20,50))
zoom_select.grid(row=3, column = 5)


vals = np.zeros(9)
material = ""
zoom = 0
def getVals():
    global bonus_range
    global min_size
    global material
    global zoom
    vals[0] = int(tlx.get())
    vals[1] = int(tly.get())
    vals[2] = float(tlf.get())
    
    vals[3] = int(trx.get())
    vals[4] = int(tr_y.get())
    vals[5] = float(trf.get())
    
    vals[6] = int(brx.get())
    vals[7] = int(bry.get())
    vals[8] = float(brf.get())
    
    material = material_select.get()
    zoom = int(zoom_select.get())
    bonus_range = cv.getTrackbarPos('Bonus Range', 'trackbars')
    min_size = cv.getTrackbarPos('Minimum Blob Size', 'trackbars')
    coords.destroy()
    
b = tk.Button(coords, text="ok", command = getVals)
b.grid(row = 4)
coords.mainloop()

highRC = int(RGBbounds[material_dict[material]][0][zoom_RGB_dict[zoom]][0])       #load in boundaries
lowRC = int(RGBbounds[material_dict[material]][0][zoom_RGB_dict[zoom]][1])        #from selected material & thickness
highGC = int(RGBbounds[material_dict[material]][0][zoom_RGB_dict[zoom]][2])
lowGC = int(RGBbounds[material_dict[material]][0][zoom_RGB_dict[zoom]][3])
highBC = int(RGBbounds[material_dict[material]][0][zoom_RGB_dict[zoom]][4])
lowBC = int(RGBbounds[material_dict[material]][0][zoom_RGB_dict[zoom]][5])

x_travel_count = math.ceil((vals[3]-vals[0])/zoom_horiz_travel_dict[zoom]) #compute number of moves for x and y
y_travel_count = math.ceil((vals[7]-vals[4])/zoom_vert_travel_dict[zoom])

dfdx = 0
dfdy = 0
if(x_travel_count != 0):
    dfdx = ((vals[5]-vals[2])/zoom_focus_dict[zoom])/x_travel_count  #compute focus mouse clicks per move
if(y_travel_count != 0):
    dfdy = ((vals[8]-vals[5])/zoom_focus_dict[zoom])/y_travel_count

loc = [0,0] #initialize
cur_foc = 0
dir = 1
i = 1
def process(i):
    cap = pyautogui.screenshot()

    img_native = cv.cvtColor(np.array(cap), cv.COLOR_BGR2RGB)
    img_cropped = img_native[crop_tl[1]:crop_br[1], crop_tl[0]:crop_br[0]]

    Z = img_cropped.reshape((-1,3))
    Z = np.float32(Z)
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 5, .5)
    K = 6
    ret,label,center=cv.kmeans(Z,K,None,criteria,10,cv.KMEANS_RANDOM_CENTERS)
    center = np.uint8(center)
    background = center[mode(label.flatten())]

    highR = (highRC-20)/100*background[0]+background[0]
    lowR = (lowRC-20)/100*background[0]+background[0]
    highG = (highGC-20)/100*background[0]+background[0]
    lowG = (lowGC-20)/100*background[0]+background[0]
    highB = (highBC-20)/100*background[0]+background[0]
    lowB = (lowBC-20)/100*background[0]+background[0]

    img_binary = cv.inRange(img_cropped, (lowR, lowG, lowB), (highR,highG,highB))

    img_filtered = cv.morphologyEx(img_binary, cv.MORPH_OPEN,cv.getStructuringElement(cv.MORPH_ELLIPSE,(5,5)))#kernel)
    no,img_filtered = cv.threshold(img_filtered,127,255,cv.THRESH_BINARY)
    img_filtered = cv.dilate(img_filtered, kernel, iterations = 1)


    contours,heirarchy = cv.findContours(img_filtered,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv.contourArea(contour)*area_per_pixel_dict[zoom] > min_size:
            print(cv.contourArea(contour)*area_per_pixel_dict[zoom])
            x,y,w,h = cv.boundingRect(contour)
            cv.imwrite( "Snap "+str(i)+".jpg", img_cropped );
            cv.rectangle(img_cropped,(x,y),(x+w,y+h),(0,255,0),2)
            pyautogui.click(snap_loc[0], snap_loc[1]) 
            cv.imwrite( "Snap box"+str(i)+".jpg", img_cropped );
            i += 1
            pyautogui.moveTo(crop_tl[0]+200,crop_tl[1]+200, duration = .25) 
            time.sleep(2)
            break
    return i
            

def focus(cur_foc):
    if int(cur_foc) != 0:
        if(cur_foc > 0):
            keyboard.press('ctrl')
            time.sleep(.01)
            mouse.wheel(1)
            cur_foc -= 1
        elif(cur_foc < 0):
            keyboard.press('ctrl')
            time.sleep(.01)
            mouse.wheel(-1)
            cur_foc += 1
        time.sleep(.01)
        keyboard.release('ctrl')

    return cur_foc
            

done = False
print(min_size)
time.sleep(5)
while(not done):
    i = process(i)
    print ("looped")
    
    keyboard.press('ctrl')
    time.sleep(.01)
    if dir == 1 and loc[0] != x_travel_count:
        keyboard.press_and_release('right')
        loc[0] += 1
        cur_foc += dfdx
    elif dir == -1 and loc[0] != 0:
        keyboard.press_and_release('left')
        loc[0] -= 1
        cur_foc -= dfdx
    else:
        if loc[1] == y_travel_count:
            done = True
        keyboard.press_and_release('down')
        loc[1] += 1
        dir *= -1
        cur_foc += dfdy
    keyboard.release('ctrl')
    cur_foc = focus(cur_foc)
    
    breakKey = cv.waitKey(3000)
    if breakKey == 27:
        break

cv.destroyAllWindows()
