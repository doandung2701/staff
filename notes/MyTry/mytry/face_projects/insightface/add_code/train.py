import pickle
from os.path import join
from data import load_emb_data
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
	args= vars(ap.parse_args())

	name2file, name2emb = load_emb_data(args['data_dir'], vector_dir=args['vector_dir'], force=True)
	idx2path = {name: [join(args['data_dir'], name, f) for f in files] for name, files in name2file.items()}
	emb_data = name2emb
	with open(args['idx2path'], 'wb') as f:
		pickle.dump(idx2path, f)

	ide = IdentifyModel()
	ide.fit(emb_data)
	ide.dump_classify_model(args['model_path'])

	