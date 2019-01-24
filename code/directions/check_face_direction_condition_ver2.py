import cv2
import numpy as np
import sys
import os
import glob
import math
from numpy import (array, dot, arccos, clip)
from numpy.linalg import norm

import config
import util
from face_detection_mtcnn import detect_face
sys.path.append('/home/cuong/VNG/National_Identification_Card_Reader/src')
import support_lib as sl

MIN_SIZE = config.FACE_MIN_SIZE
MAX_SIZE = config.FACE_MAX_SIZE

def get_point_coords(points):
    x1 = points[0]
    y1 = points[0 + 5]
    x4 = points[1]
    y4 = points[1 + 5]
    x_nose = points[2]
    y_nose = points[2 + 5]
    x3 = points[3]
    y3 = points[3 + 5]
    x2 = points[4]
    y2 = points[4 + 5]
    return (x1,y1), (x2,y2), (x3,y3), (x4, y4), (x_nose, y_nose)
    
def center_of_4points(points):
	(x1,y1), (x2,y2), (x3,y3), (x4, y4) = points
	xi = ((x1*y2-y1*x2)*(x3-x4) - (x1-x2)*(x3*y4-y3*x4))/((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4))
	yi = ((x1*y2-y1*x2)*(y3-y4) - (y1-y2)*(x3*y4-y3*x4))/((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4))
	return xi, yi
def calculate_angle_vector_and_vertical_vector(vector):
	x, y = vector
	vertical_vector = np.array([0, 1])
	vector = np.array(vector)
	u, v = vertical_vector, vector
	c = dot(u,v)/norm(u)/norm(v) 
	angle = arccos(clip(c, -1, 1))
	if x < 0:
		angle = 2*math.pi - angle 
	return angle
def update_drawed_regions(face_location, (x1,y1), (x2,y2), (x3,y3), (x4, y4), (x_nose, y_nose), drawed_regions, regions, frame):
    (l, t, r, b) =  face_location

    face_size = ((r-l) + (b -t))/2
    print face_size
    top_limit = 0.08*face_size
    bottom_limit = 0.04*face_size

    sl.draw_points(frame, [(x_nose,y_nose)], (0, 255, 0), radius=10, thickness=10)
    four_points = (x1,y1), (x2,y2), (x3,y3), (x4, y4)
    x_intersec, y_intersec = sl.center_of_4points(four_points)
    vector = (x_nose-x_intersec, y_nose-y_intersec)
    angle = sl.calculate_angle_vector_and_vertical_vector(vector)
    vector_length = np.linalg.norm(vector)
    region_number = int(angle/(math.pi/4))
    radius = max((r-l)*1, (b-t)*1)
    box = (c_x, c_y), (w, h), _ = ((l+r)//2, (b+t)//2), (radius*2, radius*2), 0
    cv2.ellipse(frame, box, (0, 0, 255), 100)
    frame =	cv2.arrowedLine(frame, (x_intersec, y_intersec), (x_nose, y_nose), color=(0,0,255), thickness=10)
    if (region_number in [0,1,6,7] and vector_length > bottom_limit) or (region_number not in [0,1,6,7] and vector_length > top_limit):
        for i in range(3):
            angle_i = (regions[region_number][0] + 15*i)/180.0*math.pi
            draw_point = int(c_x + math.sin(angle_i)*radius), int(c_y + math.cos(angle_i)*radius)
            if region_number not in drawed_regions:
                drawed_regions.append(region_number)
    else:
        drawed_regions.append(-1)
        region_number = -1
    for region_number in drawed_regions:
        for i in range(3):
            angle_i = (regions[region_number][0] + 15*i)/180.0*math.pi
            draw_point = int(c_x + math.sin(angle_i)*radius), int(c_y + math.cos(angle_i)*radius)
            sl.draw_points(frame, [draw_point], color=(0, 255, 0), radius=15, thickness=50)
    return region_number

def get_require_direction(indir, outdir):
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    MIN_FACE_PER_DIRECTION = 10
    drawed_regions = []
    regions = []
    for i in range(8):
        region = (i*45, (i+1)*45)
        regions.append(region)
    four_drawed_region_counter = [0]*5
    four_drawed_region_files = dict()
    for i in range(5):
        four_drawed_region_files[i] = []
    list_images_file = glob.glob(os.path.join(indir, '*/*.jpg')) + glob.glob(os.path.join(indir, '*.jpg'))
    for image_file in list_images_file:
        img = cv2.imread(image_file)
        img = cv2.flip(img, 1)
        location, points = detect_face(img, MIN_SIZE, MAX_SIZE)
        if len(location) > 0:
            max_size = -1
            best_index = -1
            for i in range(len(location)):
                (l, t, r, b) = location[i]
                size = (r-l)*(b-t)
                if size > max_size:
                    max_size = size
                    best_index = i

            face_location = location[best_index]
            
            face = img[t:b, l:r]
            if face.shape[0] > 0 and face.shape[1] > 0:
                is_good = util.is_good(face, points[:, best_index])
                # if is_good:
                (x1,y1), (x2,y2), (x3,y3), (x4, y4), (x_nose, y_nose) = util.get_point_coords(points[:, best_index])
                
                region_number = update_drawed_regions(face_location, (x1,y1), (x2,y2), (x3,y3), (x4, y4), (x_nose, y_nose), drawed_regions, regions, img.copy())
                if region_number is not None:
                    if region_number == -1:
                        new_region = 0
                    else:
                        # new_region = region_number//2 + 1
                        if region_number in [7,0]:
                            new_region = 1
                        elif region_number in [1,2]:
                            new_region = 2
                        elif region_number in [3,4]:
                            new_region = 3
                        elif region_number in [5,6]:
                            new_region = 4

                        # if region_number in [1,2,3]:
                        #     new_region = 2
                        # elif region_number in [5,6,7]:
                        #     new_region = 4
                        # elif region_number == 0:
                        #     new_region = 1
                        # elif region_number == 4:
                        #     new_region = 3
                    four_drawed_region_counter[new_region] += 1
                    if four_drawed_region_counter[new_region] <= MIN_FACE_PER_DIRECTION:
                        four_drawed_region_files[new_region].append(image_file)
                        basename = os.path.basename(image_file)
                        basename = basename[:basename.rfind('.')]
                        write_file = os.path.join(outdir, basename + '_' + str(region_number) + '_' +str(new_region) +'.jpg')
                        cv2.imwrite(write_file ,img)
    require_direction = []
    for i in range(5):
        if len(four_drawed_region_files[i]) < MIN_FACE_PER_DIRECTION:
            require_direction.append(i)
    return require_direction

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage: python check_face_direction_condition.py indir outdir'
        sys.exit(0)

    if len(sys.argv) == 3:
        indir = sys.argv[1]
        outdir = sys.argv[2]
    require_direction = get_require_direction(indir, outdir)
    print(require_direction)
