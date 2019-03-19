from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import argparse
import sys
import numpy as np
from scipy import misc
from sklearn.model_selection import KFold
from scipy import interpolate
import sklearn
import cv2
import math
import datetime
import pickle
from sklearn.decomposition import PCA
import mxnet as mx
from mxnet import ndarray as nd
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
import face_image



def evaluate(embeddings, issame_list):
	thresholds = np.arange(0, 4, 0.01)
	nrof_thresholds = len(thresholds)
	embeddings1 = embeddings[0::2]
	embeddings2 = embeddings[1::2]
	assert(embeddings1.shape[0] == embeddings2.shape[0])
	assert(embeddings1.shape[1] == embeddings2.shape[1])
	actual_issame = np.asarray(actual_issame)
	nrof_pairs = min(len(actual_issame), embeddings1.shape[0])

	# n_train_set, n_test_set = 6000, 17091*1000
	# n_train_set = 6000, 17091*1000
	train_set = list(range(nrof_pairs))
	print('train_set', train_set)
	# print('test_set', test_set)

	if pca==0:
	  diff = np.subtract(embeddings1, embeddings2)
	  dist = np.sum(np.square(diff),1)


	# Find the best threshold for the fold
	acc_train = np.zeros((nrof_thresholds))
	for threshold_idx, threshold in enumerate(thresholds):
		_, _, acc_train[threshold_idx] = calculate_accuracy(threshold, dist[train_set], actual_issame[train_set])
	best_threshold_index = np.argmax(acc_train)
	print('threshold', thresholds[best_threshold_index])

	# predict_issame = np.less(dist[test_set], thresholds[best_threshold_index])


	# for threshold_idx, threshold in enumerate(thresholds):
	# 	tprs[fold_idx,threshold_idx], fprs[fold_idx,threshold_idx], _ = calculate_accuracy(threshold, dist[test_set], actual_issame[test_set])
	# _, _, accuracy[fold_idx] = calculate_accuracy(thresholds[best_threshold_index], dist[test_set], actual_issame[test_set])

def load_bin(path, image_size):
  bins, issame_list = pickle.load(open(path, 'rb'))
  print('len(issame_list): ', len(issame_list))
  print('issame_list[0]: ', issame_list[0])
  data_list = []
  for flip in [0,1]:
    data = nd.empty((len(issame_list)*2, 3, image_size[0], image_size[1]))
    data_list.append(data)
  for i in xrange(len(issame_list)*2):
    _bin = bins[i]
    img = mx.image.imdecode(_bin)
    if img.shape[1]!=image_size[0]:
      img = mx.image.resize_short(img, image_size[0])
    img = nd.transpose(img, axes=(2, 0, 1))
    for flip in [0,1]:
      if flip==1:
        img = mx.ndarray.flip(data=img, axis=2)
      data_list[flip][i][:] = img
    if i%1000==0:
      print('loading bin', i)
  print(data_list[0].shape)
  return (data_list, issame_list)


def test(data_set, mx_model, batch_size, data_extra = None, label_shape = None):
	print('testing verification..')
	data_list = data_set[0]
	issame_list = data_set[1]
	model = mx_model
	embeddings_list = []
	if data_extra is not None:
		_data_extra = nd.array(data_extra)
	time_consumed = 0.0
	if label_shape is None:
		_label = nd.ones( (batch_size,) )
	else:
		_label = nd.ones( label_shape )
	for i in xrange( len(data_list) ):
		data = data_list[i]
		embeddings = None
		ba = 0
		while ba<data.shape[0]:
			bb = min(ba+batch_size, data.shape[0])
			count = bb-ba
			_data = nd.slice_axis(data, axis=0, begin=bb-batch_size, end=bb)
			#print(_data.shape, _label.shape)
			time0 = datetime.datetime.now()
			if data_extra is None:
				db = mx.io.DataBatch(data=(_data,), label=(_label,))
			else:
				db = mx.io.DataBatch(data=(_data,_data_extra), label=(_label,))
			model.forward(db, is_train=False)
			net_out = model.get_outputs()
			#_arg, _aux = model.get_params()
			#__arg = {}
			#for k,v in _arg.iteritems():
			#  __arg[k] = v.as_in_context(_ctx)
			#_arg = __arg
			#_arg["data"] = _data.as_in_context(_ctx)
			#_arg["softmax_label"] = _label.as_in_context(_ctx)
			#for k,v in _arg.iteritems():
			#  print(k,v.context)
			#exe = sym.bind(_ctx, _arg ,args_grad=None, grad_req="null", aux_states=_aux)
			#exe.forward(is_train=False)
			#net_out = exe.outputs
			_embeddings = net_out[0].asnumpy()
			time_now = datetime.datetime.now()
			diff = time_now - time0
			time_consumed+=diff.total_seconds()
			#print(_embeddings.shape)
			if embeddings is None:
				embeddings = np.zeros( (data.shape[0], _embeddings.shape[1]) )
			embeddings[ba:bb,:] = _embeddings[(batch_size-count):,:]
			ba = bb	
		embeddings_list.append(embeddings)

	_xnorm = 0.0
	_xnorm_cnt = 0
	for embed in embeddings_list:
		for i in xrange(embed.shape[0]):
			_em = embed[i]
			_norm=np.linalg.norm(_em)
			#print(_em.shape, _norm)
			_xnorm+=_norm
			_xnorm_cnt+=1
	_xnorm /= _xnorm_cnt

	embeddings = embeddings_list[0].copy()
	embeddings = sklearn.preprocessing.normalize(embeddings)

	print('infer time', time_consumed)
	_, _, accuracy, val, val_std, far = evaluate(embeddings, issame_list)


