# test embeding
python -c "from nface_embedding import FaceModel;from data import get_config;args=get_config();f=FaceModel(args);from cv2 import imread,resize;v1 = f.get_feature(resize(imread('/home/cuongvm/Resources/datasets/faces/vn_celeb_face_recognition_lfw10/0/0_0000.jpg'),(112,112) ));import numpy as np;d=np.sum(np.square(v1-v1));print(d)    "

# 