import sys
sys.path.append('./deploy')
# sys.path.append('/home/cuongvm/MySetting/staff/notes/MyTry/mytry/face_projects/insightface/add_code')

import random
from os import listdir, mkdir
from os.path import expanduser, join, split, splitext, exists
from glob import glob
import cv2, pickle
# from nface_model import FaceModel
from nface_embedding import FaceModel
from easydict import EasyDict as edict
import mxnet as mx
import argparse
import pdb



def get_config():
	args = edict()
	args.model = 'models/model-r100-ii/model,0000'
	args.det = 0
	args.threshold = 0.87
	args.image_size = '112,112'
	args.gpu = 0
	args.ga_model = ''
	args.flip = 1
	return args

def load_data(data_dir):
	name2file = {}
	person_dirs = listdir(data_dir)
	for person_dir in person_dirs:
		person_files = listdir(join(data_dir, person_dir))
		name2file[person_dir] = []
		for person_file in person_files:
			name2file[person_dir].append(person_file)
	return name2file

def load_emb(data_dir, data, vector_dir):
	args = get_config()
	fmodel = FaceModel(args)
	emb_data = {}

	for name, file_names in data.items():
		_embs = []
		for file_name in file_names:
			bfile_name = splitext(file_name)[0]
			emb_path = join(vector_dir, name, bfile_name + '.pkl')
			if not exists(join(vector_dir, name)):
				mkdir(join(vector_dir, name))
			if not exists(emb_path):
				_img = cv2.imread(join(data_dir, name, file_name))
				# pdb.set_trace()

				# i_input = fmodel.get_input(_img)
				# if i_input is not None:
				# 	_img = i_input
				# else:
				# 	pdb.set_trace()
				# 	exit(0)
				
				_emb = fmodel.get_feature(_img)
				with open(emb_path, 'wb') as f:
					pickle.dump(_emb, f)
			else:
				with open(emb_path, 'rb') as f:
					_emb = pickle.load(f)
			_embs.append(_emb)
		emb_data[name] = _embs
	# pdb.set_trace()
	return emb_data

def load_emb_data(data_dir, vector_dir=None):
	data = load_data(data_dir)
	print('load_data: ', data)
	# pdb.set_trace()
	emb_data = load_emb(data_dir, data, vector_dir)
	return data, emb_data

