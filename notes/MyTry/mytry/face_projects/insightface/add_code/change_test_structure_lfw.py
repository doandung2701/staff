import random
from os import listdir, mkdir, system
from os.path import expanduser, join, split, splitext, exists
from glob import glob


def main(indir, testdir, outdir, des_file_path):
	indir = expanduser(indir)
	testdir = expanduser(testdir)
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

	img_names = listdir(testdir)
	n_test_file = len(img_names)
	test_idxs = list(range(n_kpeople,n_kpeople + n_test_file))
	for img_name, idx in zip(img_names, test_idxs):
		assert img_name.endswith('png')
		bimg_name = splitext(img_name)[0]
		idx2img_names[idx] = [bimg_name]



	for idx in idxs:
		mkdir(join(outdir, str(idx)))
		for i, img_name in enumerate(idx2img_names[idx]):
			system('cp ' + join(indir, img_name) + ' ' + join(outdir, str(idx), '%04d' % int(i) + '.png'))


	
		


if __name__=='__main__':
	import argparse
	ap = argparse.ArgumentParser()
	ap.add_argument("--indir", help="indir")
	ap.add_argument("--testdir", help="testdir")
	ap.add_argument("--outdir", help="outdir")
	ap.add_argument("--des_file_path", help="des_file_path")
	args= vars(ap.parse_args())
	main(args["indir"], args["testdir"], args["outdir"], args["des_file_path"])
