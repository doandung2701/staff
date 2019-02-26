import os, glob, cv2, random
from zemcy import support_lib as sl
def split_data(indir, outdir, ratio=0.1):
	print("##Split data function")
	indir = os.path.expanduser(indir)
	outdir = os.path.expanduser(outdir)
	if os.path.exists(outdir):
		os.system("rm -rf " + outdir)
	os.mkdir(outdir)
	test_dir, other_dir = os.path.join(outdir, 'test'), os.path.join(outdir, 'other')
	os.mkdir(test_dir)
	os.mkdir(other_dir)

	for root, _, file_names in os.walk(indir):
		print('#Root:',root)
		print('#file_names: ', file_names)
		root_part_path = os.path.relpath(root, indir)
		print('#root_part_path: ', root_part_path)
		print(file_names)
		img_file_names = list(filter(sl.is_img_type, file_names))
		other_file_paths = [os.path.join(root, e) for e in [x for x in file_names if x not in img_file_names]]
		print('nimg_file_names', len(img_file_names))
		img_file_paths, des_file_paths = [], []
		for img_file_name in img_file_names:
			core_file_name_ = os.path.splitext(img_file_name)[0]
			print('core_file_name_:', core_file_name_)
			img_file_paths.append(os.path.join(root, img_file_name))
			des_file_path = os.path.join(root, core_file_name_ + '.txt')
			if os.path.exists(des_file_path):
				des_file_paths.append(des_file_path)
				other_file_paths.remove(des_file_path)
			else:
				print('Skip ', des_file_path)
		n_des_file = len(des_file_paths)
		if n_des_file == 0:
			des_file_paths = ['nope']*len(img_file_names)
		pairs = list(zip(img_file_paths, des_file_paths))
		print('pairs: ', pairs)
		random.shuffle(pairs)
		n_img = len(pairs)
		n_test_img = max(int(ratio*n_img), 1)
		print('#n_img , n_test_img: ', n_img, n_test_img)
		test_pairs, other_pairs = pairs[:n_test_img], pairs[n_test_img:]

		def write_pairs(folder, pairs):
			for img_file_path, des_file_path in pairs:
				os.system('cp ' + img_file_path + ' ' + folder)
				os.system('cp ' + des_file_path + ' ' + folder)
		
		test_current_dir, other_current_dir = os.path.join(test_dir,root_part_path), os.path.join(other_dir,root_part_path)
		print('test_current_dir: ', test_current_dir)
		try:
			os.mkdir(test_current_dir)
			os.mkdir(other_current_dir)
		except: pass
		write_pairs(test_current_dir, test_pairs)
		write_pairs(other_current_dir, other_pairs)
		for file_path in other_file_paths:
			os.system('cp ' + file_path + ' ' + test_current_dir)
			os.system('cp ' + file_path + ' ' + other_current_dir)


if __name__=='__main__':
	import argparse
	ap = argparse.ArgumentParser()
	ap.add_argument("--indir", help="indir")
	ap.add_argument("--outdir", help="outdir")
	args= vars(ap.parse_args())
	split_data(args["indir"], args["outdir"])