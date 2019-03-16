from __future__ import division
import os, glob, cv2, random, numpy as np
from zemcy import support_lib as sl
import sys
sys.path.append(os.path.expanduser('~/MySetting/staff/code/Librarys/'))
from image_process.affine_transform import four_point_transform
def apply_affine_transform(indir, outdir):
	print("##Apply_affine_transform function")
	indir = os.path.expanduser(indir)
	outdir = os.path.expanduser(outdir)
	if os.path.exists(outdir):
		os.system("rm -rf " + outdir)
	os.mkdir(outdir)

	for root, _, file_names in os.walk(indir):
		print('#Root:',root)
		print('#file_names: ', file_names)
		root_part_path = os.path.relpath(root, indir)
		print('#root_part_path: ', root_part_path)
		print(file_names)
		des_file_names = list(filter(lambda x: x.endswith('.txt'), file_names))
		img_file_names = [os.path.splitext(e)[0] + '.jpg' for e in des_file_names]
		des_file_paths = [os.path.join(root, e) for e in des_file_names]
		img_file_paths = [os.path.join(root, e) for e in img_file_names]
		print('ndes_file_names', len(des_file_names))
		try:
			os.mkdir(os.path.join(outdir, root_part_path))
		except: pass


		for img_file_name, img_file_path, des_file_name, des_file_path in zip(img_file_names, img_file_paths,\
								des_file_names, des_file_paths):
			print(img_file_name + ' ===? ' + des_file_name)
			img = cv2.imread(img_file_path)
			H, W, _ = img.shape
			bfile_name = os.path.splitext(des_file_name)[0]
			print('bfile_name: ', bfile_name)
			with open(des_file_path) as f:
				lines = f.readlines()
				print(lines)
				for i, line in enumerate(lines):
					print('line=', line)
					colums = line.split(',')
					pts = [[float(colums[1])*W, float(colums[5])*H], [float(colums[2])*W, float(colums[6])*H],\
							 [float(colums[3])*W,float(colums[7])*H], [float(colums[4])*W, float(colums[8])*H]]
					# pts = [[float(colums[1])*W, float(colums[2])*H], [float(colums[3])*W, float(colums[4])*H],\
					# 		 [float(colums[5])*W,float(colums[6])*H], [float(colums[7])*W, float(colums[8])*H]]
					# npts = [[p[0], p[1]] for p in [pts[2], pts[0], pts[3], pts[1]]]
					# pts = npts
					print('pts: ', pts)
					pts = np.array(pts).astype(np.float)
					print('pts: ', pts)
					lp_img = four_point_transform(img, pts.copy())
					lp_img_path = os.path.join(outdir, root_part_path, bfile_name + '_' + str(i) + '.jpg')
					print('lp_img_path: ', lp_img_path)
					print('lp_img shape: ', lp_img.shape)
					cv2.imwrite(lp_img_path, lp_img)
					# new_img = img.copy()
					# sl.draw_points(new_img, [(int(e[0]), int(e[1])) for e in list(pts)])
					# cv2.imwrite(os.path.join(outdir, root_part_path, bfile_name + '_raw_' + str(i) + '.jpg') , new_img)



if __name__=='__main__':
	import argparse
	ap = argparse.ArgumentParser()
	ap.add_argument("--indir", help="indir")
	ap.add_argument("--outdir", help="outdir")
	args= vars(ap.parse_args())
	apply_affine_transform(args["indir"], args["outdir"])