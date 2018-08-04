import sys
sys.path.append('/home/cuong/VNG/National_Identification_Card_Reader/src')
import support_lib as sl

import cv2
import numpy as np
from PIL import Image,ImageFont, ImageDraw
fontpath = "/home/cuong/Documents/vni-full-standard/font-times-new-roman.ttf"   
font_size = 12
font = ImageFont.truetype(fontpath, font_size)

img = sl.create_img((100,100))
img_pil = Image.fromarray(img)
draw = ImageDraw.Draw(img_pil)

ascent, descent = font.getmetrics()
print('ascent, descent = ', ascent, descent)
text = 'Â'
(width, baseline), (offset_x, offset_y) = font.font.getsize(text)
print('width, baseline = ', width, baseline)
print('offset_x, offset_y = ', offset_x, offset_y)

box = font.getmask(text).getbbox()
print('box = ',box)

b,g,r,a = 0,255,0,0
draw.text((0, offset_y ),  text, font = font, fill = (b, g, r, a))
img = np.array(img_pil)
cv2.imshow('img', img)
cv2.waitKey(0)
