import cv2 
import numpy as np 
from matplotlib import pyplot as plt
import imutils
import math
import pytesseract

DEFAULT_INPUT_FOLDER = "data"
DEFAULT_TEXT_FOLDER = "text"
DEFAULT_WIP_FOLDER = "wip"


def rotate_to_reciept(img):
    # img = cv2.resize(img, (0, 0), fx = 0.2, fy = 0.2)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5,), 0)

    low_threshold = 100
    high_threshold = 150
    edges = cv2.Canny(blurred, low_threshold, high_threshold)

    rho = 1  # distance resolution in pixels of the Hough grid
    theta = np.pi / 180  # angular resolution in radians of the Hough grid
    threshold = 15  # minimum number of votes (intersections in Hough grid cell)
    min_line_length = 50  # minimum number of pixels making up a line
    max_line_gap = 20  # maximum gap in pixels between connectable line segments
    # line_image = np.copy(img) * 0  # creating a blank to draw lines on

    # Run Hough on edge detected image
    # Output "lines" is an array containing endpoints of detected line segments
    lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
                        min_line_length, max_line_gap)

    count = 0
    filtered = []
    for line in lines:
        for x1,y1,x2,y2 in line:
            dx = x2 - x1
            dy = y2 - y1
            angle = math.atan(dy/dx)
            length = math.sqrt(dx**2 + dy**2)
            if abs(angle) <= np.pi*(1/18):
                count += 1
                filtered.append((line, length, angle))

    filtered = sorted(filtered, key= lambda x:x[1], reverse=True)

    # create a new image with the detected lines
    # for line, _, _1 in filtered[:10]:
    #     for x1,y1,x2,y2 in line:
    #         cv2.line(line_image,(x1,y1),(x2,y2),(255,0,0),5)

    deg = filtered[0][2]* (180/np.pi)

    # rotate the image
    image_center = tuple(np.array(img.shape[1::-1]) / 2)
    rotation_matrix = cv2.getRotationMatrix2D(image_center, deg, 1.0)
    result = cv2.warpAffine(img, rotation_matrix, img.shape[1::-1], flags=cv2.INTER_LINEAR)

    
    # increase the contrast
    _, result = cv2.threshold(result, 180, 255, cv2.THRESH_BINARY)

    # overlay image with lines with the original image
    # lines_edges = cv2.addWeighted(img, 0.8, line_image, 1, 0)
    return result


def detect_text(img, psm=6):
    # Use psm 4 for single column, use psm 6 if the price are not picked up
    options = "--psm " + str(psm)
    text = pytesseract.image_to_string(
        cv2.cvtColor(img, cv2.COLOR_BGR2RGB),
        config=options)
    return text.split("\n")


# TODO - Resize image first for faster computation
# TODO - Crop image first for faster computation
def detect_by_contour(img):

    # img = cv2.resize(img, (0, 0), fx = 0.2, fy = 0.2)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5,), 0)
    edged = cv2.Canny(blurred, 75, 200)

    # setting threshold of gray image 
    # _, threshold = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY) 
    # _, threshold = cv2.threshold(blurred, 190, 255, cv2.THRESH_BINARY) 

    # using a threshold  
    # contours, _ = cv2.findContours( 
    #     threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # using a edge map (is that what it's called?)
    contours = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours) # Only needed with edge

    contours = sorted(contours, key=lambda x:cv2.contourArea(x), reverse=True)

    ### detecting 4 corners ###

    # # initialize a contour that corresponds to the receipt outline
    # receiptCnt = None
    # # loop over the contours
    # for c in contours:
    # 	# approximate the contour
    # 	peri = cv2.arcLength(c, True)
    # 	approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    # 	# if our approximated contour has four points, then we can
    # 	# assume we have found the outline of the receipt
    # 	if len(approx) == 4:
    # 		receiptCnt = approx
    # 		break 

    cv2.drawContours(img, [contours[0]],0, (0, 0, 255), 5)
    return img


def detect(image, folder=DEFAULT_INPUT_FOLDER, debug=False):
    # Load the image
    name, _ = image.split(".")
    img = cv2.imread(folder+'/'+image)

    # Rotate image and detect text
    rotated = rotate_to_reciept(img)
    texts = detect_text(rotated)

    # print(texts)
    # print("\n")

    if not debug:
        return texts
    
    # For debugging
    # Save text into file
    with open(DEFAULT_TEXT_FOLDER+'/'+name+'_text.txt', mode='w') as file:
        for text in texts:
            file.writelines(text)
            file.write('\n')

    # Save wip image for debugging
    cv2.imwrite(DEFAULT_WIP_FOLDER+'/'+name+'_wip.jpeg', rotated)

    return texts