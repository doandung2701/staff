import cv2
from os import listdir, mkdir
from os.path import expanduser, join, split, splitext, exists, isfile
from zemcy.videostream import QueuedStream
# from easydict import EasyDict as edict
import pickle
import numpy as np
from random import randint
import pdb
from time import time
from datetime import datetime as dt

from collections import Counter
import operator
import collections


def main(args):
	video = QueuedStream(args['url'], queueSize=8, fps=24)
	video.start()
	# video = cv2.VideoCapture(args['url'])
	ret, frame = video.read()
	if not ret:
		print 'Camera is not open!'
		sys.exit(1)
	print('Camera Resolution: ', frame.shape[1::-1])

	fourcc = cv2.VideoWriter_fourcc(*'mp4v')
	out = cv2.VideoWriter(args['output_path'],fourcc, 24.0, frame.shape[1::-1])

	while video.isOpened():
		ret, frame = video.read()
		if not ret:
			print 'Camera is not open!'
			break
		out_frame = frame.copy()
		out.write(out_frame)
		if args['mode'] == 'show':
			cv2.imshow('demo', out_frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
	video.release()
	out.release()
		

if __name__=='__main__':
	import argparse
	ap = argparse.ArgumentParser()
	ap.add_argument("-u","--url", help="url")
	ap.add_argument("--mode", default='show', help="mode = show/notshow")
	ap.add_argument("-op","--output_path", default='test.mp4', help="output_path")
	args= vars(ap.parse_args())
	main(args)
