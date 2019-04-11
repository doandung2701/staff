from __future__ import division
import sys
import cv2
import numpy as np
import traceback
sys.path.append('.')

import darknet.python.darknet as dn
from sort_label import numeric_compare, analysis, is_bottom, is_top

from os.path 				import splitext, basename, join
from glob					import glob
from darknet.python.darknet import detect
from src.label				import dknet_label_conversion
from src.utils 				import nms
from os import system, mkdir

from numpy import (array, dot, arccos, clip)
from numpy.linalg import norm
from math import pi as PI

def cosin(u, v):
	u, v = array(u), array(v)
	return dot(u,v)/norm(u)/norm(v)


def ordinal_score(u):
	cos = cosin(u, [-1,0])
	angle = arccos(cos)
	dangle = angle/PI*180
	if u[1] > 0:
		dangle = dangle
	elif u[0] > 0 and u[1] < 0:
		dangle = 1000 - (360 - dangle)
	elif u[0] < 0 and u[1] < 0:
		dangle = 1000 - (360 - dangle - 90)
	return dangle


# class F:
# 	def __init__(self, l, v):
# 		self.__tl, self.__br = l
# 		self.v = v
# 	def tl(self):
# 		return self.__tl
# 	def br(self):
# 		return self.__br


# width, height = 1, 1
# a = F( ((0, 2), (1, 3)), 'a' )
# b = F( ((2, 3), (3, 4)), 'b' )
# L = [a, b]
# L_pair = list(zip(L, [(width, height)]* len(L)))
# L_pair = sorted(L_pair, cmp=numeric_compare)

# [e[0].v for e in sorted(L_pair, cmp=numeric_compare)]
def letter2digit(strg):
	strg=strg.replace('Q', '0')
	strg=strg.replace('D', '0')
	strg=strg.replace('Z', '7')
	strg=strg.replace('S', '5')
	strg=strg.replace('I', '1')
	strg=strg.replace('A', '4')
	strg=strg.replace('B', '8')
	strg=strg.replace('T', '1')
	strg=strg.replace('G', '6')
	
	return strg

def digit2letter(strg):
	strg=strg.replace('5', 'S')
	strg=strg.replace('7', 'Z')
	# strg=strg.replace('1', 'I')
	strg=strg.replace('8', 'B')
	strg=strg.replace('2', 'Z')
	strg=strg.replace('4', 'A')
	strg=strg.replace('6', 'G')
	strg=strg.replace('1', 'T')
	strg=strg.replace('0', 'U')
	return strg

# def output_verify1(lp_str):
# 	# lp_str=lp_str.replace('W', 'N')
# 	s1=lp_str[:2]
# 	s2=lp_str[2:3]
# 	s3=lp_str[3:4]
# 	s1 = letter2digit(s1)
# 	s2 = digit2letter(s2)
# 	# s1=s1.replace('Z','4')
# 	# s1=s1.replace('L','4')
# 	# s3=s3.replace('Z','4')
# 	# s3=s3.replace('L','4')
# 	lp_str=s1+s2+s3
# 	return lp_str

# def output_verify2(lp_str):
# 	# lp_str=lp_str.replace('Z', '4')
# 	# lp_str=lp_str.replace('L', '4')
# 	lp_str = letter2digit(lp_str)
# 	return lp_str


def output_verify1(lp_str):
	lp_str=lp_str.replace('W', 'N')
	s1=lp_str[:2]
	s2=lp_str[2:3]
	s3=lp_str[3:4]
	s1=s1.replace('Z','4')
	s1=s1.replace('L','4')
	s3=s3.replace('Z','4')
	s3=s3.replace('L','4')
	s1 = letter2digit(s1)
	lp_str=s1+s2+s3
	return lp_str

def output_verify2(lp_str):
	lp_str=lp_str.replace('Z', '2')
	lp_str=lp_str.replace('L', '4')
	lp_str = letter2digit(lp_str)
	return lp_str


