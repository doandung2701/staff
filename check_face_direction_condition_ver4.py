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

MIN_FACE_DIRECTION_CENTER = 10
MIN_FACE_DIRECTION_UP = 8
MIN_FACE_DIRECTION_LOW = 8
MIN_FACE_DIRECTION_RIGHT_LEFT = 40
MIN_FACE_DIRECTION_DICT = {0: MIN_FACE_DIRECTION_CENTER, 1: MIN_FACE_DIRECTION_LOW, 3: MIN_FACE_DIRECTION_UP}


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
def evaluate_region_direction(face_location, (x1,y1), (x2,y2), (x3,y3), (x4, y4), (x_nose, y_nose), frame):
	(l, t, r, b) =  face_location

	# face_size = ((r-l) + (b -t))/2
	face_size = (b -t)
	top_limit = 0.07*face_size
	bottom_limit = 0.015*face_size

	sl.draw_points(frame, [(x_nose,y_nose)], (0, 255, 0), radius=10, thickness=10)
	sl.draw_points(frame, [(x1,y1)], (255, 0, 0), radius=10, thickness=10)
	sl.draw_points(frame, [(x2,y2)], (0, 0, 255), radius=10, thickness=10)
	sl.draw_points(frame, [(x3,y3)], (255, 0, 255), radius=10, thickness=10)
	sl.draw_points(frame, [(x4,y4)], (0, 255, 255), radius=10, thickness=10)
	
	four_points = (x1,y1), (x2,y2), (x3,y3), (x4, y4)
	x_intersec, y_intersec = sl.center_of_4points(four_points)
	vector = (x_nose-x_intersec, y_nose-y_intersec)
	angle = sl.calculate_angle_vector_and_vertical_vector(vector)
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
	if region_number == 0:
		if four_drawed_region_counter[0] < MIN_FACE_DIRECTION_CENTER:
			return True
		return False
	elif region_number == 1:
		if four_drawed_region_counter[1] < MIN_FACE_DIRECTION_LOW:
			return True
		return False
	elif region_number == 2 or region_number == 4:
		if four_drawed_region_counter[2] + four_drawed_region_counter[4] < MIN_FACE_DIRECTION_RIGHT_LEFT:
			return True
		return False
	elif region_number == 3:
		if four_drawed_region_counter[3] < MIN_FACE_DIRECTION_UP:
			return True
		return False
