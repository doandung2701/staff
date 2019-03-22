import random
from os import listdir, mkdir, system
from os.path import expanduser, join, split, splitext, exists
from glob import glob

def file_idx(file_name):
    bfile_name = splitext(file_name)[0]
    es = bfile_name.split('_')
    idx = es[-1]
    return idx

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
		idx2img_names[idx] = [img_name]

	final_idxs = list(range(n_kpeople + n_test_file))

	for idx in final_idxs:
		idx_dir = indir if idx < n_kpeople else testdir
		mkdir(join(outdir, str(idx)))
		for i, img_name in enumerate(idx2img_names[idx]):
			system('cp ' + join(idx_dir, img_name) + ' ' + join(outdir, str(idx), str(idx) + '_%04d' % int(i) + '.jpg'))


	person_dirs = [str(idx) for idx in final_idxs] 
	n_people = n_kpeople + n_test_file
	pairs = []
	idxs_of_person = {}
	for person_dir in person_dirs:
		_idxs = []
		person_files = listdir(join(outdir, person_dir))
		print('person_files: ', person_files)
		n_path = len(person_files)
		for i in range(n_path):
			file_name1 = person_files[i]
			idx1 = file_idx(file_name1)
			_idxs.append(idx1)
			# print('idx: ', idx1)
			# for j in range(i+1, n_path):
			# 	file_name2 = person_files[j]
			# 	idx2 = file_idx(file_name2)
				# print('idx: ', idx2)
				# pairs.append((person_dir, idx1, idx2))
		idxs_of_person[person_dir] = _idxs
	



	for j in range(n_kpeople, n_people):
		person_dir1 = person_dirs[j]
		idx1 = idxs_of_person[person_dir1][0]
		for i in range(n_kpeople):
			person_dir2 = person_dirs[i]
			print(j, i)
			print(person_dir1, person_dir2)
			for idx2 in idxs_of_person[person_dir2]:
				pairs.append((person_dir1, idx1, person_dir2, idx2))
	print('pairs: ', pairs)
	print('len(pairs): ', len(pairs))
	with open(join(outdir, 'pairs.txt'), 'w') as f:
		f.write('Hello\n')
		for i, pair in enumerate(pairs):
			f.write(' '.join(pair))
			if i < len(pairs) - 1:
				f.write('\n')
	
		


if __name__=='__main__':
	import argparse
	ap = argparse.ArgumentParser()
	ap.add_argument("--indir", help="indir")
	ap.add_argument("--testdir", help="testdir")
	ap.add_argument("--outdir", help="outdir")
	ap.add_argument("--des_file_path", help="des_file_path")
	args= vars(ap.parse_args())
	main(args["indir"], args["testdir"], args["outdir"], args["des_file_path"])