if __name__ == '__main__':

	try:
	
		input_dir  = sys.argv[1]
		output_dir = input_dir
		ocr_weights = sys.argv[2]

		ocr_threshold = .4

		# ocr_weights = 'data/finetune_ocr/ocr-net.weights'
		# ocr_weights = 'data/retrained_ocr/backup/ocr-net_final.weights'
		# ocr_weights = 'data/retrained_ocr/20191103-1145/ocr-net_final.weights'
		# ocr_weights = 'darknet/backup/ocr-net_final.weights'
		# ocr_weights = 'data/retrained_ocr/20191203-1140/ocr-net_100000.weights'
		# ocr_weights = 'data/retrained_ocr/20191403-1510/ocr-net_100000.weights'

		# 2.5 hours
		# ocr_weights = 'data/retrained_ocr/20191103-1458/ocr-net_final.weights'
		ocr_netcfg  = 'data/ocr/ocr-net.cfg'
		ocr_dataset = 'data/ocr/ocr-net.data'
		# ocr_netcfg = 'data/retrained_ocr/ocr-net.cfg'
		# ocr_dataset = 'data/retrained_ocr/ocr-net.data'

		# ocr_netcfg = 'data/finetune_ocr/ocr-net.cfg'
		# ocr_dataset = 'data/finetune_ocr/ocr-net.data'


		# ocr_weights = 'data/retrained_ocr_keep_structure/20191103-1223/ocr-net_900.weights'
		# ocr_netcfg = 'data/retrained_ocr_keep_structure/ocr-net-test.cfg'
		# ocr_dataset = 'data/retrained_ocr_keep_structure/ocr-net.data'



		ocr_net  = dn.load_net(ocr_netcfg, ocr_weights, 0)
		ocr_meta = dn.load_meta(ocr_dataset)

		imgs_paths = sorted(glob('%s/*lp.png' % output_dir))

		print 'Performing OCR...'

		for i,img_path in enumerate(imgs_paths):

			print '\tScanning %s' % img_path

			bname = basename(splitext(img_path)[0])
			# if bname.startswith('24954'):
			# 	import pdb; pdb.set_trace()
				
			Ilp = cv2.imread(img_path)
			is_detected = False 
			# print('Ilp.shape[1]/Ilp.shape[0] : ', Ilp.shape[1]/Ilp.shape[0] )
			if Ilp.shape[1]/Ilp.shape[0] < 1.8:
				ocr_tmp = 'ocr-tmp'
				system('rm -r ' + ocr_tmp)
				mkdir(ocr_tmp)
				Ilp1=Ilp[2:62,0:210]
				Ilp2=Ilp[58:118,0:210]
				Ilp1_path = join(ocr_tmp, bname + '_1.jpg')
				Ilp2_path = join(ocr_tmp, bname + '_2.jpg')
				cv2.imwrite(Ilp1_path, Ilp1)
				cv2.imwrite(Ilp2_path, Ilp2)
				R1,(width,height) = detect(ocr_net, ocr_meta, Ilp1_path ,thresh=ocr_threshold, nms=None)
				R2,(width,height) = detect(ocr_net, ocr_meta, Ilp2_path ,thresh=ocr_threshold, nms=None)
				if len(R1) and len(R2):
					L1 = dknet_label_conversion(R1,width,height)
					L1 = nms(L1,.45)
					L1.sort(key=lambda x: x.tl()[0])
					lp_str1 = ''.join([chr(l.cl()) for l in L1])

					L2 = dknet_label_conversion(R2,width,height)
					L2 = nms(L2,.45)
					L2.sort(key=lambda x: x.tl()[0])
					lp_str2 = ''.join([chr(l.cl()) for l in L2])
					lp_str1 = output_verify1(lp_str1)
					lp_str2 = output_verify2(lp_str2)
					lp_str = lp_str1+lp_str2
					is_detected = True
				
			else:
				R,(width,height) = detect(ocr_net, ocr_meta, img_path ,thresh=ocr_threshold, nms=None)
				if len(R):
					L = dknet_label_conversion(R,width,height)
					L = nms(L,.45)
					L.sort(key=lambda x: x.tl()[0])
					lp_str = ''.join([chr(l.cl()) for l in L])
					new_line_idx = 3
					lp_str1 = lp_str[:new_line_idx+1]
					lp_str2 = lp_str[new_line_idx+1:]
					lp_str1 = output_verify1(lp_str1)
					lp_str2 = output_verify2(lp_str2)
					lp_str = lp_str1 + lp_str2

					is_detected = True
				
			# if Ilp.shape != (60,210,3):
			# if Ilp.shape != (80,240,3):
			# 	import pdb; pdb.set_trace()
			if is_detected:

			# if len(R):

			# 	print('###')
			# 	L = dknet_label_conversion(R,width,height)
			# 	L = nms(L,.45)
			# 	# L.sort(key=lambda x: ordinal_score([(x.tl()[0] + x.br()[0] - 1)*width//2, -(x.tl()[1] + x.br()[1] - 1)*height//2]))
			# 	L_pair = list(zip(L, [(width, height)]* len(L)))
			# 	L_pair = sorted(L_pair, cmp=numeric_compare)
				# new_line_idx = None
				# for i, l_pair in enumerate(L_pair):
				# 	if i < len(L_pair) - 1:
				# 		if is_bottom(L_pair[i+1], l_pair):
				# 			new_line_idx = i
				# if new_line_idx is None:
				# 	new_line_idx = 3
				# l1 = ''.join([chr(l.cl()) for (l,_) in L_pair[:new_line_idx+1]])
				# l2 = ''.join([chr(l.cl()) for (l,_) in L_pair[new_line_idx+1:]])
				# l1 = output_verify1(l1)
				# l2 = output_verify2(l2)
				# print('l1: ', l1)
				# print('l2: ', l2)
				# lp_str = l1 + l2

				# L, _ = zip(*L_pair)
				# lp_str = ''.join([chr(l.cl()) for l in L])

				with open('%s/%s_str.txt' % (output_dir,bname),'w') as f:
					f.write(lp_str + '\n')

				print '\t\tLP: %s' % lp_str
				# for i, l in enumerate(L):
				# 	print('#')
				# 	print(chr(l.cl()))
				# 	if l != L[-1]:
				# 		ll, lt, lr, lb = l.tl()[0]*width, l.tl()[1]*height, l.br()[0]*width, l.br()[1]*height
				# 		print('ll, lt, lr, lb = ', ll, lt, lr, lb)
				# 		print('(aw, ah), (acx, acy) = ', analysis((ll, lt, lr, lb)))
				# 		l1_pair, l2_pair = (l, (width, height)), (L[i+1], (width, height))
				# 		print('#numeric_compare(l, L[i+1])', numeric_compare(l1_pair, l2_pair))
				# 		print('is_bottom(L[i+1], l) = ', is_bottom(l2_pair, l1_pair))
				# 		print('is_top(L[i+1], l) = ', is_top(l2_pair, l1_pair))
						

				# 	a, b = (l.tl()[0]*width + l.br()[0]*width)//2, (l.tl()[1]*height + l.br()[1]*height)//2
				# 	print('centerx, centery, width, height = ', a, b, width, height)
				# 	print('centerx - width//2 , centery - height//2 = ', a - width//2, b - height//2)					
				# 	print('dangle_with_minus1_zero: ', ordinal_score([(l.tl()[0] + l.br()[0])*width//2  - width//2, - (l.tl()[1] + l.br()[1])*height//2 + height//2]))

			else:

				print 'No characters found'

	except:
		traceback.print_exc()
		sys.exit(1)

	sys.exit(0)

# cv2.resize()
# cv2.imwrite()