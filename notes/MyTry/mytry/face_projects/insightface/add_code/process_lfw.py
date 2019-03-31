import random
from os import listdir
from os.path import expanduser, join, split, splitext
from glob import glob

def file_idx(file_name):
	bfile_name = splitext(file_name)[0]
	es = bfile_name.split('_')
	idx = es[-1]
	return idx


def main(indir, outdir, npair):
	indir = expanduser(indir)
	outdir = expanduser(outdir)
	person_dirs = listdir(indir)
	n_people = len(person_dirs)
	print('person_dirs: ', person_dirs)

	pairs = []
	idxs_of_person = {}
	for person_dir in person_dirs:
		_idxs = []
		person_files = listdir(join(indir, person_dir))
		print('person_files: ', person_files)
		n_path = len(person_files)
		for i in range(n_path):
			file_name1 = person_files[i]
			idx1 = file_idx(file_name1)
			_idxs.append(idx1)
			# print('idx: ', idx1)
			for j in range(i+1, n_path):
				file_name2 = person_files[j]
				idx2 = file_idx(file_name2)
				# print('idx: ', idx2)
				pairs.append((person_dir, idx1, idx2))
		idxs_of_person[person_dir] = _idxs
	same_pair_number = len(pairs)
	final_same_pair_number = min(same_pair_number, npair//2)
	
	for i in range(n_people):
		person_dir1 = person_dirs[i]
		for idx1 in idxs_of_person[person_dir1]:
			for j in range(i+1, n_people):
				person_dir2 = person_dirs[j]
				print(i, j)
				print(person_dir1, person_dir2)
				for idx2 in idxs_of_person[person_dir2]:
					pairs.append((person_dir1, idx1, person_dir2, idx2))
	print('pairs: ', pairs)
	final_pairs = random.sample(pairs[:same_pair_number], final_same_pair_number) +\
		 random.sample(pairs[same_pair_number:],npair - final_same_pair_number)
	print('len(final_pairs): ', len(final_pairs))
	with open(join(outdir, 'pairs.txt'), 'w') as f:
		f.write('Hello\n')
		for i, pair in enumerate(final_pairs):
			f.write(' '.join(pair))
			if i < len(final_pairs) - 1:
				f.write('\n')
	



if __name__=='__main__':
	import argparse
	ap = argparse.ArgumentParser()
	ap.add_argument("--indir", help="indir")
	ap.add_argument("--outdir", help="outdir")
	ap.add_argument("--npair", type=int, help="npair")
	args= vars(ap.parse_args())
	main(args["indir"], args["outdir"], args["npair"])
