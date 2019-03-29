from os import mkdir, system
from os.path import split, splitext, join, exists
from identification import IdentifyModel, Image, TestImage, Person, Tree
from data import load_emb_data, get_config
from face_model import FaceModel
import cv2, pickle
import numpy as np
from utils import get_batch_number, get_slice_of_batch
from time import time
import pdb


def identify(tree, ide_model, known_vector_dir, k, output, threshold, batch_size, tree_path, predict_issame_dir):
	print('Identifing!')
	if exists(tree_path):
		with open(tree_path, 'rb') as f:
			tree = pickle.load(f)
	# else:
	if True:
		n_test_img = tree.len()
		# tree_candidates = []
		# pdb.set_trace()
		# n_batch = get_batch_number(n_test_img, batch_size)
		# start = time()
		# for batch_idx in range(n_batch):
		# 	s, e = get_slice_of_batch(n_test_img, batch_size, batch_idx)
		# 	_batch = tree.test_imgs()[s:e]
		# 	_batch = [e.emb() for e in _batch]
		# 	bstart = time()
		# 	_batch_candidates = ide_model.batch_candidates(_batch)
		# 	print(batch_idx, time() - bstart)
		# 	tree_candidates.extend(_batch_candidates)
		# tree.paste_candidate_idx(tree_candidates)
		# print('Get candidate done! ', time() - start)

		predict_issame = []
		for i in range(13):
			with open(join(predict_issame_dir, 'predict_issame_' + str(i) + '.pkl'), 'rb') as f:
				_predict_issame = pickle.load(f)
			predict_issame.extend(_predict_issame)
		
		pairs = []
		for i in range(13):
			with open(join('/home/cuongvm/Resources/datasets/faces/vn_celeb_face_recognition_lfw10_delete02_renamed_vertificate_input_pairs', 'pairs_' + str(i) + '.txt'), 'r') as f:
				# _predict_issame = pickle.load(f)
				lines = f.readlines()
				for line in lines[1:]:
					pairs.append(line.split(' '))
		pair_idx = 0

		


		# pdb.set_trace()
		predict_idx = 0
		start = time()
		for test_img in tree.test_imgs():
			test_emb = test_img.emb()
			persons = test_img.candidates()
			for person in persons:
				paths = ide_model.idx2path[str(person.idx())]
				person_dist = []
				for path in paths:
					img_dir, file_name = split(path)
					bfile_name = splitext(file_name)[0]
					if bfile_name.split('_')[-1] != pairs[predict_idx][3].rstrip():
						pdb.set_trace()
					# name = split(img_dir)[1]
					# emb_path = join(known_vector_dir, name, bfile_name + '.pkl')
					# with open(emb_path, 'rb') as f:
					# 	_emb = pickle.load(f)
					# img = Image(path, _emb)
					# person.append(img)
					# dist = np.sum(np.square(test_emb-img.emb()))
					if predict_issame[predict_idx] == True:
						dist = 0
					else:
						dist = 1
					predict_idx += 1
					person_dist.append(dist)
				test_img.append_dist(person_dist)
		print('Cal dist done! ', time() - start)

		# if not exists(split(tree_path)[0]):
		# 	system('mkdir -p ' + split(tree_path)[0])
		# with open(tree_path, 'wb') as f:
		# 	pickle.dump(tree, f)

	top_5s = []
	for test_img in tree.test_imgs():
		is_sames = []
		for person_dist in test_img.dists():
			print('person_dist: ', person_dist)
			print('vote: ')
			# pdb.set_trace()
			vote = 0
			for dist in person_dist:
				if dist < threshold:
					vote += 1
			print  str(vote) + ', ',
			if vote > 0:
				is_sames.append(1)
			else:
				is_sames.append(0)
			print()
		print('is_sames: ', is_sames)

		top_5 = [0] * k
		is_novelty = False
		for i, (person, is_same) in enumerate(zip(test_img.candidates(), is_sames)):
			if i == 0:
				if is_same == 1:
					top_5[i] = person.idx()
				else:
					top_5[i] = 1000
					is_novelty = True
		candidate_idxs = [person.idx() for person in test_img.candidates()]
		if is_novelty == False:
			top_5[-1] = 1000
			top_5[1:-1] = candidate_idxs[1:-1]
		else:
			top_5[1:] = candidate_idxs[0:-1]
		top_5s.append(top_5)
		
	if not exists(split(output)[0]):
		system('mkdir -p ' + split(output)[0])
	with open(output, 'w') as f:
		f.write('image,label\n')
		for i, (test_img, top_5) in enumerate(zip(tree.test_imgs(),top_5s)):
			path = test_img.path()
			file_name = split(path)[1]
			bfile_name = splitext(file_name)[0]
			name = bfile_name[:bfile_name.rfind('_')]
			f.write(name + '.png,' + ' '.join([str(e) for e in top_5]))
			if i < len(top_5s) - 1:
				f.write('\n')


if __name__=='__main__':
	import argparse
	ap = argparse.ArgumentParser()
	ap.add_argument("--data-dir", help="data-dir")
	ap.add_argument("--known-vector-dir", help="known-vector-dir")
	ap.add_argument("--ver-vector-dir", help="ver-vector-dir")
	ap.add_argument("--model-path", help="model-path")
	ap.add_argument("--idx2path", help="idx2path")
	ap.add_argument("--threshold", type=float,help="threshold")
	ap.add_argument("--k", type=int, help="n_top_candidate")
	ap.add_argument("--output", help="output")
	ap.add_argument("--batch-size", type=int, help="batch-size")
	ap.add_argument("--tree-path", help="tree-path")
	ap.add_argument("--predict-issame-dir", help="predict-issame-dir")

	args= vars(ap.parse_args())

	tree = Tree()
	if not exists(args['tree_path']):
		start = time()
		name2file, emb_data = load_emb_data(args['data_dir'], vector_dir=args['ver_vector_dir'])
		data = {name: [join(args['data_dir'], name, f) for f in files] for name, files in name2file.items()}
		print('loaded data: ', time() - start)
		for name, paths in data.items():
			_emb = emb_data[name][0]
			test_img = TestImage(paths[0], _emb)
			tree.append(test_img) 
	# pdb.set_trace()

	ide_model = IdentifyModel()
	ide_model.load_classify_model(args['model_path'])
	# ide_model.known_vector_dir(args['known_vector_dir'])
	# ide_model.set_threshold(args['threshold'])
	ide_model.set_n_top_candidate(args['k'])
	ide_model.load_idx2path(args['idx2path'])
	print('ide_model.idx2path: ', ide_model.idx2path)
	identify(tree, ide_model, args['known_vector_dir'], args['k'], args['output'], args['threshold'], args['batch_size'], args['tree_path'], args['predict_issame_dir'])


		