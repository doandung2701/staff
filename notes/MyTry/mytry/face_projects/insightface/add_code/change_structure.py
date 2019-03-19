import random
from os import listdir, mkdir, system
from os.path import expanduser, join, split, splitext, exists
from glob import glob


def main(indir, outdir, des_file_path):
	indir = expanduser(indir)
	outdir = expanduser(outdir)
	des_file_path = expanduser(des_file_path)

	if exists(outdir):
		system('rm -rf ' + outdir)
	system('mkdir -p ' + outdir)

	pairs = []
	with open(des_file_path) as f:
		lines = f.readlines()
		print(lines)
		for line in lines[1:]:
			colums = line.split(',')
			img_name, idx = colums[0], int(colums[1])
			pairs.append((img_name, idx))
	n_pair = len(pairs)
	print('n_pair: ', n_pair)

	idxs = set([idx for _, idx in pairs])
	idxs = sorted(idxs)

	# print('idxs: ', idxs)

	n_kpeople = len(idxs)
	print('n_kpeople: ', n_kpeople)
	assert idxs == list(range(n_kpeople))

	idx2img_names = dict()
	for idx in idxs:
		idx2img_names[idx] = []
	for img_name, idx in pairs:
		idx2img_names[idx].append(img_name)
	

	for idx in idxs:
		mkdir(join(outdir, str(idx)))
		for i, img_name in enumerate(idx2img_names[idx]):
			system('cp ' + join(indir, img_name) + ' ' + join(outdir, str(idx), '%04d' % int(i) + '.png'))


	#         actual_strg = raw_strg.split('.')[0]
	#         print('actual_strg: ', actual_strg)
	#         actual_strgs.append(actual_strg)

	# img_files = listdir(indir)
	# for img_file in img_files:
	#     assert img_file.endswith('.png')
		

	# n_people = len(person_dirs)
	# print('person_dirs: ', person_dirs)

	pairs = []
	idxs_of_person = {}

if __name__=='__main__':
	import argparse
	ap = argparse.ArgumentParser()
	ap.add_argument("--indir", help="indir")
	ap.add_argument("--outdir", help="outdir")
	ap.add_argument("--des_file_path", help="des_file_path")
	args= vars(ap.parse_args())
	main(args["indir"], args["outdir"], args["des_file_path"])
