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
# import bottleneck as bn

def identify(tree, ide_model, known_vector_dir, k, output, threshold, batch_size, tree_path):
	print('Identifing!')
	if exists(tree_path):
		with open(tree_path, 'rb') as f:
			tree = pickle.load(f)
	else:
		n_test_img = tree.len()
		tree_candidates = []
		# pdb.set_trace()
		n_batch = get_batch_number(n_test_img, batch_size)
		start = time()
		for batch_idx in range(n_batch):
			s, e = get_slice_of_batch(n_test_img, batch_size, batch_idx)
			_batch = tree.test_imgs()[s:e]
			_batch = [e.emb() for e in _batch]
			bstart = time()
			_batch_candidates = ide_model.batch_candidates(_batch)
			print(batch_idx, time() - bstart)
			tree_candidates.extend(_batch_candidates)
		tree.paste_candidate_idx(tree_candidates)
		print('Get candidate done! ', time() - start)

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
					name = split(img_dir)[1]
					emb_path = join(known_vector_dir, name, bfile_name + '.pkl')
					with open(emb_path, 'rb') as f:
						_emb = pickle.load(f)
					img = Image(path, _emb)
					person.append(img)
					dist = np.sum(np.square(test_emb-img.emb()))
					person_dist.append(dist)
				test_img.append_dist(person_dist)
		print('Cal dist done! ', time() - start)

		if not exists(split(tree_path)[0]):
			system('mkdir -p ' + split(tree_path)[0])
		with open(tree_path, 'wb') as f:
			pickle.dump(tree, f)

	# top_5s = []
	# test_imgs = sorted(tree.test_imgs(), key=lambda test_img:min(test_img.dists()), reverse=True)
	# for test_img in test_imgs:
	#     pairs = list(zip(test_img.candidates(), test_img.dists()))
	#     pairs = sorted(pairs, key x: min(x[1]), reverse=True)
	#     for person, person_dist in zip(pairs):
	#         if min(person_dist) < threshold:
	#             top_5s.append(person.idx())
				


	top_5s = []
	change_c = 0
	for test_img in tree.test_imgs():
		ti_candidates, ti_dists = test_img.candidates(), test_img.dists()

		pairs = list(zip(ti_candidates, ti_dists))
		sorted_pairs = sorted(pairs, key= lambda x: min(x[1]))
		ti_candidates, ti_dists = zip(*sorted_pairs)
		if [person.idx() for person in ti_candidates] != [person.idx() for person in test_img.candidates()]:
			change_c += 1
		
		is_sames = []
		for person, person_dist in zip(ti_candidates,ti_dists):
			print('person_dist: ', person_dist)
			print('vote: ')
			_embs = np.array([img.emb() for img in person.imgs])
			mean_emb = np.mean(_embs, axis=0)
			# bn.median(sequence_mutil_probability, axis=0)
			# pdb.set_trace()
			dist = np.sum(np.square(test_emb-mean_emb))
			if dist < threshold:
				is_sames.append(1)
			else:
				is_sames.append(0)
			print()
		print('is_sames: ', is_sames)

		top_5 = [0] * k
		is_novelty = False
		for i, (person, is_same) in enumerate(zip(ti_candidates, is_sames)):
			if i == 0:
				if is_same == 1:
					top_5[i] = person.idx()
				else:
					top_5[i] = 1000
					is_novelty = True
		candidate_idxs = [person.idx() for person in ti_candidates]
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

	print('change_c: ', change_c)
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
	identify(tree, ide_model, args['known_vector_dir'], args['k'], args['output'], args['threshold'], args['batch_size'], args['tree_path'])


		
