import pickle
from os.path import join
from data import load_data
from identification import IdentifyModel
	
# def train(emb_data):
# 	ide = IdentifyModel()
# 	ide.fit(emb_data)
# 	return ide

if __name__=='__main__':
	import argparse
	ap = argparse.ArgumentParser()
	ap.add_argument("--data-dir", help="data-dir")
	ap.add_argument("--model-path", help="model-path")
	ap.add_argument("--idx2path", help="idx2path")
	ap.add_argument("--vector-dir", help="vector_dir")
	ap.add_argument("--ver-vector-dir", help="ver-vector_dir")
	args= vars(ap.parse_args())

	from add_image_main import load_emb_from_idx2path
	with open(args['idx2path'], 'rb') as f:
		idx2path = pickle.load(f)
	name2emb = load_emb_from_idx2path(args['data_dir'],idx2path, vector_dir=args['vector_dir'], ver_vector_dir=args['ver_vector_dir'])
	# idx2path = {name: [join(args['data_dir'], name, f) for f in files] for name, files in name2file.items()}
	emb_data = name2emb
	# with open(args['idx2path'], 'wb') as f:
	# 	pickle.dump(idx2path, f)

	ide = IdentifyModel()
	ide.fit(emb_data)
	ide.dump_classify_model(args['model_path'])

	