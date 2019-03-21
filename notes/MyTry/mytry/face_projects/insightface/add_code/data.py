import sys
sys.path.append('./deploy')
import random
from os import listdir
from os.path import expanduser, join, split, splitext, exists
from glob import glob
import cv2, pickle
from nface_embedding import FaceModel
from easydict import EasyDict as edict
import mxnet as mx
import argparse



def file_idx(file_name):
	bfile_name = splitext(file_name)[0]
	es = bfile_name.split('_')
	idx = es[-1]
	return idx

def get_config():
	args = edict()
	args.model = 'models/model-r100-ii/model,0000'
	args.det = 0
	args.threshold = 0.87
	args.image_size = '112,112'
	args.gpu = 0
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

def load_emb_data(data_dir, vector_dir=None):
	data = load_data(data_dir)
	print('load_data: ', data)
	args = get_config()
	emb_data = {}
	for name, file_names in data.items():
		_embs = []
		for file_name in file_names:
			bfile_name = splitext(file_name)[0]
			emb_path = join(vector_dir, name, bfile_name + '.pkl')
			if not exists(emb_path):
				_img = cv2.imread(join(data_dir, name, file_name))
				_img = cv2.resize(_img, (112,112))
				_img = mx.nd.array(_img)
				face_model = FaceModel(args)
				_emb = face_model.get_feature(_img)
				with open(emb_path, 'wb') as f:
					pickle.dump(emb_path, f)
			else:
				_emb = pickle.load(emb_path)
			_embs.append(_emb)
		emb_data[name] = _embs
	return data, emb_data
		
			



	emb_data 
	return -1, -1
	
def main(indir, outdir, npair):
	indir = expanduser(indir)
	outdir = expanduser(outdir)
	person_dirs = listdir(indir)
	n_people = len(person_dirs)
	print('person_dirs: ', person_dirs)

	pairs = []
	idxs_of_person = {}
	for person_dir in person_dirs:
		_idxs = []
		person_files = listdir(join(indir, person_dir))
		print('person_files: ', person_files)
		n_path = len(person_files)

		


		
		for i in range(n_path):
			file_name1 = person_files[i]
			idx1 = file_idx(file_name1)
			_idxs.append(idx1)
			# print('idx: ', idx1)
			for j in range(i+1, n_path):
				file_name2 = person_files[j]
				idx2 = file_idx(file_name2)
				# print('idx: ', idx2)
				pairs.append((person_dir, idx1, idx2))
		idxs_of_person[person_dir] = _idxs
	
	for i in range(n_people):
		person_dir1 = person_dirs[i]
		for idx1 in idxs_of_person[person_dir1]:
			for j in range(i+1, n_people):
				person_dir2 = person_dirs[j]
				print(i, j)
				print(person_dir1, person_dir2)
				for idx2 in idxs_of_person[person_dir2]:
					pairs.append((person_dir1, idx1, person_dir2, idx2))
	print('pairs: ', pairs)
	final_pairs = random.sample(pairs, npair)
	print('len(final_pairs): ', len(final_pairs))
	with open(join(outdir, 'pairs.txt'), 'w') as f:
		f.write('Hello\n')
		for i, pair in enumerate(final_pairs):
			f.write(' '.join(pair))
			if i < len(pairs) - 1:
				f.write('\n')
	



if __name__=='__main__':
	import argparse
	ap = argparse.ArgumentParser()
	ap.add_argument("--indir", help="indir")
	ap.add_argument("--outdir", help="outdir")
	ap.add_argument("--npair", type=int, help="npair")
	args= vars(ap.parse_args())
	main(args["indir"], args["outdir"], args["npair"])
