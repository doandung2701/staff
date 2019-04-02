from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from scipy import misc
import sys
sys.path.append('./deploy')
import os
import argparse
#import tensorflow as tf
import numpy as np
import mxnet as mx
import random
import cv2
import sklearn
from sklearn.decomposition import PCA
from time import sleep
from easydict import EasyDict as edict
from mtcnn_detector import MtcnnDetector
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'common'))
import face_image
import face_preprocess
from mxnet import ndarray as nd
import pdb



def do_flip(data):
  for idx in xrange(data.shape[0]):
    data[idx,:,:] = np.fliplr(data[idx,:,:])

def get_model(ctx, image_size, model_str, layer):
  _vec = model_str.split(',')
  assert len(_vec)==2
  prefix = _vec[0]
  epoch = int(_vec[1])
  print('loading',prefix, epoch)
  sym, arg_params, aux_params = mx.model.load_checkpoint(prefix, epoch)
  all_layers = sym.get_internals()
  sym = all_layers[layer+'_output']
  model = mx.mod.Module(symbol=sym, context=ctx, label_names = None)
  #model.bind(data_shapes=[('data', (args.batch_size, 3, image_size[0], image_size[1]))], label_shapes=[('softmax_label', (args.batch_size,))])
  model.bind(data_shapes=[('data', (1, 3, image_size[0], image_size[1]))])
  model.set_params(arg_params, aux_params)
  return model

class FaceModel:
  def __init__(self, args):
    self.args = args
    ctx = mx.gpu(args.gpu)
    _vec = args.image_size.split(',')
    assert len(_vec)==2
    image_size = (int(_vec[0]), int(_vec[1]))
    self.model = None
    self.ga_model = None
    if len(args.model)>0:
      self.model = get_model(ctx, image_size, args.model, 'fc1')
    if len(args.ga_model)>0:
      self.ga_model = get_model(ctx, image_size, args.ga_model, 'fc1')

    self.threshold = args.threshold
    self.det_minsize = 50
    self.det_threshold = [0.6,0.7,0.8]
    #self.det_factor = 0.9
    self.image_size = image_size
    mtcnn_path = os.path.join('deploy','mtcnn-model')
    if args.det==0:
      detector = MtcnnDetector(model_folder=mtcnn_path, ctx=ctx, num_worker=1, accurate_landmark = True, threshold=self.det_threshold)
    else:
      detector = MtcnnDetector(model_folder=mtcnn_path, ctx=ctx, num_worker=1, accurate_landmark = True, threshold=[0.0,0.0,0.2])
    self.detector = detector


  def get_input(self, img):
    ret = self.detector.detect_face(img, det_type = self.args.det)
    if ret is None:
      g_bbox, g_points = [], []
    else:
      bbox, points = ret
      if bbox.shape[0]==0:
        g_bbox, g_points = [], []
      else:
        g_bbox = bbox[:,0:4]
        g_points = [points[i,:].reshape((2,5)).T for i in range(points.shape[0])]
    #print(bbox)
    #print(points)

    aligned_imgs = []
    for bbox, points in zip(g_bbox, g_points):
        nimg = face_preprocess.preprocess(img, bbox, points, image_size='112,112')
        nimg = cv2.cvtColor(nimg, cv2.COLOR_BGR2RGB)
        aligned = np.transpose(nimg, (2,0,1))
        aligned_imgs.append(aligned)
    return aligned_imgs, g_bbox

  def mutil_get_feature(self, aligneds, batch_size=32):
    batch_size = min(len(aligneds), batch_size)
    # pdb.set_trace()
    # data = nd.array([mx.image.imdecode(_bin) for _bin in aligneds])
    data = nd.array(aligneds)
    embeddings = None
    ba = 0
    while ba<data.shape[0]:
      bb = min(ba+batch_size, data.shape[0])
      count = bb-ba
      _data = nd.slice_axis(data, axis=0, begin=bb-batch_size, end=bb)
      # _data = nd.array(aligneds[bb-batch_size:bb])
      #print(_data.shape, _label.shape)
      # time0 = datetime.datetime.now()
      _label = nd.ones( (batch_size,) )
      db = mx.io.DataBatch(data=(_data,))
      self.model.forward(db, is_train=False)
      net_out = self.model.get_outputs()
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
    #   time_now = datetime.datetime.now()
    #   diff = time_now - time0
    #   time_consumed+=diff.total_seconds()
      print(_embeddings.shape)
      if embeddings is None:
        embeddings = np.zeros( (data.shape[0], _embeddings.shape[1]) )
      embeddings[ba:bb,:] = _embeddings[(batch_size-count):,:]
      ba = bb
    # embeddings_list.append(embeddings)



    # input_blob = np.expand_dims(aligned, axis=0)
    # data = mx.nd.array(input_blob)
    # db = mx.io.DataBatch(data=(data,))
    # self.model.forward(db, is_train=False)
    # embedding = self.model.get_outputs()[0].asnumpy()
    embeddings = sklearn.preprocessing.normalize(embeddings)
    return embeddings

  def get_feature(self, aligned):
    input_blob = np.expand_dims(aligned, axis=0)
    data = mx.nd.array(input_blob)
    db = mx.io.DataBatch(data=(data,))
    self.model.forward(db, is_train=False)
    embedding = self.model.get_outputs()[0].asnumpy()
    embedding = sklearn.preprocessing.normalize(embedding).flatten()
    return embedding

  def get_ga(self, aligned):
    input_blob = np.expand_dims(aligned, axis=0)
    data = mx.nd.array(input_blob)
    db = mx.io.DataBatch(data=(data,))
    self.ga_model.forward(db, is_train=False)
    ret = self.ga_model.get_outputs()[0].asnumpy()
    g = ret[:,0:2].flatten()
    gender = np.argmax(g)
    a = ret[:,2:202].reshape( (100,2) )
    a = np.argmax(a, axis=1)
    age = int(sum(a))

    return gender, age

