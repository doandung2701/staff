from __future__ import division
import os, glob, cv2, random
def edit_des_file(indir, preddir):
	print("##Evaluate function")
	indir = os.path.expanduser(indir)
	preddir = os.path.expanduser(preddir)

	for root, _, file_names in os.walk(indir):
		print('#Root:',root)
		print('#file_names: ', file_names)
		root_part_path = os.path.relpath(root, indir)
		print('#root_part_path: ', root_part_path)
		print(file_names)
		des_file_names = list(filter(lambda x: x.endswith('.txt'), file_names))
		des_file_paths = [os.path.join(root, e) for e in des_file_names]
		print('ndes_file_names', len(des_file_names))
		pred_file_path = os.path.join(preddir, root_part_path, 'results.csv')
		pred_strgs_of_img = dict()
		with open(pred_file_path) as f:
			lines = f.readlines()
			print(lines)
			for line in lines:
				print('line=', line)
				colums = [e.rstrip() for e in line.split(',')]
				print('colums: ', colums)
				# if len(colums) > 1:
				pred_strgs_of_img[colums[0]] = colums[1:]
				# else:
				# 	pred_strgs_of_img[colums[0]] = ['']
				print('pred_strgs_of_img[colums[0]]: ', pred_strgs_of_img[colums[0]])
		print('pred_strgs_of_img: ', pred_strgs_of_img)
		correct_count = 0
		n_lp = 0
		false_reports = []
		for des_file_name, des_file_path in zip(des_file_names, des_file_paths):
			des_bfile_name = os.path.splitext(des_file_name)[0]
			print('des_bfile_name: ', des_bfile_name)
			with open(des_file_path) as f:
				lines = f.readlines()
				print(lines)
				# actual_strgs = []
				for line in lines:
					print('line=', line)
					colums = line.split(',')
					raw_strg = colums[9]
					actual_strg = raw_strg.split('.')[0]
					# actual_strgs.append(actual_strg)
					if actual_strg in pred_strgs_of_img[des_bfile_name]:
						correct_count += 1
						print(actual_strg + ' in ' + str(pred_strgs_of_img[des_bfile_name]))
					else:
						false_reports.append(actual_strg + ' not in ' + str(pred_strgs_of_img[des_bfile_name]))
					n_lp += 1
		acc = correct_count/n_lp
		print('acc = ', acc)
		print('false_report: ')
		for false_report in false_reports:
			print(false_report)
				


if __name__=='__main__':
	import argparse
	ap = argparse.ArgumentParser()
	ap.add_argument("--indir", help="indir")
	ap.add_argument("--preddir", help="preddir")
	args= vars(ap.parse_args())
	edit_des_file(args["indir"], args["preddir"])