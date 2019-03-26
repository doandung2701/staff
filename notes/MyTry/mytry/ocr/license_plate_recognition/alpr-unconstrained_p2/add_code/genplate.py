#coding=utf-8
import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import cv2
import numpy as np
import os
from math import *
import pdb


# font = ImageFont.truetype("Arial-Bold.ttf",14)

index = {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
		 "6": 6, "7": 7, "8": 8, "9": 9, "A": 10, "B": 11, "C": 12, "D": 13, "E": 14, "F": 15, "G": 16, "H": 17,
		 "K": 18, "L": 19, "M": 20, "N": 21, "P": 22, "Q": 23, "R": 24, "S": 25, "T": 26, "U": 27, "V": 28,
		 "X": 29, "Y": 30, "Z": 31}

chars = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A",
			 "B", "C", "D", "E", "F", "G", "H", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "U", "V", "X",
			 "Y", "Z"
			 ]

def AddSmudginess(img, Smu):
	rows = r(Smu.shape[0] - 50)

	cols = r(Smu.shape[1] - 50)
	adder = Smu[rows:rows + 50, cols:cols + 50]
	adder = cv2.resize(adder, (50, 50))
	#   adder = cv2.bitwise_not(adder)
	img = cv2.resize(img,(50,50))
	img = cv2.bitwise_not(img)
	img = cv2.bitwise_and(adder, img)
	img = cv2.bitwise_not(img)
	return img

def rot(img,angel,shape,max_angel):

	size_o = [shape[1],shape[0]]

	size = (shape[1]+ int(shape[0]*cos((float(max_angel )/180) * 3.14)),shape[0])


	interval = abs( int( sin((float(angel) /180) * 3.14)* shape[0]))

	pts1 = np.float32([[0,0]         ,[0,size_o[1]],[size_o[0],0],[size_o[0],size_o[1]]])
	if(angel>0):

		pts2 = np.float32([[interval,0],[0,size[1]  ],[size[0],0  ],[size[0]-interval,size_o[1]]])
	else:
		pts2 = np.float32([[0,0],[interval,size[1]  ],[size[0]-interval,0  ],[size[0],size_o[1]]])

	M  = cv2.getPerspectiveTransform(pts1,pts2)
	dst = cv2.warpPerspective(img,M,size)

	return dst

def rotRandrom(img, factor, size):
	shape = size
	pts1 = np.float32([[0, 0], [0, shape[0]], [shape[1], 0], [shape[1], shape[0]]])
	pts2 = np.float32([[r(factor), r(factor)], [ r(factor), shape[0] - r(factor)], [shape[1] - r(factor),  r(factor)],
					   [shape[1] - r(factor), shape[0] - r(factor)]])
	M = cv2.getPerspectiveTransform(pts1, pts2)
	dst = cv2.warpPerspective(img, M, size)
	return dst



def tfactor(img):
	hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

	hsv[:,:,0] = hsv[:,:,0]*(0.8+ np.random.random()*0.2)
	hsv[:,:,1] = hsv[:,:,1]*(0.3+ np.random.random()*0.7)
	hsv[:,:,2] = hsv[:,:,2]*(0.2+ np.random.random()*0.8)

	img = cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
	return img

def random_envirment(img,data_set):
	index=r(len(data_set))
	env = cv2.imread(data_set[index])

	env = cv2.resize(env,(img.shape[1],img.shape[0]))

	bak = (img==0)
	bak = bak.astype(np.uint8)*255
	inv = cv2.bitwise_and(bak,env)
	img = cv2.bitwise_or(inv,img)
	return img

def GenCh(f,val):
	# pdb.set_trace()
	img=Image.new("RGB", (45,70),(0,0,0))
	draw = ImageDraw.Draw(img)
	draw.text((0, 3),val,(0,0,0),font=f)
	img =  img.resize((23,70))
	A = np.array(img)

	return A
def GenCh1(f,val):
	img=Image.new("RGB", (23,70),(0,0,0))
	draw = ImageDraw.Draw(img)
	draw.text((0, 2),val.decode('utf-8'),(0,0,0),font=f)
	A = np.array(img)
	return A
