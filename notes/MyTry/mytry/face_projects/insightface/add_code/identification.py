import sys
sys.path.append('./deploy')
from utils import svm_classify, get_person_images
import pickle
from random import shuffle
import numpy as np
import cv2
from data import get_config
from nface_embedding import FaceModel
import pdb

class Image(object):
	def __init__(self, path=None, emb=None):
		self._path = path
		self._emb = emb

	def emb(self):
		return self._emb

	def path(self):
		return self._path

class Person:
	def __init__(self, idx):
		self._idx = idx
		self._imgs = []
	
	def imgs(self):
		return self._imgs
	
	def append(self, img):
		self._imgs.append(img)
	
	def idx(self):
		return self._idx

class TestImage(Image):
	def __init__(self, path, emb=None):
		super(self.__class__, self).__init__(path, emb)
		self._candidates = []
		self._dists = []
	
	def candidates(self):
		return self._candidates

	def append_dist(self, dist):
		self._dists.append(dist)

	def append(self, person):
		self._candidates.append(person)

	def dists(self):
		return self._dists

class Tree:
	def __init__(self):
		self._test_imgs = []

	def append(self, test_img):
		self._test_imgs.append(test_img)
	
	def test_imgs(self):
		return self._test_imgs

	def len(self):
		return len(self._test_imgs)
	
	def get_paths(self):
		paths = []
		for test_img in self._test_imgs:
			for person in test_img.candidates():
				for img in person.imgs():
					paths.append(img.path)
		return paths
	
	def paste_emb(self, embs):
		emb_iter = iter(embs)
		for test_img in self._test_imgs:
			for person in test_img.candidates():
				for img in person.imgs():
					img.emb = next(emb_iter)
	
	def paste_candidate_idx(self, candidate_idxs):
		iter_candidate_idx = iter(candidate_idxs)
		for test_img in self._test_imgs:
			candidate_idx = next(iter_candidate_idx)
			for idx in candidate_idx:
				person = Person(idx)
				test_img.append(person)

				


class IdentifyModel:
	def __init__(self):
		self.args = get_config()
		self.face_model = FaceModel(self.args)

	def set_threshold(self,threshold):
		self.threshold = threshold
	
	def set_n_top_candidate(self,n_top_candidate):
		self.n_top_candidate = n_top_candidate

	def load_idx2path(self, path):
		with open(path, 'rb') as f:
			self.idx2path = pickle.load(f)
	
	def fit(self, data):
		print('len(data.items()): ', len(data.items()))
		X, Y = [], []
		for idx, embs in data.items():
			for emb in embs:
				X.append(emb)
				Y.append(idx)
		pairs = list(zip(X, Y))
		shuffle(pairs)
		# print('pairs: ', pairs)
		X, Y = zip(*pairs)
		print('len(X), len(Y): ', len(X), len(Y))
		if len(X) > len(data.items())*2:
			self.classify_model = svm_classify(X, Y)
		else:
			from sklearn import svm
			clf = svm.SVC(gamma='scale')
			clf.fit(X, Y)
			self.classify_model = clf

	def dump_classify_model(self, classify_model_path):
		with open(classify_model_path, 'wb') as f:
			pickle.dump(self.classify_model, f)

	def load_classify_model(self, classify_model_path):
		with open(classify_model_path, 'rb') as f:
			self.classify_model = pickle.load(f)
	
	def _classify_batch(self, batch):
		batch_probs = self.classify_model.decision_function(batch)
		try:
			batch_idx2prob = [{self.classify_model.classes_[i]:prob for i, prob in enumerate(probs)} for probs in batch_probs]
		except:
			max_idxs = self.classify_model.predict(batch)
			batch_idx2prob = [{l:1 if l == max_idx else 0  for l in self.classify_model.classes_} for max_idx in max_idxs]
			# pdb.set_trace()
		return batch_idx2prob

	def batch_candidates(self, batch):
		batch_idx2prob = self._classify_batch(batch)
		batch_candidates = []
		for idx2prob in batch_idx2prob:
			_candidates = [e[0] for e in sorted(idx2prob.items(), key=lambda x:x[1], reverse=True)][:self.n_top_candidate]
			batch_candidates.append(_candidates)
		return batch_candidates
	



	# def identify_batch(self, batch):
	# 	batch_idx2prob = self._classify_batch(batch)
		
	# 	path_tree = []
	# 	for candidates in batch_candidates:
	# 		path_tree.append([[self.idx2path[str(candidate)]] for candidate in candidates])
	# 	path2
	# 	dist_tree = []
	# 	for candidates in path_tree:
	# 		for _paths in candidates:
	# 			for _path in _paths:


	# def _classify(self, x):
	# 	probs = self.classify_model.decision_function([x])[0]
	# 	idx2prob = {self.classify_model.classes_[i]:prob for i, prob in enumerate(probs)}
	# 	return idx2prob
	


	# def _cal_dist(self, x, candidates):
	# 	dists = []
	# 	for candidate in candidates:
	# 		imgs = get_person_images(candidate, self.idx2path)
	# 		imgs = [cv2.resize(img, (112,112)) for img in imgs]
	# 		person_dist = []
	# 		for img in imgs:
	# 			x_c = self.face_model.get_feature(img)
	# 			dist = np.sum(np.square(x-x_c))
	# 			print('dist: ', dist)
	# 			person_dist.append(dist)
	# 		dists.append(person_dist)
	# 	return dists

	# def _vertificate(self, x, candidates):
	# 	# pdb.set_trace()
	# 	is_sames = []
	# 	dists = self._cal_dist(x, candidates)
	# 	for person_dist in dists:
	# 		vote = 0
	# 		for dist in person_dist:
	# 			if dist < self.threshold:
	# 				vote += 1
	# 		print('vote: ', vote)
	# 		if vote > 0:
	# 			is_sames.append(1)
	# 		else:
	# 			is_sames.append(0)
	# 	print('is_sames: ', is_sames)
	# 	return is_sames
	
	# def identify(self, x, n_top_candidate):
	# 	# x = FaceModel.get_feature()
	# 	idx2prob = self._classify(x)
	# 	# pdb.set_trace()
	# 	candidates = [e[0] for e in sorted(idx2prob.items(), key=lambda x:x[1], reverse=True)][:self.n_top_candidate]
	# 	print('candidates: ', candidates)
	# 	dists = self._cal_dist(x, candidates)
	# 	return candidates, dists

	# @staticmethod
	# def load_model(model_path):
	# 	return IdentifyModel()

	# @staticmethod
	# def dump_model(ide, model_path):
	# 	pass

