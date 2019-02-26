from __future__ import division
import os, glob, cv2, random
from zemcy import support_lib as sl
def location_to_des(indir, outdir):
	print("##Location_to_des function")
	indir = os.path.expanduser(indir)
	outdir = os.path.expanduser(outdir)
	if os.path.exists(outdir):
		os.system("rm -rf " + outdir)
	os.mkdir(outdir)

	# fold_dirs = [os.path.join(outdir, 'fold_' + str(e)) for e in range(n_fold)]
	# for fold_dir in fold_dirs:
	# 	os.mkdir(fold_dir)

	for root, _, file_names in os.walk(indir):
		print('#Root:',root)
		print('#file_names: ', file_names)
		root_part_path = os.path.relpath(root, indir)
		print('#root_part_path: ', root_part_path)
		print(file_names)
		img_file_names = list(filter(sl.is_img_type, file_names))
		other_file_names = [x for x in file_names if x not in img_file_names]
		print('other_file_names: ', other_file_names)
		location_of_file_name = dict()
		if 'location.txt' in other_file_names:
			with open(os.path.join(root,'location.txt')) as f:
				lines = f.readlines()
				print(lines)
				for line in lines:
					print('line=', line)
					colums = line.split(' ')
					print('colums: ', colums)
					if len(colums) > 5:
						if colums[0] in img_file_names:
							img_file_path = os.path.join(root, colums[0])
							img = cv2.imread(img_file_path)
							H, W, _ = img.shape
							print('colums[1:] = ', colums[1:])
							l, t, w, h = map(sl.string_to_int,colums[2:])
							location_of_file_name[colums[0]] = [l/W, t/H, (l+w)/W, t/H, (l+w)/W, (t+h)/H, l/W, (t+h)/H]
		new_root = os.path.join(outdir, root_part_path)
		try:
			os.mkdir(new_root)
		except: pass
		for img_file_name in img_file_names:
			img_file_path = os.path.join(root, img_file_name)
			os.system('cp ' + img_file_path + ' ' + new_root)
			core_file_name = os.path.splitext(img_file_name)[0]
			print('core_file_name: ', core_file_name)
			with open(os.path.join(new_root, core_file_name + '.txt'), 'w+') as f:
				print('location_of_file_name[img_file_name] = ', location_of_file_name[img_file_name])
				location_strg = ','.join([img_file_name] + [str(e)[:8] for e in location_of_file_name[img_file_name]]) + ',,'
				print('location_strg: ', location_strg)
				f.write(location_strg)
		


if __name__=='__main__':
	import argparse
	ap = argparse.ArgumentParser()
	ap.add_argument("--indir", help="indir")
	ap.add_argument("--outdir", help="outdir")
	args= vars(ap.parse_args())
	location_to_des(args["indir"], args["outdir"])