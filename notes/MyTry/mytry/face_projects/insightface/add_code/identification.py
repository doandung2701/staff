import sys
sys.path.append('./deploy')
from utils import svm_classify, get_person_images
import pickle
from random import shuffle
import numpy as np
class IdentifyModel:
	def __init__(self):
		pass

	def set_threshold(self,threshold):
		self.threshold = threshold
	
	def set_n_top_candidate(self,n_top_candidate):
		self.n_top_candidate = n_top_candidate

	def load_idx2path(self, path):
		with open(path, 'rb') as f:
			self.idx2path = pickle.load(f)
	
	def fit(self, data):
		print('data: ', data)
		X, Y = [], []
		for idx, embs in data.items():
			for emb in embs:
				X.append(emb)
				Y.append(idx)
		pairs = list(zip(X, Y))
		shuffle(pairs)
		print('pairs: ', pairs)
		X, Y = zip(*pairs)
		self.classify_model = svm_classify(X, Y)
	
	def _classify(self, x):
		probs = self.classify_model.predict_proba([x])[0]
		return probs

	def _vertificate(self, x, candidates):
		idx = -1
		for i, candidate in enumerate(candidates):
			imgs = get_person_images(candidate, self.idx2path)
			vote = 0
			for img in imgs:
				x_c = FaceModel.get_feature(img)
				dist = np.sum(np.square(x-x_c))
				if dist < self.threshold:
					vote += 1
			if vote > len(imgs)//2:
				idx = i
		return idx
	
	def identify(self, x, n_top_candidate):
		# x = FaceModel.get_feature()
		probs = self._classify(x)
		candidates = [e[0] for e in sorted(enumerate(probs), key=lambda x:x[1])][:self.n_top_candidate]
		ide = self._vertificate(x, candidates)
		return ide

	@staticmethod
	def load_model(model_path):
		return IdentifyModel()

	@staticmethod
	def dump_model(ide, model_path):
		pass

