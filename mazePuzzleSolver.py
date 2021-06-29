import streamlit as st
import os
import cv2
import numpy as np
import time
from PIL import Image

def dilate(img, struct_element, origin):
	h, w = img.shape
	result = img[:,:].copy()
	add_y = struct_element.shape[0] - origin[0]
	add_x = struct_element.shape[1] - origin[1]
	for i in range (h):
		for j in range (w):
            # and bool(struct_element[origin[0]][origin[1]])
			if bool(img[i][j]) and bool(struct_element[origin[0]][origin[1]]):
				x1 = j-origin[1]
				x2 = j+add_x
				y1 = i-origin[0]
				y2 = i+add_y
				# structure modification
				s_x1 = 0
				s_x2 = struct_element.shape[1]
				s_y1 = 0
				s_y2 = struct_element.shape[0]

				if x1 < 0:
					s_x1 = s_x1 + (0 - x1)
					x1 = 0
				if x2 > w:
					s_x2 = s_x2 - (x2 - (w))
					x2 = w
				if y1 < 0:
					s_y1 = s_y1 + (0 - y1)
					y1 = 0
				if y2 > h:
					s_y2 = s_y2 - (y2 - (h))
					y2 = h

				window = img[y1:y2, x1:x2] | struct_element[s_y1:s_y2, s_x1:s_x2]
				result[y1:y2, x1:x2] = window
	return result
def erode(img, struct_element, origin):
	h, w = img.shape
	result = img[:,:].copy()
	add_y = struct_element.shape[0] - origin[0]
	add_x = struct_element.shape[1] - origin[1]
	for i in range (h):
		for j in range (w):
			if bool(img[i][j]) and bool(struct_element[origin[0]][origin[1]]):
				x1 = j-origin[1]
				x2 = j+add_x
				y1 = i-origin[0]
				y2 = i+add_y

				s_x1 = 0
				s_x2 = struct_element.shape[1]
				s_y1 = 0
				s_y2 = struct_element.shape[0]

				if x1 < 0:
					s_x1 = s_x1 + (0 - x1)
					x1 = 0
				if x2 > w:
					s_x2 = s_x2 - (x2 - (w))
					x2 = w
				if y1 < 0:
					s_y1 = s_y1 + (0 - y1)
					y1 = 0
				if y2 > h:
					s_y2 = s_y2 - (y2 - (h))
					y2 = h
				window = img[y1:y2, x1:x2]
				flag = False
				for x in range(window.shape[0]):
					for y in range(window.shape[1]):
						if window[x][y] == 0:
							flag=True
							break
					if flag:break
				if flag:
					result[i][j] = 0
	return result

def solve(ImgCV, kSize = 21):
    sleepTime = 2

    img = ImgCV.copy()

    ret, binaryImage = cv2.threshold(img, 10, 255, cv2.THRESH_BINARY_INV)
    imageLocation.image(binaryImage, use_column_width=True, caption="Binary Image")
    time.sleep(sleepTime)

    contours, hierarchy = cv2.findContours(binaryImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    path = np.zeros(binaryImage.shape, np.uint8)
    cv2.drawContours(path, contours, 1, (255,255,255), cv2.FILLED)
    imageLocation.image(path, use_column_width=True, caption='After contour')
    time.sleep(sleepTime)
    kernel = np.ones((kSize,kSize),np.uint8)*255
    dilated = dilate(path,kernel,[kSize//2,kSize//2])

    imageLocation.image(dilated, use_column_width=True, caption="Dilated")
    time.sleep(sleepTime)
    kernel = np.ones((int(kSize/2),int(kSize/2)),np.uint8)*255
    erosion = erode(dilated,kernel,[kSize//4,kSize//4])
    # erosion = cv2.erode(dilated,kernel,iterations = 1)

    imageLocation.image(erosion, use_column_width=True, caption="Eroded")

    time.sleep(sleepTime)

    diff = cv2.absdiff(erosion, dilated)

    img = cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)

    img[diff==255] = (0,255,0)

    imageLocation.image(img, use_column_width=True, caption="Solved Puzzle")

def hideMenuandFooter():
    hide_menu_footer_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_menu_footer_style, unsafe_allow_html=True)

def applyStyleCSS():
    with open("style.css") as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)

hideMenuandFooter()
applyStyleCSS()

folder = 'mazes/'
    
imageDict = {}
for i in os.listdir(folder):
    imageDict[str(i[:-4])] = "".join((folder, i))

st.markdown("<h1 style='text-align: center; color: white;'>Maze Puzzle Solver</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: white;'>Solving Maze Puzzles from Images using Morphological Operations</p>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: white;'>Select a maze image from the dropdown and click on solve:</h3>", unsafe_allow_html=True)
key = st.selectbox("Picture choices", list(imageDict.keys()), 0)
filenameDropDown = imageDict[key]
ImgCV = cv2.imread(filenameDropDown, 0)
fileName = filenameDropDown

btn = st.button("Solve the maze!")

imageLocation = st.empty()

if ImgCV is not None:
    imageLocation.image(ImgCV, use_column_width=True, caption="Original Maze")

if btn:
    if ImgCV is not None:
        solve(ImgCV)