from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from scipy import misc
import sys
sys.path.append('./deploy')
import os
import argparse
import tensorflow as tf
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
import face_preprocess
from umeyama import umeyama
from face_alignment import FaceAlignment, LandmarksType
# from align_image import landmarks_2D, transform
import pdb

mean_face_x = np.array([
0.000213256, 0.0752622, 0.18113, 0.29077, 0.393397, 0.586856, 0.689483, 0.799124,
0.904991, 0.98004, 0.490127, 0.490127, 0.490127, 0.490127, 0.36688, 0.426036,
0.490127, 0.554217, 0.613373, 0.121737, 0.187122, 0.265825, 0.334606, 0.260918,
0.182743, 0.645647, 0.714428, 0.793132, 0.858516, 0.79751, 0.719335, 0.254149,
0.340985, 0.428858, 0.490127, 0.551395, 0.639268, 0.726104, 0.642159, 0.556721,
0.490127, 0.423532, 0.338094, 0.290379, 0.428096, 0.490127, 0.552157, 0.689874,
0.553364, 0.490127, 0.42689 ])

mean_face_y = np.array([
0.106454, 0.038915, 0.0187482, 0.0344891, 0.0773906, 0.0773906, 0.0344891,
0.0187482, 0.038915, 0.106454, 0.203352, 0.307009, 0.409805, 0.515625, 0.587326,
0.609345, 0.628106, 0.609345, 0.587326, 0.216423, 0.178758, 0.179852, 0.231733,
0.245099, 0.244077, 0.231733, 0.179852, 0.178758, 0.216423, 0.244077, 0.245099,
0.780233, 0.745405, 0.727388, 0.742578, 0.727388, 0.745405, 0.780233, 0.864805,
0.902192, 0.909281, 0.902192, 0.864805, 0.784792, 0.778746, 0.785343, 0.778746,
0.784792, 0.824182, 0.831803, 0.824182 ])

landmarks_2D = np.stack( [ mean_face_x, mean_face_y ], axis=1 )

def transform( image, mat, size, padding=0 ):
    mat = mat * size
    mat[:,2] += padding
    new_size = int( size + padding * 2 )
    return cv2.warpAffine( image, mat, ( new_size, new_size ) )

def do_flip(data):
  for idx in xrange(data.shape[0]):
    data[idx,:,:] = np.fliplr(data[idx,:,:])

class FaceModel:
  def __init__(self, args):
    self.args = args
    model = edict()

    self.threshold = args.threshold
    self.det_minsize = 50
    self.det_threshold = [0.4,0.6,0.6]
    self.det_factor = 0.9
    _vec = args.image_size.split(',')
    assert len(_vec)==2
    image_size = (int(_vec[0]), int(_vec[1]))
    self.image_size = image_size
    _vec = args.model.split(',')
    assert len(_vec)==2
    prefix = _vec[0]
    epoch = int(_vec[1])
    print('loading',prefix, epoch)
    ctx = mx.gpu(args.gpu)
    sym, arg_params, aux_params = mx.model.load_checkpoint(prefix, epoch)
    all_layers = sym.get_internals()
    sym = all_layers['fc1_output']
    model = mx.mod.Module(symbol=sym, context=ctx, label_names = None)
    #model.bind(data_shapes=[('data', (args.batch_size, 3, image_size[0], image_size[1]))], label_shapes=[('softmax_label', (args.batch_size,))])
    model.bind(data_shapes=[('data', (1, 3, image_size[0], image_size[1]))])
    model.set_params(arg_params, aux_params)
    self.model = model
    # mtcnn_path = os.path.join(os.path.dirname(__file__), 'mtcnn-model')
    mtcnn_path = os.path.join('deploy','mtcnn-model')
    detector = MtcnnDetector(model_folder=mtcnn_path, ctx=ctx, num_worker=1, accurate_landmark = True, threshold=[0.0,0.0,0.2])
    self.detector = detector
    self.FACE_ALIGNMENT = FaceAlignment( LandmarksType._3D, device='cuda', flip_input=False )


  def get_feature(self, face_img):
    detected = True
    #face_img is bgr image
    def mtcnn_align(img):
      ret = self.detector.detect_face_limited(face_img, det_type = self.args.det)
      if ret is None:
        # detected = False
        bbox, points = None, None
      else:
        bbox, points = ret
        if bbox.shape[0]==0:
          # detected = False
          bbox, points = None, None
        else:
          bbox = bbox[0,0:4]
          points = points[0,:].reshape((2,5)).T
      # print(bbox)
      # print(points)
      nimg = face_preprocess.preprocess(face_img, bbox, points, image_size='112,112')
      return nimg
    # skimage.io.imread( str(fn) )
    faces = self.FACE_ALIGNMENT.get_landmarks(face_img)
    if faces is not None:
      if len(faces) > 1:
        faces = faces[0:1]
        # pdb.set_trace()
      points = faces[0]
      alignment = umeyama(points[17:], landmarks_2D, True)[0:2]
      nimg = _aligned_image = transform(face_img, alignment, 112, 0)
    else:
      nimg = mtcnn_align(face_img)
      # nimg = face_preprocess.preprocess(face_img, image_size='112,112')
    # pdb.set_trace()
    nimg = cv2.cvtColor(nimg, cv2.COLOR_BGR2RGB)
    aligned = np.transpose(nimg, (2,0,1))
    #print(nimg.shape)
    embedding = None
    for flipid in [0,1]:
      if flipid==1:
        if self.args.flip==0:
          break
        do_flip(aligned)
      input_blob = np.expand_dims(aligned, axis=0)
      data = mx.nd.array(input_blob)
      db = mx.io.DataBatch(data=(data,))
      self.model.forward(db, is_train=False)
      _embedding = self.model.get_outputs()[0].asnumpy()
      #print(_embedding.shape)
      if embedding is None:
        embedding = _embedding
      else:
        embedding += _embedding
    embedding = sklearn.preprocessing.normalize(embedding).flatten()
    return detected, embedding

