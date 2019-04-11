from __future__ import division
import sys, time, cv2
import numpy as np
sys.path.append('.')
from src.utils import getWH, nms
from src.projection_utils import getRectPts, find_T_matrix
from src.keras_utils import DLabel


def reconstruct(Iorig,I,Y,out_sizes,threshold=.9):
	
	net_stride 	= 2**4
	side 		= ((208. + 40.)/2.)/net_stride # 7.75

	Probs = Y[...,0]
	Affines = Y[...,2:]
	rx,ry = Y.shape[:2]
	ywh = Y.shape[1::-1]
	iwh = np.array(I.shape[1::-1],dtype=float).reshape((2,1))

	xx,yy = np.where(Probs>threshold)

	WH = getWH(I.shape)
	MN = WH/net_stride

	vxx = vyy = 0.5 #alpha

	base = lambda vx,vy: np.matrix([[-vx,-vy,1.],[vx,-vy,1.],[vx,vy,1.],[-vx,vy,1.]]).T
	labels = []

	for i in range(len(xx)):
		y,x = xx[i],yy[i]
		affine = Affines[y,x]
		prob = Probs[y,x]

		mn = np.array([float(x) + .5,float(y) + .5])

		A = np.reshape(affine,(2,3))
		A[0,0] = max(A[0,0],0.)
		A[1,1] = max(A[1,1],0.)

		pts = np.array(A*base(vxx,vyy)) #*alpha
		pts_MN_center_mn = pts*side
		pts_MN = pts_MN_center_mn + mn.reshape((2,1))

		pts_prop = pts_MN/MN.reshape((2,1))

		labels.append(DLabel(0,pts_prop,prob))

	final_labels = nms(labels,.1)
	TLps = []

	if len(final_labels):
		final_labels.sort(key=lambda x: x.prob(), reverse=True)
		for i,label in enumerate(final_labels):
			##add code
			print('out_sizes: ', out_sizes)
			assert isinstance(out_sizes, list) and len(out_sizes) > 0 and len(out_sizes) < 3
			if len(out_sizes) == 1:
				out_size = out_sizes[0]
			else:
				w=label.pts[0][1]-label.pts[0][0]
				h=label.pts[1][3]-label.pts[1][0]
				r = w/h
				s1, s2 = out_sizes[0], out_sizes[1]
				if r > 1.3:
					out_size = s1 if s1[0]/s1[1] > s2[0]/s2[1] else s2
				else:
					out_size = s1 if s1[0]/s1[1] < s2[0]/s2[1] else s2
				print('r, out_size: ',r, out_size)
			##
			t_ptsh 	= getRectPts(0,0,out_size[0],out_size[1])
			ptsh 	= np.concatenate((label.pts*getWH(Iorig.shape).reshape((2,1)),np.ones((1,4))))
			H 		= find_T_matrix(ptsh,t_ptsh)
			Ilp 	= cv2.warpPerspective(Iorig,H,out_size,borderValue=.0)

			TLps.append(Ilp)

	return final_labels,TLps

def detect_lp(model,I,max_dim,net_step,out_sizes,threshold):
	assert isinstance(out_sizes, list)
	min_dim_img = min(I.shape[:2])
	factor 		= float(max_dim)/min_dim_img

	w,h = (np.array(I.shape[1::-1],dtype=float)*factor).astype(int).tolist()
	w += (w%net_step!=0)*(net_step - w%net_step)
	h += (h%net_step!=0)*(net_step - h%net_step)
	Iresized = cv2.resize(I,(w,h))

	T = Iresized.copy()
	T = T.reshape((1,T.shape[0],T.shape[1],T.shape[2]))

	start 	= time.time()
	Yr 		= model.predict(T)
	Yr 		= np.squeeze(Yr)
	elapsed = time.time() - start

	L,TLps = reconstruct(I,Iresized,Yr,out_sizes,threshold)

	return L,TLps,elapsed