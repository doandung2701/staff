from __future__ import division
import os, glob, cv2, random
import pdb
def main(indir, preddir, name_file):
	print("##Evaluate function")
	indir = os.path.expanduser(indir)
	preddir = os.path.expanduser(preddir)

	for root, _, file_names in os.walk(indir):
		print('#Root:',root)
		print('#file_names: ', file_names)
		root_part_path = os.path.relpath(root, indir)
		print('#root_part_path: ', root_part_path)
		print(file_names)
		# des_file_names = list(filter(lambda x: x.endswith('.txt'), file_names))
		# des_file_paths = [os.path.join(root, e) for e in des_file_names]
		# print('ndes_file_names', len(des_file_names))
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


		with open(name_file) as f:
			names = f.readlines()
			print(names)
			print('sorted(names)',sorted(names))
			name2idx = {name.rstrip().upper(): i for i, name in enumerate(sorted(names))}
			idx2name = {i:name.rstrip().upper() for i, name in enumerate(sorted(names))}
			print('name2idx = ', name2idx)

		yolo_file_names = list(filter(lambda x: x.endswith('.txt'), file_names))
		yolo_file_paths = [os.path.join(root, e) for e in yolo_file_names]

		correct_count = 0
		n_lp = 0
		false_reports = []

		print('idx2name: ', idx2name)
		for yolo_file_name, yolo_file_path in zip(yolo_file_names, yolo_file_paths):
			yolo_bfile_name = os.path.splitext(yolo_file_name)[0]
			print('yolo_bfile_name: ', yolo_bfile_name)
			with open(yolo_file_path) as f:
				lines = f.readlines()
				print(lines)
				#  = []
				actual_strg = ''
				for line in lines:
					# line = line.replace("-", "")
					# print('line=', line)
					colums = line.split(' ')
					leter = idx2name[int(colums[0])]
					actual_strg += leter
				# try: 
				if actual_strg in pred_strgs_of_img[yolo_bfile_name]:
					correct_count += 1
					print('True ' + yolo_bfile_name + ': ' + actual_strg + ' in ' + str(pred_strgs_of_img[yolo_bfile_name]))
				else:
					false_reports.append('False ' + yolo_bfile_name + ': ' + actual_strg + ' not in ' + str(pred_strgs_of_img[yolo_bfile_name]))
				# except:
				# 	pdb.set_trace()

				n_lp += 1
		acc = correct_count/n_lp
		print('correct_count/n_lp = ' + str(correct_count) + '/' + str(n_lp))
		print('acc = ', acc)
		print('false_report: ')
		for false_report in false_reports:
			print(false_report)
				


if __name__=='__main__':
	import argparse
	ap = argparse.ArgumentParser()
	ap.add_argument("--indir", help="indir")
	ap.add_argument("--preddir", help="preddir")
	ap.add_argument("--name_file", help="name_file")
	args= vars(ap.parse_args())
	main(args["indir"], args["preddir"], args['name_file'])