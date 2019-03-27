#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Data augmentation module."""

import glob
import os
import random
import sys

import cv2

# import dlib

import numpy as np

# class Aug(object):
#     def brightness_aug(self, src, x):
#       alpha = 1.0 + random.uniform(-x, x)
#       src *= alpha
#       return src

#     def contrast_aug(self, src, x):
#       alpha = 1.0 + random.uniform(-x, x)
#       coef = np.array([[[0.299, 0.587, 0.114]]])
#       gray = src * coef
#       gray = (3.0 * (1.0 - alpha) / gray.size) * np.sum(gray)
#       src *= alpha
#       src += gray
#       return src

#     def saturation_aug(self, src, x):
#       alpha = 1.0 + random.uniform(-x, x)
#       coef = np.array([[[0.299, 0.587, 0.114]]])
#       gray = src * coef
#       gray = np.sum(gray, axis=2, keepdims=True)
#       gray *= (1.0 - alpha)
#       src *= alpha
#       src += gray
#       return src

#     def color_aug(self, img, x):
#       augs = [self.brightness_aug, self.contrast_aug, self.saturation_aug]
#       random.shuffle(augs)
#       for aug in augs:
#         #print(img.shape)
#         img = aug(img, x)
#         #print(img.shape)
#       return img

#     def mirror_aug(self, img):
#       _rd = random.randint(0,1)
#       if _rd==1:
#         for c in xrange(img.shape[2]):
#           img[:,:,c] = np.fliplr(img[:,:,c])
#       return img

def flip(imgs):
    """Flip images."""
    ret = []
    for img in imgs:
        ret.append(cv2.flip(img, 1))
    return ret


def gamma_adjust(imgs):
    """Adjust brightness."""
    ret = []
    for img in imgs:
        if random.random() < 0.5:
            gamma = random.uniform(0.5, 0.7)
        else:
            gamma = random.uniform(1.5, 2)
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) *
                          255 for i in np.arange(0, 256)]).astype("uint8")
        ret.append(cv2.LUT(img, table))
    return ret


def color(imgs):
    """Adjust color."""
    ret = []
    for img in imgs:
        if random.random() < 0.25:  # apply only for 25% images
            img = img.astype('float32')
            img[:, :, 2] += random.randint(20, 50)  # red channel
            if random.random() < 0.5:
                if random.random() < 0.5:
                    img[:, :, 0] += random.randint(20, 50)
                else:
                    img[:, :, 1] += random.randint(20, 50)
            img = cv2.convertScaleAbs(img)
            ret.append(img)
    return ret


def rotate(imgs):
    """Rotate images."""
    ret = []
    for img in imgs:
        h, w, d = img.shape
        if random.random() < 0.5:
            rotation_matrix = cv2.getRotationMatrix2D(
                (w / 2, h / 2), random.uniform(-15, -5), 1)
        else:
            rotation_matrix = cv2.getRotationMatrix2D(
                (w / 2, h / 2), random.uniform(5, 15), 1)
        img_rotation = cv2.warpAffine(img, rotation_matrix, (w, h))
        ret.append(img_rotation)
    return ret


def get_augmented_image(imgs):
    """Apply all adjustment."""
    ret = imgs
    ret.extend(flip(ret))
    ret.extend(rotate(ret))
    ret.extend(color(ret))
    ret.extend(gamma_adjust(ret))
    return ret
    


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print './data_augmentation indir outdir'
        exit()

    in_dir = sys.argv[1]
    out_dir = sys.argv[2]

    list_dir = os.listdir(in_dir)
    for dn in list_dir:
        list_file = glob.glob(os.path.join(in_dir, dn) + '/*.jpg')
        imgs = []
        for fn in list_file:
            imgs.append(cv2.imread(fn))
        imgs = get_augmented_image(imgs)

        out_dir_full = os.path.join(out_dir, dn)
        if not os.path.exists(out_dir_full):
            os.makedirs(out_dir_full)

        for i in range(len(imgs)):
            cv2.imwrite(out_dir_full + '/' + str(i) + '.jpg', imgs[i])
