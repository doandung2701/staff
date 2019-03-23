
import random
from os import listdir, mkdir, system
from os.path import expanduser, join, split, splitext, exists
from glob import glob


def main(indir, input_path, output):
	actual_img_names = listdir(indir)

	pairs = []
	with open(input_path) as f:
		lines = f.readlines()
		print(lines)
		for line in lines[1:]:
			colums = line.split(',')
			img_name, result = colums[0], colums[1].rstrip()
			pairs.append((img_name, result))
	n_pair = len(pairs)
	print('n_pair: ', n_pair)



	with open(output, 'w') as f:
		f.write('image,label\n')
		for i, ((img_name, result), actual_img_name) in enumerate(zip(pairs,actual_img_names)):
			f.write(actual_img_name + ',' + result)
			if i < len(actual_img_names) - 1:
				f.write('\n')


if __name__=='__main__':
	import argparse
	ap = argparse.ArgumentParser()
	ap.add_argument("--indir", help="indir")
	ap.add_argument("--input_path", help="input_path")
	ap.add_argument("--output_path", help="output_path")
	args= vars(ap.parse_args())
	main(args["indir"],args["input_path"], args["output_path"])
