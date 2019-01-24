import numpy as np
from numpy import (array, dot, arccos, clip)
from numpy.linalg import norm
import math
def center_of_4points(points):
	(x1,y1), (x2,y2), (x3,y3), (x4, y4) = points
	xi = ((x1*y2-y1*x2)*(x3-x4) - (x1-x2)*(x3*y4-y3*x4))/((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4))
	yi = ((x1*y2-y1*x2)*(y3-y4) - (y1-y2)*(x3*y4-y3*x4))/((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4))
	return xi, yi
def calculate_angle_vector_and_vertical_vector(vector):
	x, y = vector
	vertical_vector = np.array([0, 1])
	# vertical_vector = np.array([1, 0])

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
