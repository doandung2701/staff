from os import mkdir
from os.path import split, splitext, join, exists
from identification import IdentifyModel, Image, TestImage, Person, Tree
from data import load_emb_data, get_config
from nface_embedding import FaceModel
import cv2, pickle
import numpy as np
from utils import get_batch_number, get_slice_of_batch
from time import time
import pdb


def identify(tree, ide_model, known_vector_dir, k, output, threshold, batch_size):
	print('Identifing!')
	n_test_img = tree.len()
	tree_candidates = []
	# pdb.set_trace()
	n_batch = get_batch_number(n_test_img, batch_size)
	start = time()
	for batch_idx in range(n_batch):

		s, e = get_slice_of_batch(n_test_img, batch_size, batch_idx)
		_batch = tree.test_imgs()[s:e]
		bstart = time()
		_batch_candidates = ide_model.batch_candidates(_batch)
		print(batch_idx, time() - bstart)
		tree_candidates.extend(_batch_candidates)
	tree.paste_candidate(tree_candidates)
	print('Get candidate done! ', time() - start)

	start = time()
	for test_img in tree.test_imgs():
		test_emb = test_img.emb()
		persons = test_img.candidates()
		for person in persons:
			paths = ide_model.idx2path[person.idx]
			for path in paths:
				img_dir, file_name = split(path)[0]
				bfile_name = splitext(file_name)[0]
				name = split(img_dir)[1]
				emb_path = join(known_vector_dir, name, bfile_name + '.pkl')
				with open(emb_path, 'rb') as f:
					_emb = pickle.load(f)
				img = Image(path, _emb)
				person.append(img)
				dist = np.sum(np.square(test_emb-img.emb))
				person.append_dist(dist)
	print('Cal dist done! ', time() - start)

	top_5s = []
	for test_img in tree.test_imgs():
		is_sames = []
		for dists in zip(test_img.dists()):
			vote = 0
			for dist in dists:
				if dist < threshold:
					vote += 1
			print('vote: ', vote)
			if vote > 0:
				is_sames.append(1)
			else:
				is_sames.append(0)
		print('is_sames: ', is_sames)

		top_5 = [0] * k
		is_novelty = False
		for i, (person, is_same) in enumerate(zip(test_img.candidates(), is_sames)):
			if i == 0:
				if is_same == True:
					top_5[i] = person.idx()
				else:
					top_5[i] = 1000
					is_novelty = True
		candidate_idxs = [person.idx() for person in test_emb.candidates()]
		if is_novelty == False:
			top_5[-1] = 1000
			top_5[1:-1] = candidate_idxs[1:-1]
		else:
			top_5[1:] = candidate_idxs[0:-1]
		top_5s.append(top_5)
		
	
	with open(output, 'w') as f:
		f.write('image,label\n')
		for i, (test_img, top_5) in enumerate(zip(tree.test_imgs(),top_5s)):
			path = test_emb.path
			file_name = split(path)[1]
			bfile_name = splitext(file_name)[0]
			f.write(bfile_name + '.png,' + ' '.join([str(e) for e in top_5]))
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
	args= vars(ap.parse_args())

	start = time()
	name2file, emb_data = load_emb_data(args['data_dir'], vector_dir=args['ver_vector_dir'])
	data = {name: [join(args['data_dir'], name, f) for f in files] for name, files in name2file.items()}
	print('loaded data: ', time() - start)

	tree = Tree()
	for name, paths in data.items():
		_emb = emb_data[name][0]
		test_img = TestImage(paths[0], _emb)
		tree.append(test_img) 

	ide_model = IdentifyModel()
	ide_model.load_classify_model(args['model_path'])
	# ide_model.known_vector_dir(args['known_vector_dir'])
	# ide_model.set_threshold(args['threshold'])
	ide_model.set_n_top_candidate(args['k'])
	ide_model.load_idx2path(args['idx2path'])
	print('ide_model.idx2path: ', ide_model.idx2path)
	identify(tree, ide_model, args['known_vector_dir'], args['k'], args['output'], args['threshold'], args['batch_size'])


		