if __name__=='__main__':
	import argparse
	parser = argparse.ArgumentParser(description='do verification')
	parser.add_argument('--model', default='../model/softmax,50', help='path to load model.')
	parser.add_argument('--batch-size', default=32, type=int, help='')
	parser.add_argument('--gpu', default=0, type=int, help='gpu id')

	# ap.add_argument("--indir", help="indir")
	# ap.add_argument("--outdir", help="outdir")
	# ap.add_argument("--des_file_path", help="des_file_path")
	# args= vars(ap.parse_args())
	args = parser.parse_args()

	prop = face_image.load_property(args.data_dir)
    image_size = prop.image_size
    print('image_size', image_size)
	ctx = mx.gpu(args.gpu)
    nets = []

	vec = args.model.split(',')
	prefix = args.model.split(',')[0]
	epochs = []
	if len(vec)==1:
		pdir = os.path.dirname(prefix)
		for fname in os.listdir(pdir):
			if not fname.endswith('.params'):
				continue
			_file = os.path.join(pdir, fname)
			if _file.startswith(prefix):
				epoch = int(fname.split('.')[0].split('-')[1])
				epochs.append(epoch)
		epochs = sorted(epochs, reverse=True)
		if len(args.max)>0:
			_max = [int(x) for x in args.max.split(',')]
			assert len(_max)==2
			if len(epochs)>_max[1]:
				epochs = epochs[_max[0]:_max[1]]

	else:
		epochs = [int(x) for x in vec[1].split('|')]
	print('model number', len(epochs))
	time0 = datetime.datetime.now()
	for epoch in epochs:
		print('loading',prefix, epoch)
		sym, arg_params, aux_params = mx.model.load_checkpoint(prefix, epoch)
		#arg_params, aux_params = ch_dev(arg_params, aux_params, ctx)
		all_layers = sym.get_internals()
		sym = all_layers['fc1_output']
		model = mx.mod.Module(symbol=sym, context=ctx, label_names = None)
		#model.bind(data_shapes=[('data', (args.batch_size, 3, image_size[0], image_size[1]))], label_shapes=[('softmax_label', (args.batch_size,))])
		model.bind(data_shapes=[('data', (args.batch_size, 3, image_size[0], image_size[1]))])
		model.set_params(arg_params, aux_params)
		nets.append(model)
	time_now = datetime.datetime.now()
	diff = time_now - time0
	print('model loading time', diff.total_seconds())

	ver_list = []
	ver_name_list = []
	for name in args.target.split(','):
		path = os.path.join(args.data_dir,name+".bin")
		if os.path.exists(path):
			print('loading.. ', name)
			data_set = load_bin(path, image_size)
			ver_list.append(data_set)
			ver_name_list.append(name)

	for i in xrange(len(ver_list)):
		results = []
		for model in nets:
			acc1, std1, acc2, std2, xnorm, embeddings_list = test(ver_list[i], model, args.batch_size)
			# print('[%s]XNorm: %f' % (ver_name_list[i], xnorm))
			# print('[%s]Accuracy: %1.5f+-%1.5f' % (ver_name_list[i], acc1, std1))
			# print('[%s]Accuracy-Flip: %1.5f+-%1.5f' % (ver_name_list[i], acc2, std2))
			# results.append(acc2)
		#   print('Max of [%s] is %1.5f' % (ver_name_list[i], np.max(results)))


	# main(thresholds)