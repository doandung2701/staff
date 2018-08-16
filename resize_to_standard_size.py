import cv2
import numpy as np 
import sys
import math

def get_resolution(img):
	resolution = _weight, _height = img.shape[1::-1]
	return resolution
def create_img(img_resolution, is_value_is_zero = True):
	width, height = img_resolution
	if is_value_is_zero:
		img = np.zeros((height,width,3), np.uint8)
	else:
		img = np.ones((height,width,3), np.uint8)
	return img
def resize_img(img, cvt_area):
    width, height = _img_revolution = img.shape[1::-1]
    area = width*height
    ratio = math.sqrt(1.0*cvt_area/area)
    cvt_width = int(width*ratio)
    cvt_height = int(height*ratio)
    resize_shape = (cvt_width, cvt_height)
    resized_img = cv2.resize(img, resize_shape)
    return resized_img
def window_to_slice(window, slice_step=None):
	left, top, w, h = window
	if slice_step is None:
		window_slice = slice(top, top+h), slice(left,left+w)
	else:
		w_slice_step, h_slice_step = slice_step, slice_step
		window_slice = slice(top, top+h, h_slice_step), slice(left,left+w, w_slice_step)
	return window_slice
def resize(img_path, standard_size):
    standard_w, standard_h = standard_size
    img = cv2.imread(img_path)
    img_w, img_h = get_resolution(img)
    standard_img = create_img((standard_w,standard_h))
    resized_h = standard_h
    ratio = 1.0*resized_h/img_h
    resized_w = int(ratio*img_w)
    if resized_w <= standard_w:
        resized_img = resize_img(img, resized_w*resized_h)
        window = (standard_w - resized_w)//2, 0, resized_w, resized_h
        standard_img[window_to_slice(window)] = resized_img
    else:
        standard_img = cv2.resize(img, (standard_w, standard_h))
    return standard_img

if __name__ == '__main__':
    try:
        img_path = sys.argv[1]
    except:
        img_path = 'src/CardDetection/card_imgs_folder/cmt_mat_truoc_0.jpg'
    try:
        size_str = sys.argv[2]
    except:
        size_str = '300x360'
    standard_size = tuple(map(int,size_str.split('x')))
    img = cv2.imread(img_path)
    standard_img = resize(img_path, standard_size)
    cv2.imshow('img',img)
    cv2.imshow('standard_img',standard_img)
    cv2.waitKey(0)

    
