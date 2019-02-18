import cv2
import numpy as np
import sys
import os
import glob
import math
from numpy import (array, dot, arccos, clip)
from numpy.linalg import norm

import config
# import util
from util import preprocess_image
from face_detection_mtcnn import detect_face, detect_face_all_directions

MIN_SIZE = config.FACE_MIN_SIZE
MAX_SIZE = config.FACE_MAX_SIZE

MIN_FACE_DIRECTION_CENTER = 10
MIN_FACE_DIRECTION_UP = 8
MIN_FACE_DIRECTION_LOW = 8
MIN_FACE_DIRECTION_RIGHT = 15
MIN_FACE_DIRECTION_LEFT = 15
MIN_FACE_DIRECTION_DICT = {0: MIN_FACE_DIRECTION_CENTER, 1: MIN_FACE_DIRECTION_LOW, 2: MIN_FACE_DIRECTION_RIGHT, 3: MIN_FACE_DIRECTION_UP, 4: MIN_FACE_DIRECTION_LEFT}
DEBUG = False

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


def add_padding_to_img(img, padding):
	width, height = _resolution = get_resolution(img)
	padding_width, padding_height = width + 2*padding, height + 2*padding
	padding_img = create_img((padding_width, padding_height))
	padding_img[padding: height + padding, padding: width + padding] = img
	return padding_img


def create_img(img_resolution, is_value_is_zero = True):
	width, height = img_resolution
	if is_value_is_zero:
		img = np.zeros((height,width,3), np.uint8)
	else:
		img = np.ones((height,width,3), np.uint8)
	return img


def get_resolution(img):
	resolution = _weight, _height = img.shape[1::-1]
	return resolution


def cut_window(img, window):
	return img.copy()[window_to_slice(window)]


def window_to_slice(window):
	topleft_x, topleft_y, w, h = window
	window_slice = slice(topleft_y, topleft_y+h), slice(topleft_x,topleft_x+w)
	return window_slice

	
def draw_points(img, points, color = (0,0,255), radius=2, thickness=-1):
	for point in points:
		cv2.circle(img , point, radius, color, thickness)


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
	

