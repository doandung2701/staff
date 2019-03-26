from __future__ import print_function
import pickle
from os import system
from os.path import join, exists, split, splitext
from data import load_emb_data
from identification import IdentifyModel
import numpy as np
	

if __name__=='__main__':
	import argparse
	ap = argparse.ArgumentParser()
	ap.add_argument("--data-dir", help="data-dir")
	ap.add_argument("--output-path", help="output-path")
	ap.add_argument("--vector-dir", help="vector-dir")
	ap.add_argument("--threshold", type=float, help="threshold")
	args= vars(ap.parse_args())

	name2file, name2emb = load_emb_data(args['data_dir'], vector_dir=args['vector_dir'])
	idx2path = {name: [join(args['data_dir'], name, f) for f in files] for name, files in name2file.items()}

	name2max_dist = {}
	name2dist = {}
	for name, embs in name2emb.items():
		n_f = len(embs)
		dists = []
		_pairs = []
		for i in range(n_f-1):
			for j in range(i+1, n_f):
				dist = np.sum(np.square(embs[i]-embs[j]))
				dists.append(dist)
				_pairs.append((name2file[name][i], name2file[name][j]))
		print('dists: ', dists)
		if len(dists) == 0:
			max_dist = 0
		else:
			max_dist = max(dists)
		name2max_dist[name] = max_dist
		name2dist[name] = list(zip(dists, _pairs))
	
	pairs = sorted(name2max_dist.items(), key=lambda x: x[1])

	import matplotlib
	matplotlib.use('Agg')
	import matplotlib.pylab as plt
	x, y = zip(*pairs) # unpack a list of pairs into two tuples
	plt.plot(x, y)
	output_path = args['output_path']
	if not exists(split(output_path)[0]):
		system('mkdir -p ' + split(output_path)[0])
	plt.savefig(output_path)
	plt.close()

	name2n = {name: len(file_names) for name, file_names in name2file.items()}
	file_numbers = set(name2n.values())
	file_number2n = {}
	for file_number in file_numbers:
		file_number2n[file_number] = 0
		
	for name, n in name2n.items():
		file_number2n[n] += 1
	
	x, y = zip(*file_number2n.items()) # unpack a list of pairs into two tuples
	plt.plot(x, y)
	output_path = args['output_path']
	output_dir = split(output_path)[0]
	if not exists(output_dir):
		system('mkdir -p ' + output_dir)
	plt.savefig(join(output_dir, 'file_number2n.png'))
	print('file_number2n: ', file_number2n)


	print('\n\n\n\n\n')

	warn_names = []
	for name, max_dist in pairs[::-1]:
		if max_dist > args['threshold']:
			warn_names.append(name)
	delete_statis = 0
	warn_statis = 0
	for name in warn_names:
		dist_pairs = sorted(name2dist[name], key= lambda x: x[0], reverse=True)
		dist_pairs = list(filter(lambda x: x[0] > args['threshold'], dist_pairs))
		_, pairs = zip(*dist_pairs) 
		l,r = zip(*pairs)
		imgs = set(l+r)
		img2n = {}
		img2dist = {}
		for img in imgs:
			img2n[img] = 0
			img2dist[img] = []
		for dist_pair in dist_pairs:
			_l, _r = dist_pair[1]
			img2n[_l] += 1
			img2n[_r] += 1
			img2dist[_l].append((dist_pair[0], _r))
			img2dist[_r].append((dist_pair[0], _l))
		print('name: ', name)
		imgs = sorted(imgs, key=lambda x:img2n[x], reverse=True)
		deletes = []
		for img in imgs:
			if len(img2dist[img]) == len(name2file[name]) - 1:
				deletes.append(img)
				delete_statis += 1
				print('Delete: ' + img + ' >> ' + ', '.join([str(dist) for dist, other in img2dist[img]]))
			else:
				_warn_dist = []
				for dist, other in img2dist[img]:
					if other not in deletes:
						_warn_dist.append((dist, other))
				if _warn_dist:
					d, o = zip(*_warn_dist)
					warn_statis += 1
					if max(d) > args['threshold'] + 0.2:
						prefix = '0.2>>>>>>>>>>>'
					if max(d) > args['threshold'] + 0.4:
						prefix = '0.4>>>>>>>>'
					if max(d) > args['threshold'] + 0.6:
						prefix = '0.6>>>>>>'
					if max(d) > args['threshold'] + 0.8:
						prefix = '0.8>>>>'
					if max(d) > args['threshold'] + 0.4:
						prefix = ''
					else:
						prefix = '>>>>>>>>>>>>>>>>>>>>>>>>>>'
					print('Warn: ' + prefix + img + ' >> ' + ', '.join([str(e) for e in d]) + ' b>> ' + ', '.join(o))
		
	print('n_warn_name: ', len(warn_names))
	print('n_delete_img: ', delete_statis)
	print('n_warn_img: ', warn_statis)
			# print(img + ' :' + str(img2dist[img]) + should_delete)




	# log_strs = [str(name) + ': ' + str(sorted(name2dist[name], key= lambda x: x[0], reverse=True)) for name in warn_names]
	# for log_str in log_strs:
	# 	print(log_str)
			
	




	

	