def get_require_direction(indir):
	base_folder = indir[:indir.rfind('/')]
	outdir = indir[:indir.rfind('/')]
	outdir = os.path.join(base_folder, 'tmp_out')
	# os.system("rm -rf " + outdir)
	if not os.path.exists(outdir):
		os.makedirs(outdir)
	# test_outdir = '/home/cuong/VNG/temp/face_system/data/test_data/test_result'
	# tmp_test_outdir = '/home/cuong/VNG/temp/face_system/data/test_data/tmp_test_outdir'
	# os.system("rm -rf " + test_outdir)
	# os.system("mkdir " + test_outdir)
	# os.system("rm -rf " + tmp_test_outdir)
	# os.system("mkdir " + tmp_test_outdir)

	
	four_drawed_region_counter = [0]*5
	four_drawed_region_files = dict()
	for i in range(5):
		four_drawed_region_files[i] = []
	vecto_length_each_region = dict()
	for i in range(5):
		vecto_length_each_region[i] = []
	list_images_file = glob.glob(os.path.join(indir, '*/*.jpg')) + glob.glob(os.path.join(indir, '*.jpg'))
	ignore_img_count = 0
	
	for image_file in list_images_file:
		img = cv2.imread(image_file)
		img = sl.add_padding_to_img(img, 50)
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
				
				new_region, vector_length = evaluate_region_direction(face_location, (x1,y1), (x2,y2), (x3,y3), (x4, y4), (x_nose, y_nose), img)
				four_drawed_region_counter[new_region] += 1
				four_drawed_region_files[new_region].append(image_file)
				vecto_length_each_region[new_region].append(vector_length)


				basename = os.path.basename(image_file)
				basename = basename[:basename.rfind('.')]
				# test_write_file = os.path.join(test_outdir, basename  + '_' +str(new_region) +'.jpg')
				# cv2.imwrite(test_write_file ,img)
				# tmp_test_write_file = os.path.join(tmp_test_outdir, basename  + '_' +str(new_region) +'.jpg')
				# cv2.imwrite(tmp_test_write_file ,img)
			else:
				print(image_file)
				ignore_img_count += 1
		else:
			print(image_file)
			ignore_img_count += 1
	print 'file ignore = ', ignore_img_count
	print 'file consider = ', len(list_images_file) - ignore_img_count


	final_four_drawed_region_files = dict()
	for i in range(5):
		final_four_drawed_region_files[i] = []

	
	require_direction = []
	for i in [0, 1, 3]:
		if check_false_condition(i, four_drawed_region_counter):
			require_direction.append(i)
			end_index = four_drawed_region_counter[i]
		else:
			end_index = MIN_FACE_DIRECTION_DICT[i]
		
		file_and_vector_length = [[f, vector_length] for f, vector_length in zip(four_drawed_region_files[i], vecto_length_each_region[i])]
		file_and_vector_length = sorted(file_and_vector_length, key=lambda element:element[1])
		if len(file_and_vector_length) > 0:
			for image_file_and_vector_length in file_and_vector_length[:end_index]:
				image_file = image_file_and_vector_length[0]
				final_four_drawed_region_files[i].append(image_file)
	

	if four_drawed_region_counter[2] < four_drawed_region_counter[4]:
		lower, upper = 2, 4
	else:
		lower, upper = 4, 2
	if check_false_condition(2, four_drawed_region_counter):
		for i in [2,4]:
			for image_file in four_drawed_region_files[i]:
				final_four_drawed_region_files[i].append(image_file)
		require_direction.append(lower)
	else:
		file_and_vector_length = [[f, vector_length] for f, vector_length in zip(four_drawed_region_files[upper], vecto_length_each_region[upper])]
		file_and_vector_length = sorted(file_and_vector_length, key=lambda element:element[1])
		if MIN_FACE_DIRECTION_RIGHT_LEFT > four_drawed_region_counter[lower]:
			for image_file in four_drawed_region_files[lower]:
				final_four_drawed_region_files[lower].append(image_file)
			
			if len(file_and_vector_length) > 0:
				for image_file_and_vector_length in file_and_vector_length[:MIN_FACE_DIRECTION_RIGHT_LEFT - four_drawed_region_counter[lower]]:
					image_file = image_file_and_vector_length[0]
					final_four_drawed_region_files[upper].append(image_file)
	

			# for image_file in four_drawed_region_files[upper][:MIN_FACE_DIRECTION_RIGHT_LEFT - four_drawed_region_counter[lower]]:
			# 	final_four_drawed_region_files[upper].append(image_file)
		else:
			for i in [2,4]:
				# for image_file in four_drawed_region_files[i][: MIN_FACE_DIRECTION_RIGHT_LEFT//2]:
				# 	final_four_drawed_region_files[i].append(image_file)
				if len(file_and_vector_length) > 0:
					for image_file_and_vector_length in file_and_vector_length[:MIN_FACE_DIRECTION_RIGHT_LEFT//2]:
						image_file = image_file_and_vector_length[0]
						final_four_drawed_region_files[i].append(image_file)	

	image_number = 0
	for i in range(5):
		print 'Huong ' + str(i) + ': ', four_drawed_region_counter[i], len(final_four_drawed_region_files[i])
		image_number += len(final_four_drawed_region_files[i])

	print indir
	print outdir

	os.system("rm -rf " + indir)
	os.renames(outdir, indir)
	# os.system('mv' + outdir + ' ' + indir)


	'''


	remain_region_files = []
	remain_vector_length = []

	# add_final_four_drawed_region_files = []

	# for i in range(5):
	# 	for image_file in final_four_drawed_region_files[i]:
	# 		basename = os.path.basename(image_file)
	# 		basename = basename[:basename.rfind('.')]
	# 		write_file = os.path.join(outdir, basename  + '_' +str(i) +'.jpg')
	# 		img = cv2.imread(image_file)
	# 		img = sl.add_padding_to_img(img, 50)
	# 		img = cv2.flip(img, 1)
	# 		cv2.imwrite(write_file ,img)
	# 	for f, vector_length in zip(four_drawed_region_files[i], vecto_length_each_region[i]):
	# 		if f not in final_four_drawed_region_files[i]:
	# 			remain_region_files.append(f)
	# 			remain_vector_length.append(f)
	# 	for test_image_file in set(four_drawed_region_files[i]) - set(final_four_drawed_region_files[i]):
	# 		basename = os.path.basename(test_image_file)
	# 		basename = basename[:basename.rfind('.')]
			# os.rename(os.path.join(test_outdir, basename  + '_' +str(i) +'.jpg'), os.path.join(test_outdir, basename  + '_' +str(i) +'x.jpg'))
	


	file_and_vector_length = [[f, vector_length] for f, vector_length in zip(remain_region_files, remain_vector_length)]
	file_and_vector_length = sorted(file_and_vector_length, key=lambda element:element[1])
	if len(file_and_vector_length) > 0:
		for image_file_and_vector_length in file_and_vector_length[:min(60 - image_number, len(file_and_vector_length))]:
			image_file = image_file_and_vector_length[0]
			add_final_four_drawed_region_files.append(image_file)

	for i in range(5):
		not_satify_set = set(four_drawed_region_files[i]) - set(final_four_drawed_region_files[i]) - set(add_final_four_drawed_region_files)
		for test_image_file in not_satify_set:
			basename = os.path.basename(test_image_file)
			basename = basename[:basename.rfind('.')]
			# new_write_file = glob.glob(os.path.join(test_outdir, basename) + '*')[0]
			# writefile_basename = os.path.basename(new_write_file)
			# writefile_basename = writefile_basename[:writefile_basename.rfind('x.')]
			# os.remove(os.path.join(tmp_test_outdir, writefile_basename)  +'.jpg')
	# for image_file in add_final_four_drawed_region_files:
	# 	basename = os.path.basename(image_file)
	# 	basename = basename[:basename.rfind('.')]
	# 	write_file = os.path.join(outdir, basename  + '_' +str(i) +'.jpg')
	# 	img = cv2.imread(image_file)
	# 	img = sl.add_padding_to_img(img, 50)
	# 	img = cv2.flip(img, 1)
	# 	cv2.imwrite(write_file ,img)

	# 	new_write_file = glob.glob(os.path.join(test_outdir, basename) + '*')[0]
	# 	not_extend_write_file = new_write_file[:new_write_file.rfind('.')]
	# 	os.rename(new_write_file, not_extend_write_file +'o.jpg')
	
	'''
	
	print 'image_number = ', image_number
	# print 'added image number = ', len(add_final_four_drawed_region_files) 
	# print 'final image_number = ', image_number + len(add_final_four_drawed_region_files) 
	return require_direction

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print 'Usage: python check_face_direction_condition.py indir'
		sys.exit(0)

	if len(sys.argv) == 2:
		indir = sys.argv[1]
	require_direction = get_require_direction(indir)
	
	print(require_direction)
