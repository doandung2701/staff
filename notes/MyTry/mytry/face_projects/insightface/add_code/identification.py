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
		self.classify_model = svm_classify(X, Y)

	def dump_classify_model(self, classify_model_path):
		with open(classify_model_path, 'wb') as f:
			pickle.dump(self.classify_model, f)

	def load_classify_model(self, classify_model_path):
		with open(classify_model_path, 'rb') as f:
			self.classify_model = pickle.load(f)
	
	def _classify(self, x):
		probs = self.classify_model.predict_proba([x])[0]
		idx2prob = {self.classify_model.classes_[i]:prob for i, prob in enumerate(probs)}
		return idx2prob

	def _vertificate(self, x, candidates):
		is_sames = []
		for candidate in candidates:
			imgs = get_person_images(candidate, self.idx2path)
			imgs = [cv2.resize(img, (112,112)) for img in imgs]

			vote = 0
			for img in imgs:
				x_c = self.face_model.get_feature(img)
				dist = np.sum(np.square(x-x_c))
				print('dist: ', dist)
				if dist < self.threshold:
					vote += 1
			print('vote: ', vote)
			if vote > 0:
				is_sames.append(1)
			else:
				is_sames.append(0)
		print('is_sames: ', is_sames)
		return is_sames
	
	def identify(self, x, n_top_candidate):
		# x = FaceModel.get_feature()
		idx2prob = self._classify(x)
		# pdb.set_trace()
		candidates = [e[0] for e in sorted(idx2prob.items(), key=lambda x:x[1], reverse=True)][:self.n_top_candidate]
		print('candidates: ', candidates)
		is_sames = self._vertificate(x, candidates)
		return candidates, is_sames

	@staticmethod
	def load_model(model_path):
		return IdentifyModel()

	@staticmethod
	def dump_model(ide, model_path):
		pass