def AddGauss(img, level):
	return cv2.blur(img, (level * 2 + 1, level * 2 + 1))


def r(val):
	return int(np.random.random() * val)

def AddNoiseSingleChannel(single):
	diff = 255-single.max()
	noise = np.random.normal(0,1+r(6),single.shape)
	noise = (noise - noise.min())/(noise.max()-noise.min())
	noise= diff*noise
	noise= noise.astype(np.uint8)
	dst = single + noise
	return dst

def addNoise(img,sdev = 0.5,avg=10):
	img[:,:,0] =  AddNoiseSingleChannel(img[:,:,0])
	img[:,:,1] =  AddNoiseSingleChannel(img[:,:,1])
	img[:,:,2] =  AddNoiseSingleChannel(img[:,:,2])
	return img


class GenPlate:


	def __init__(self,fontCh,fontEng,NoPlates):
		self.fontC =  ImageFont.truetype(fontCh,43,0)
		self.fontE =  ImageFont.truetype(fontEng,60,0)
		self.img=np.array(Image.new("RGB", (226,70),(255,255,255)))
		self.bg  = cv2.resize(cv2.imread("./images/xemaybg.bmp"),(226,70))
		self.smu = cv2.imread("./images/smu2.jpg")
		self.noplates_path = []
		for parent,parent_folder,filenames in os.walk(NoPlates):
			for filename in filenames:
				path = parent+"/"+filename
				self.noplates_path.append(path)


	def draw(self,val):
		offset= 2 

		self.img[0:70,offset+8:offset+8+23]= GenCh(self.fontC,val[0])
		self.img[0:70,offset+8+23+6:offset+8+23+6+23]= GenCh1(self.fontE,val[1])
		for i in range(5):
			base = offset+8+23+6+23+17 +i*23 + i*6 
			self.img[0:70, base  : base+23]= GenCh1(self.fontE,val[i+2])
		return self.img
		
	def generate(self,text):
		print("text: ", text)
		if len(text) == 9:
			fg = self.draw(text.decode(encoding="utf-8"))
			pdb.set_trace()
			fg = cv2.bitwise_not(fg)
			com = cv2.bitwise_or(fg,self.bg)
			com = rot(com,r(60)-30,com.shape,30)
			com = rotRandrom(com,10,(com.shape[1],com.shape[0]))
			#com = AddSmudginess(com,self.smu)

			com = tfactor(com)
			com = random_envirment(com,self.noplates_path)
			com = AddGauss(com, 1+r(4))
			# com = addNoise(com)


			return com
	def genPlateString(self,pos,val):
		plateStr = ""
		box = [0,0,0,0,0,0,0,0,0]
		if(pos!=-1):
			box[pos]=1
		for unit,cpos in zip(box,range(len(box))):
			if unit == 1:
				plateStr += val
			else:
				if cpos == 3:
					plateStr += chars[r(22)]
				elif cpos == 2:
					plateStr += chars[10+r(12)]
				else:
					plateStr += chars[r(10)]

		return plateStr

	def genBatch(self, batchSize,pos,charRange, outputPath,size):
		if (not os.path.exists(outputPath)):
			os.mkdir(outputPath)
		for i in range(batchSize):
			plateStr = G.genPlateString(-1,-1)
			img =  G.generate(plateStr)
			img = cv2.resize(img,size)
			filename = os.path.join(outputPath, str(i).zfill(4) + '.' + plateStr + ".jpg")
			cv2.imwrite(filename, img)

G = GenPlate("/home/cuongvm/Resources/common/Soxe2banh.TTF",'/home/cuongvm/Resources/common/Soxe2banh.TTF',"./NoPlates")

# G.genBatch(10000,2,range(31,65),"./plate_train",(272,72))
G.genBatch(1000,2,range(31,65),"/home/cuongvm/tmp/tmp14",(272,72))



cv2.imwrite()



#
#
# cv2.imshow("a",com)
# cv2.waitKey(0)
