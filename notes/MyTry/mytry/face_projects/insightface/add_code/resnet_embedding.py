from keras_vggface.vggface import VGGFace
from keras_vggface import utils as vggface_utils
import numpy as np
import tensorflow as tf
import cv2

def prepocess_img_for_resnet(img, image_size):
	img = cv2.resize(img, (image_size, image_size))
	img = img.astype('float64')
	img = img[:, :, ::-1]
	x = np.expand_dims(img, axis=0)
	x = vggface_utils.preprocess_input(x, version=1)
	return x

class FaceModel:
	def __init__(self, image_size):
		self.image_size = image_size
		self._load_model(image_size)

	def _load_model(self):
		with tf.Graph().as_default() as graph:
			self.vgg_features = VGGFace(model='resnet50', include_top=False, input_shape=(self.image_size, self.image_size, 3))
			self.graph = graph

	def get_feature(self, img):
		cvt_image = prepocess_img_for_resnet(img, self.image_size) 
		with self.graph.as_default():
			face_encoding = self.vgg_features.predict(cvt_image)
			return face_encoding
			# face_encodings.shape = (1,-1) #1*2048


# def get_resnet_embeding(vgg_features, graph, images, image_size=None):
# 	cvt_images = [prepocess_img_for_resnet(img, image_size) for img in images]
# 	vecs = []
# 	for cvt_image in cvt_images:
# 		with graph.as_default():
# 			face_encodings = vgg_features.predict(cvt_image)
# 			face_encodings.shape = (1,-1) #1*2048
# 			vecs.append(face_encodings[0])
# 	return np.array(vecs)

# with tf.Graph().as_default() as graph:
# 	vgg_features = VGGFace(model='resnet50', include_top=False, input_shape=(image_size, image_size, 3))
# 	vecs = get_resnet_embeding(vgg_features, graph, images, image_size)


