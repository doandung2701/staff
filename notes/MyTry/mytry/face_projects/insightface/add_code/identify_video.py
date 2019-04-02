import cv2
from os import listdir, mkdir
from os.path import expanduser, join, split, splitext, exists, isfile
from zemcy.videostream import QueuedStream
from mutil_face_model import FaceModel
import nface_embedding as fe
from identification import IdentifyModel, Image, TestImage, Person, Tree
from easydict import EasyDict as edict
import pickle
import numpy as np
from datetime import datetime as dt
from random import randint

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

def get_time_id():
    time_string = str(dt.now())
    cvt_time_string = time_string.split('.')[0].replace(' ', '_').replace(':', '-')
    time_id = cvt_time_string + '_' + str(randint(0, 100000))
    return time_id

def main(url, ide_model, args):
	model_args = get_config()
	fmodel = FaceModel(model_args)
	limit_fmodel = fe.FaceModel(model_args)

	# video = QueuedStream(url, queueSize=8, fps=24)
	# video.start()
	video = cv2.VideoCapture(url)
	ret, frame = video.read()
	if not ret:
		print 'Camera is not open!'
		sys.exit(1)
	print('Camera Resolution: ', frame.shape[1::-1])

	fourcc = cv2.VideoWriter_fourcc(*'mp4v')
	out = cv2.VideoWriter('output.mp4',fourcc, 24.0, frame.shape[1::-1])
	# idx2name = {0:'cuongvm', 1:'dathv', 2:'doanhnt', 3:'dunglt', 4:'tuanbd'}
	# name2idx = {'cuongvm': 0, 'dathv': 1, 'doanhnt': 2, 'dunglt':3, 'tuanbd': 4}
	idx2embs = {}
	for idx, paths in ide_model.idx2path.items():
		_embs = []
		for path in paths:
			root_dir, file_name = split(path)
			name = split(root_dir)[1]
			bfile_name = splitext(file_name)[0]
			emb_path = join(args['known_vector_dir'], name, bfile_name + '.pkl')
			if not exists(emb_path):
				if not exists(join(vector_dir, name)):
					mkdir(join(vector_dir, name))
				_img = cv2.imread(path)
				_, k_emb = limit_fmodel.get_feature(_img)
				with open(emb_path, 'wb') as f:
					pickle.dump(k_emb, f)
			else:
				with open(emb_path, 'rb') as f:
					k_emb = pickle.load(f)
			_embs.append(k_emb)
		idx2embs[idx] = _embs
	uidx2embs = {}
	u_ide = IdentifyModel()

	while video.isOpened():
		ret, frame = video.read()
		if not ret:
			print 'Camera is not open!'
			break
		out_frame = frame.copy()
		
		aligneds, boxs = fmodel.get_input(frame)
		_embs = fmodel.mutil_get_feature(aligneds)
		batch_candidates = ide_model.batch_candidates(_embs)
		predicts = [candidates[0] for candidates in batch_candidates]

		for box, predict, _emb in zip(boxs, predicts, _embs):
			# paths = ide_model.idx2path[predict]
			k_embs = idx2embs[predict]
			is_same = False
			for k_emb in k_embs:
				dist = np.sum(np.square(_emb-k_emb))
				if dist < args['threshold']:
					is_same = True
					break
			
			if not is_same:
				u_is_same = False
				if len(uidx2embs.items()) > 1:
					u_batch_candidates = u_ide.batch_candidates([_emb])
					u_predict = [candidates[0] for candidates in u_batch_candidates][0]
					u_embs = uidx2embs[u_predict]
					for u_emb in u_embs:
						dist = np.sum(np.square(_emb-u_emb))
						if dist < args['threshold'] + 0.2:
							u_is_same = True
							u_predict = uidx
							if len(uidx2embs[uidx]) < 5:
								uidx2embs[uidx].append(_emb)
							break
				if not u_is_same:
					# n_udix = get_time_id()
					n_udix = str(len(uidx2embs.items()))
					uidx2embs[n_udix] = [_emb]
					if len(uidx2embs.items()) > 1:
						u_ide.fit(uidx2embs)
			
			out_strg = predict if is_same else ('Unk:' + u_predict if u_is_same else '')

			l, t, r, b = int(box[0]), int(box[1]), int(box[2]), int(box[3])
			cv2.rectangle(out_frame, (l,t), (r, b), (0,255,0), 1)
			cv2.putText(out_frame, out_strg, (l, t - 5), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
		out.write(out_frame)
	video.release()
	out.release()
		

if __name__=='__main__':
	import argparse
	ap = argparse.ArgumentParser()
	ap.add_argument("--url", help="url")
	ap.add_argument("--model-path", help="model-path")
	ap.add_argument("--idx2path", help="idx2path")
	ap.add_argument("--output", help="output")
	# ap.add_argument("--batch-size", type=int, help="batch-size")
	ap.add_argument("--k", type=int, help="n_top_candidate")
	ap.add_argument("--known-vector-dir", help="known-vector-dir")
	ap.add_argument("--threshold", type=float, help="threshold")


	args= vars(ap.parse_args())
	ide_model = IdentifyModel()
	ide_model.load_classify_model(args['model_path'])
	ide_model.set_n_top_candidate(args['k'])
	ide_model.load_idx2path(args['idx2path'])
	print('ide_model.idx2path: ', ide_model.idx2path)
	main(args['url'], ide_model, args)
