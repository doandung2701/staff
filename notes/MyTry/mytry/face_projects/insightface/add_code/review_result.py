
import random
from os import listdir, mkdir, system
from os.path import expanduser, join, split, splitext, exists
from glob import glob


def main(input_path, output_path):

	pairs = []
	with open(input_path) as f:
		lines = f.readlines()
		print(lines)
		for line in lines[1:]:
			colums = line.split(',')
			img_name, result = colums[0], colums[1].rstrip()
			result = [int(e) for e in result.split(' ')]
			pairs.append((img_name, result))
	n_pair = len(pairs)
	print('n_pair: ', n_pair)
	pairs = sorted(pairs, key= lambda x: x[0])

	statis = dict()
	for i in range(1001):
		statis[i] = 0
	for img, result in pairs:
		statis[result[0]] += 1

	import matplotlib
	matplotlib.use('Agg')
	import matplotlib.pylab as plt
	lists = sorted(statis.items())
	x, y = zip(*lists) # unpack a list of pairs into two tuples
	plt.plot(x, y)
	if not exists(split(output_path)[0]):
		system('mkdir -p ' + split(output_path)[0])
	plt.savefig(output_path)


	# with open(output, 'w') as f:
	# 	f.write('image,label\n')
	# 	for i, ((idx, result), actual_img_name) in enumerate(zip(pairs,actual_img_names)):
	# 		assert i == idx
	# 		f.write(actual_img_name + ',' + result)
	# 		if i < len(actual_img_names) - 1:
	# 			f.write('\n')


if __name__=='__main__':
	import argparse
	ap = argparse.ArgumentParser()
	ap.add_argument("--input_path", help="input_path")
	ap.add_argument("--output_path", help="output_path")
	args= vars(ap.parse_args())
	main(args["input_path"], args["output_path"])