def evaluate_region_direction(face_location, (x1,y1), (x2,y2), (x3,y3), (x4, y4), (x_nose, y_nose), frame):
	(l, t, r, b) =  face_location

	# face_size = ((r-l) + (b -t))/2
	face_size = (b -t)
	top_limit = 0.07*face_size
	bottom_limit = 0.015*face_size
	if DEBUG:
		draw_points(frame, [(x_nose,y_nose)], (0, 255, 0), radius=10, thickness=10)
		draw_points(frame, [(x1,y1)], (255, 0, 0), radius=10, thickness=10)
		draw_points(frame, [(x2,y2)], (0, 0, 255), radius=10, thickness=10)
		draw_points(frame, [(x3,y3)], (255, 0, 255), radius=10, thickness=10)
		draw_points(frame, [(x4,y4)], (0, 255, 255), radius=10, thickness=10)
	
	four_points = (x1,y1), (x2,y2), (x3,y3), (x4, y4)
	x_intersec, y_intersec = center_of_4points(four_points)
	vector = (x_nose-x_intersec, y_nose-y_intersec)
	angle = calculate_angle_vector_and_vertical_vector(vector)
	vector_length = np.linalg.norm(vector)
	region_number = int(angle/(math.pi/4))
	radius = max((r-l)*1, (b-t)*1)
	box = (c_x, c_y), (w, h), _ = ((l+r)//2, (b+t)//2), (radius*2, radius*2), 0
	frame =	cv2.arrowedLine(frame, (x_intersec, y_intersec), (x_nose, y_nose), color=(0,0,255), thickness=10)
	if (region_number in [0,1,6,7] and vector_length < bottom_limit):
		new_region = 0
	elif (region_number in [2, 5] and vector_length < 0.03*face_size):
		new_region = 0
	elif region_number in [7,0]:
		new_region = 1
	elif region_number in [1,2]:
		new_region = 2
	elif region_number in [3]:
		if angle/(math.pi/4) > 3.5 and vector_length > top_limit:
			new_region = 3
		elif angle/(math.pi/4) <= 3.8 and vector_length > 0.04*face_size:
			new_region = 2
		else:
			new_region = 0
	elif region_number in [4]:
		if angle/(math.pi/4) < 4.5 and vector_length > top_limit:
			new_region = 3
		elif angle/(math.pi/4) >= 4.2 and vector_length > 0.04*face_size:
			new_region = 4
		else:
			new_region = 0
	elif region_number in [5,6]:            
		new_region = 4
	else:
		print(region_number)
		
	if new_region == 0:
		direction_str = 'Center'
	elif new_region == 1:
		direction_str = 'Bottom'
	elif new_region == 2:
		direction_str = 'Right'
	elif new_region == 3:
		direction_str = 'Top'
	elif new_region == 4:
		direction_str = 'Left'
	cv2.putText(frame, str(direction_str), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 4)
	return new_region, vector_length/face_size


def check_false_condition(region_number, four_drawed_region_counter):
	if four_drawed_region_counter[region_number] < MIN_FACE_DIRECTION_DICT[region_number]:
		return True
	return False


def get_require_direction(indir):
	base_folder = indir[:indir.rfind('/')]
	indir_name = indir[:indir.rfind('/')]
	outdir_name = 'tmp_out'
	outdir = os.path.join(base_folder, outdir_name)
	# os.system("rm -rf " + outdir)
	if not os.path.exists(outdir):
		os.makedirs(outdir)
	if DEBUG:
		test_outdir = '/home/cuong/VNG/temp/face_system/data/test_data/test_result'
		tmp_test_outdir = '/home/cuong/VNG/temp/face_system/data/test_data/tmp_test_outdir'
		os.system("rm -rf " + test_outdir)
		os.system("mkdir " + test_outdir)
		os.system("rm -rf " + tmp_test_outdir)
		os.system("mkdir " + tmp_test_outdir)

	four_drawed_region_counter = [0]*5
	four_drawed_region_files = dict()
	for i in range(5):
		four_drawed_region_files[i] = []
	vecto_length_each_region = dict()
	for i in range(5):
		vecto_length_each_region[i] = []
	list_images_file = glob.glob(os.path.join(indir, '*/*.jpg')) + glob.glob(os.path.join(indir, '*.jpg'))
	ignore_img_count = 0
	rotation_angle = None
	
	new_file_count = 0
	for image_file in list_images_file:
		filename = os.path.split(image_file)[-1]
		filename = filename[:filename.rfind('.')]
		postfix = filename.split('_')
		if len(postfix) >= 3 and postfix[-1] == 'processed':
			direction = int(postfix[-3])
			vector_length = float(postfix[-2])
			four_drawed_region_counter[direction] += 1
			four_drawed_region_files[direction].append(image_file)
			vecto_length_each_region[direction].append(vector_length)
			continue
		else:
			new_file_count += 1
		
		img = cv2.imread(image_file)
		padding_img = add_padding_to_img(img, 50)
		if rotation_angle is None:
			location, points, angle = detect_face_all_directions(padding_img, MIN_SIZE, MAX_SIZE)
			rotation_angle = angle
			if rotation_angle is None:
				continue
			img = preprocess_image(img, rotation_angle=rotation_angle)
		else:
			img = preprocess_image(img, rotation_angle=rotation_angle)
			location, points = detect_face(padding_img, MIN_SIZE, MAX_SIZE)
		cv2.imwrite(image_file, img)

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
				
				# (x1,y1), (x2,y2), (x3,y3), (x4, y4), (x_nose, y_nose) = util.get_point_coords(points[:, best_index])
				(x1,y1), (x2,y2), (x3,y3), (x4, y4), (x_nose, y_nose) = get_point_coords(points[:, best_index])
				
				new_region, vector_length = evaluate_region_direction(face_location, (x1,y1), (x2,y2), (x3,y3), (x4, y4), (x_nose, y_nose), img)
				four_drawed_region_counter[new_region] += 1
				four_drawed_region_files[new_region].append(image_file)
				vecto_length_each_region[new_region].append(vector_length)

				if DEBUG:
					basename = os.path.basename(image_file)
					basename = basename[:basename.rfind('.')]
					test_write_file = os.path.join(test_outdir, basename  + '_' +str(new_region) +'.jpg')
					cv2.imwrite(test_write_file ,img)
					tmp_test_write_file = os.path.join(tmp_test_outdir, basename  + '_' +str(new_region) +'.jpg')
					cv2.imwrite(tmp_test_write_file ,img)
			else:
				print(image_file)
				ignore_img_count += 1
		else:
			print(image_file)
			ignore_img_count += 1
	print 'file ignore = ', ignore_img_count
	print 'new file =', new_file_count
	print 'file consider = ', len(list_images_file) - ignore_img_count


	final_four_drawed_region_files = dict()
	for i in range(5):
		final_four_drawed_region_files[i] = []
	final_vecto_length_each_region = dict()
	for i in range(5):
		final_vecto_length_each_region[i] = []
	
	require_direction = []
	for i in [0, 1, 2, 3, 4]:
		if check_false_condition(i, four_drawed_region_counter):
			require_direction.append(i)
			end_index = four_drawed_region_counter[i]
		else:
			end_index = min(MIN_FACE_DIRECTION_DICT[i] + 4, four_drawed_region_counter[i])
		if i == 0:
			reverse = False
		else:
			reverse = True
		file_and_vector_length = [[f, vector_length] for f, vector_length in zip(four_drawed_region_files[i], vecto_length_each_region[i])]
		file_and_vector_length = sorted(file_and_vector_length, key=lambda element:element[1], reverse=reverse)
		if len(file_and_vector_length) > 0:
			for image_file_and_vector_length in file_and_vector_length[:end_index]:
				image_file, vector_length = image_file_and_vector_length
				final_four_drawed_region_files[i].append(image_file)
				final_vecto_length_each_region[i].append(vector_length)
	
	image_number = 0
	for i in range(5):
		print 'Huong ' + str(i) + ': ', four_drawed_region_counter[i], len(final_four_drawed_region_files[i])
		image_number += len(final_four_drawed_region_files[i])
	print 'image_number = ', image_number

	for i in range(5):
		for image_file, vector_length in zip(final_four_drawed_region_files[i], final_vecto_length_each_region[i]):
			basename = os.path.basename(image_file)
			basename = basename[:basename.rfind('.')]
			postfix = basename.split('_')
			if len(postfix) >= 3 and postfix[-1] == 'processed':
				write_file = os.path.join(outdir, basename + '.jpg')
			else:
				write_file = os.path.join(outdir, basename  + '_' +str(i) + '_' + str(vector_length)[:min(5, len(str(vector_length)))] + '_processed' +'.jpg')
			img = cv2.imread(image_file)
			cv2.imwrite(write_file ,img)

	if DEBUG:
		for i in range(5):
			for test_image_file in set(four_drawed_region_files[i]) - set(final_four_drawed_region_files[i]):
				basename = os.path.basename(test_image_file)
				basename = basename[:basename.rfind('.')]
				os.rename(os.path.join(test_outdir, basename  + '_' +str(i) +'.jpg'), os.path.join(test_outdir, basename  + '_' +str(i) +'x.jpg'))


	


	'''

	remain_region_files = []
	remain_vector_length = []

	for i in range(5):
		for f, vector_length in zip(four_drawed_region_files[i], vecto_length_each_region[i]):
			if f not in final_four_drawed_region_files[i]:
				remain_region_files.append(f)
				remain_vector_length.append(f)

	add_final_four_drawed_region_files = []
	file_and_vector_length = [[f, vector_length] for f, vector_length in zip(remain_region_files, remain_vector_length)]
	file_and_vector_length = sorted(file_and_vector_length, key=lambda element:element[1], reverse=True)
	if len(file_and_vector_length) > 0:
		for image_file_and_vector_length in file_and_vector_length[:min(80 - image_number, len(file_and_vector_length))]:
			image_file = image_file_and_vector_length[0]
			add_final_four_drawed_region_files.append(image_file)

	for image_file in add_final_four_drawed_region_files:
		basename = os.path.basename(image_file)
		basename = basename[:basename.rfind('.')]
		write_file = os.path.join(outdir, basename  + '_' +str(i) +'.jpg')
		img = cv2.imread(image_file)
		cv2.imwrite(write_file ,img)
	#	new_write_file = glob.glob(os.path.join(test_outdir, basename) + '*')[0]
	# 	not_extend_write_file = new_write_file[:new_write_file.rfind('.')]
	# 	os.rename(new_write_file, not_extend_write_file +'o.jpg')

	for i in range(5):
		not_satify_set = set(four_drawed_region_files[i]) - set(final_four_drawed_region_files[i]) - set(add_final_four_drawed_region_files)
		for test_image_file in not_satify_set:
			basename = os.path.basename(test_image_file)
			basename = basename[:basename.rfind('.')]
			# new_write_file = glob.glob(os.path.join(test_outdir, basename) + '*')[0]
			# writefile_basename = os.path.basename(new_write_file)
			# writefile_basename = writefile_basename[:writefile_basename.rfind('x.')]
			# os.remove(os.path.join(tmp_test_outdir, writefile_basename)  +'.jpg')
	
	print 'added image number = ', len(add_final_four_drawed_region_files) 
	print 'final image_number = ', image_number + len(add_final_four_drawed_region_files) 
	
	'''
	
	
	os.system("rm -rf " + indir)
	os.rename(outdir, indir)
	return require_direction

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print 'Usage: python check_face_direction_condition.py indir'
		sys.exit(0)

	if len(sys.argv) == 2:
		indir = sys.argv[1]
	require_direction = get_require_direction(indir)
	
	print(require_direction)