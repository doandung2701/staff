import sys, os
import keras
import cv2
import traceback
sys.path.append('.')

from src.keras_utils 			import load_model
from glob 						import glob
from os.path 					import splitext, basename
from src.utils 					import im2single
from src.keras_utils 			import load_model, detect_lp
from src.label 					import Shape, writeShapes
import nkeras_utils


def adjust_pts(pts,lroi):
	return pts*lroi.wh().reshape((2,1)) + lroi.tl().reshape((2,1))


if __name__ == '__main__':

	try:
		
		input_dir  = sys.argv[1]
		output_dir = input_dir
		out_sizes_str = sys.argv[3]

		out_size_strs = out_sizes_str.split(':')
		out_sizes = []
		for out_size_str in out_size_strs:
			out_size = tuple([int(x) for x in out_size_str.split('x')])
			out_sizes.append(out_size)
		print('out_sizes: ', out_sizes)
		


		lp_threshold = .5

		wpod_net_path = sys.argv[2]
		wpod_net = load_model(wpod_net_path)

		imgs_paths = glob('%s/*car.png' % input_dir)

		print 'Searching for license plates using WPOD-NET'

		for i,img_path in enumerate(imgs_paths):

			print '\t Processing %s' % img_path

			bname = splitext(basename(img_path))[0]
			Ivehicle = cv2.imread(img_path)

			ratio = float(max(Ivehicle.shape[:2]))/min(Ivehicle.shape[:2])
			side  = int(ratio*288.)
			bound_dim = min(side + (side%(2**4)),608)
			print "\t\tBound dim: %d, ratio: %f" % (bound_dim,ratio)

			# Llp,LlpImgs,_ = detect_lp(wpod_net,im2single(Ivehicle),bound_dim,2**4,out_size,lp_threshold)
			Llp,LlpImgs,_ = nkeras_utils.detect_lp(wpod_net,im2single(Ivehicle),bound_dim,2**4,out_sizes,lp_threshold)

			if len(LlpImgs):
				Ilp = LlpImgs[0]
				Ilp = cv2.cvtColor(Ilp, cv2.COLOR_BGR2GRAY)
				Ilp = cv2.cvtColor(Ilp, cv2.COLOR_GRAY2BGR)

				s = Shape(Llp[0].pts)

				cv2.imwrite('%s/%s_lp.png' % (output_dir,bname),Ilp*255.)
				writeShapes('%s/%s_lp.txt' % (output_dir,bname),[s])

	except:
		traceback.print_exc()
		sys.exit(1)

	sys.exit(0)


