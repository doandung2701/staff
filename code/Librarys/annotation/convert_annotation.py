from __future__ import division
import os, glob, cv2, random
import xml.etree.ElementTree as ET 
import sys
sys.path.append('.')
from src.label import Label
import numpy as np

sys.path.append(os.path.expanduser('~/MySetting/staff/notes/MyTry/mytry/ocr/license_plate_recognition/alpr-unconstrained_p2/add_code/'))
from sort_label import numeric_compare, analysis


def main(indir, lpdir, imgdir, name_file, outdir):
	print("##Convert annotation function")
	indir = os.path.expanduser(indir)
	lpdir = os.path.expanduser(lpdir)
	imgdir = os.path.expanduser(imgdir)
	outdir = os.path.expanduser(outdir)


	if os.path.exists(outdir):
		os.system('rm -rf ' + outdir)
	os.system('mkdir -p ' + outdir)

	name_file = os.path.expanduser(name_file)
	with open(name_file) as f:
		names = f.readlines()
		print(names)
		print('sorted(names)',sorted(names))
		name2idx = {name.rstrip().upper(): i for i, name in enumerate(sorted(names))}
		print('name2idx = ', name2idx)


	for root, _, file_names in os.walk(indir):
		print('#Root:',root)
		print('#file_names: ', file_names)
		root_part_path = os.path.relpath(root, indir)
		print('#root_part_path: ', root_part_path)
		print(file_names)

		
		new_root = os.path.join(outdir, root_part_path)
		try:
			os.mkdir(new_root)
		except: pass


		des_file_names = list(filter(lambda x: x.endswith('.txt'), file_names))
		des_file_paths = [os.path.join(root, e) for e in des_file_names]
		for des_file_name, des_file_path in zip(des_file_names, des_file_paths):
			bfile_name = os.path.splitext(des_file_name)[0]
			print('bfile_name: ', bfile_name)
			actual_strgs = []
			with open(des_file_path) as f:
				lines = f.readlines()
				print(lines)
				for line in lines:
					line = line.replace("-", "")
					print('line=', line)
					colums = line.split(',')
					raw_strg = colums[9]
					actual_strg = raw_strg.split('.')[0]
					print('actual_strg: ', actual_strg)
					actual_strgs.append(actual_strg)



			xml_file_paths = sorted(glob.glob(os.path.join(lpdir, root_part_path,bfile_name + '_?.xml')))
			xml_file_names = [os.path.basename(path) for path in xml_file_paths]
			print('nxml_file_names', len(xml_file_names))



			for xml_file_name, xml_file_path, actual_strg in zip(xml_file_names, xml_file_paths, actual_strgs):
				xml_bfile_name = os.path.splitext(xml_file_name)[0]
				print('xml_bfile_name: ', xml_bfile_name)
				
				print("os.path.join(imgdir, root_part_path, xml_bfile_name + '.jpg' = ", os.path.join(imgdir, root_part_path, xml_bfile_name + '.jpg'))
				print("os.path.join(outdir, root_part_path) = ", os.path.join(outdir, root_part_path))
				os.system('cp ' + os.path.join(imgdir, root_part_path, xml_bfile_name + '.jpg') + ' ' + os.path.join(outdir, root_part_path))
				
				tree = ET.parse(xml_file_path)  
				root = tree.getroot()

				size = root[4]
				width, height = [int(e.text) for e in size[:2]]


				yolo_file_name = os.path.join(outdir, root_part_path, xml_bfile_name + '.txt')
				with open(yolo_file_name, 'w+') as f:
					L = []
					for i, ob in enumerate(root.findall('object')):
						name, bndbox = ob[0], ob[4]
						print('name.text, bndbox', name.text, bndbox)
						xmin, ymin, xmax, ymax = [int(e.text) for e in bndbox[:]]
						print('xmin, ymin, xmax, ymax: ', xmin, ymin, xmax, ymax)
						l = Label()
						l.set_tl(np.array([xmin, ymin]))
						l.set_br(np.array([xmax, ymax]))
						L.append(l)
					print('len(L): ', len(L))
					L_pair = list(zip(L, [(width, height)]* len(L)))
					L_pair = sorted(L_pair, cmp=numeric_compare)
					L, _ = zip(*L_pair)
					print('len(L): ', len(L))
					for i, l in enumerate(L):
						print('i: ', i)
						(xmin, ymin), (xmax, ymax) = l.tl(), l.br()
						yolo_location = [(xmin + xmax)/2/width, (ymin + ymax)/2/height, (xmax - xmin)/width, (ymax - ymin)/height]
						yolo_strg = str(name2idx[actual_strg[i]]) + ' ' + ' '.join(["%.6f" % round(e, 6) for e in yolo_location]) 
						print('i, yolo_strg: ', i,yolo_strg)
						if i < len(root.findall('object')) - 1:
							yolo_strg += '\n'
						f.write(yolo_strg)

				


if __name__=='__main__':
	import argparse
	ap = argparse.ArgumentParser()
	ap.add_argument("--indir", help="indir")
	ap.add_argument("--lpdir", help="lpdir")
	ap.add_argument("--imgdir", help="imgdir")
	ap.add_argument("--name_file", help="name_file")
	ap.add_argument("--outdir", help="outdir")
	
	

	args= vars(ap.parse_args())
	main(args["indir"], args["lpdir"], args['imgdir'], args['name_file'], args["outdir"])