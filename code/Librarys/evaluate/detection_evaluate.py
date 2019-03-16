from __future__ import division
import os, glob, cv2, random, numpy as np
from zemcy import support_lib as sl

	
def points_intersection_over_union(pointsA, pointsB):
	boxA = sl.points_to_box(pointsA)
	boxB = sl.points_to_box(pointsB)
	ratio = sl.cal_box_overlaping_area_ratio(boxA, boxB)
	return ratio

 
def main(indir, preddir, threshold=0.7):
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
		correct_count = 0
		n_lp = 0
		false_reports = []
		location_of_bfile_name, pred_location_of_bfile_name =  dict(), dict()
		for des_file_name, des_file_path in zip(des_file_names, des_file_paths):
			bfile_name = os.path.splitext(des_file_name)[0]
			print('bfile_name: ', bfile_name)
			with open(des_file_path) as f:
				lines = f.readlines()
				print(lines)
				# actual_strgs = []
				locations = []
				for line in lines:
					print('line=', line)
					colums = line.split(',')
					xs, ys = [float(e) for e in colums[1:5]], [float(e) for e in colums[5:9]]
					location = zip(xs, ys)
					locations.append(location)
				location_of_bfile_name[bfile_name] = locations
			
			pre_file_paths = glob.glob(os.path.join(preddir, root_part_path, bfile_name + '*_lp.txt'))
			print('os.path.join(preddir, root_part_path, bfile_name + "*_lp.txt") = ', os.path.join(preddir, root_part_path, bfile_name + '*_lp.txt'))
			print('pre_file_paths: ', pre_file_paths)
			locations = []
			for pre_file_path in pre_file_paths:
				with open(pre_file_path) as pre_f:
					line = pre_f.readlines()[0]
					colums = line.split(',')
					xs, ys = [float(e) for e in colums[1:5]], [float(e) for e in colums[5:9]]
					location = list(zip(xs, ys))
					locations.append(location)
			pred_location_of_bfile_name[bfile_name] = locations

			print('location_of_bfile_name[bfile_name]: ', location_of_bfile_name[bfile_name])
			print('pred_location_of_bfile_name[bfile_name]: ', pred_location_of_bfile_name[bfile_name])
			for des_location in location_of_bfile_name[bfile_name]:
				is_correct = False
				for pre_location in pred_location_of_bfile_name[bfile_name]:
					np_pre_location, np_des_location = np.array(pre_location, dtype='float64'), np.array(des_location, dtype='float64')
					np_pre_location, np_des_location = 1000*np_pre_location, 1000*np_des_location
					np_pre_location, np_des_location = np_pre_location.astype(int), np_des_location.astype(int)
					# np_pre_location.dtype, np_des_location.dtype = 'int64', 'int64'
					print('np_pre_location, np_des_location = ', np_pre_location, np_des_location)
					print('np_pre_location.dtype, np_des_location.dtype = ', np_pre_location.dtype, np_des_location.dtype)
					ratio = points_intersection_over_union(np_pre_location, np_des_location)
					print('ratio = ', ratio)
					if ratio > threshold:
						is_correct = True
					else:
						false_reports.append('False ' + bfile_name + ', ratio: ' + str(ratio) + ' between ' + str(np_des_location) + ' and ' + str(np_pre_location))
				if is_correct:
					correct_count += 1
				n_lp += 1
		print('\nthreshold: ', threshold)
		print('correct_count, n_lp: ', correct_count, n_lp)
		print('correct_count/n_lp = ', correct_count/n_lp)
		print('false_report: ')
		for false_report in false_reports:
			print(false_report)
				


if __name__=='__main__':
	import argparse
	ap = argparse.ArgumentParser()
	ap.add_argument("--indir", help="indir")
	ap.add_argument("--preddir", help="preddir")
	args= vars(ap.parse_args())
	main(args["indir"], args["preddir"])