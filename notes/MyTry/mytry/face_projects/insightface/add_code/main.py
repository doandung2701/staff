from os import mkdir
from os.path import split, splitext, join, exists
from identification import IdentifyModel
from data import load_data, get_config
from face_embedding import FaceModel
import cv2, pickle

def identify(data, ide_model, vector_dir, k):
	args = get_config()
	face_model = FaceModel(args)
	labels = []
	for name, paths in data.items():
		path = paths[0]
		file_name = split(path)[1]
		print('file_name: ', file_name)
		bfile_name = splitext(file_name)[0]
		emb_path = join(vector_dir, name, bfile_name + '.pkl')
		if not exists(join(vector_dir, name)):
			mkdir(join(vector_dir, name))
		if not exists(emb_path):
			_img = cv2.imread(path)
			_img = cv2.resize(_img, (112,112))
			_emb = face_model.get_feature(_img)
			with open(emb_path, 'wb') as f:
				pickle.dump(emb_path, f)
		else:
			with open(emb_path, 'rb') as f:
				_emb = pickle.load(f)
		_label = ide_model.identify(_emb, k)
		if _label == -1:
			_label = 1000
		labels.append(_label)
	
	# write csv file

if __name__=='__main__':
	import argparse
	ap = argparse.ArgumentParser()
	ap.add_argument("--data-dir", help="data-dir")
	ap.add_argument("--vector-dir", help="vector_dir")
	ap.add_argument("--model-path", help="model-path")
	ap.add_argument("--idx2path", help="idx2path")
	ap.add_argument("--threshold", type=float,help="threshold")
	ap.add_argument("--k", type=int, help="n_top_candidate")
	args= vars(ap.parse_args())

	name2file = load_data(args['data_dir'])
	data = {name: [join(args['data_dir'], name, f) for f in files] for name, files in name2file.items()}
	
	with open(args['model_path'], 'rb') as f:
		ide_model = pickle.load(f)

	ide_model.set_threshold(args['threshold'])
	ide_model.set_n_top_candidate(args['k'])
	ide_model.load_idx2path(args['idx2path'])
	print('ide_model.idx2path: ', ide_model.idx2path)
	identify(data, ide_model, args['vector_dir'], args['k'])


		
