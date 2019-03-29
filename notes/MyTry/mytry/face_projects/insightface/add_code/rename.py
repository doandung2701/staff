import sys
sys.path.append('./deploy')
# sys.path.append('/home/cuongvm/MySetting/staff/notes/MyTry/mytry/face_projects/insightface/add_code')

import random
from os import listdir, mkdir, system
from os.path import expanduser, join, split, splitext, exists
from glob import glob
import cv2, pickle
from data import load_data


if __name__=='__main__':
	import argparse
	ap = argparse.ArgumentParser()
	ap.add_argument("--data-dir", help="data-dir")
	ap.add_argument("--vector-dir", help="vector_dir")
	ap.add_argument("--idx2path", help="idx2path")
	ap.add_argument("--output-dir", help="output-dir")
	args= vars(ap.parse_args())

	name2file = load_data(args['data_dir'])
	data = {name: [join(args['data_dir'], name, f) for f in files] for name, files in name2file.items()}

	outdir = args['output_dir']
	for name, paths in data.items():
		mkdir(join(outdir, name))
		n_img = len(paths)
		for i, path in enumerate(paths):
			system('cp ' + path + ' ' + join(outdir, name, name + '_%04d' % int(i) + '.jpg'))


