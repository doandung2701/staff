import sys
sys.path.append('/home/cuongvm/MySetting/staff/code/Librarys/processing_data/')
from os import mkdir, system
from os.path import split, splitext, join, exists
from data import load_data
from augmentation import flip, gamma_adjust
from random import randint, shuffle
import cv2

def get_added_pairs(pairs, n_add):
    shuffle(pairs)
    c = 0
    added_pairs = []
    while c < n_add:
        for pair in pairs:
            if c >= n_add:
                break
            path, img = pair
            img_bpath, ext = splitext(path)
            _new_path = img_bpath + '_' + str(c) + ext 
            if c == 0:
                added_pairs.append((_new_path, flip([img])[0]))
            else:
                added_pairs.append((_new_path, gamma_adjust([img])[0]))
            c += 1
    return added_pairs


def main(data_dir, outdir, threshold):
    name2file = load_data(data_dir)
    name2path = {name: [join(data_dir, name, f) for f in files] for name, files in name2file.items()}
    for name, paths in name2path.items():
        n_f = len(paths)
        pairs = [(path, cv2.imread(path)) for path in paths]
        if n_f < threshold:
            n_add = threshold - n_f
            _added_pairs = get_added_pairs(pairs, n_add)
            _final_pairs = pairs + _added_pairs
        else:
            _final_pairs = pairs
        
        for path, img in _final_pairs:
            name_path, img_name = split(path)
            name = split(name_path)[1]
            out_path = join(outdir, name, img_name)
            if not exists(join(outdir,name)):
                mkdir(join(outdir,name))
            cv2.imwrite(out_path,img)


if __name__=='__main__':
	import argparse
	ap = argparse.ArgumentParser()
	ap.add_argument("--indir", help="indir")
	ap.add_argument("--outdir", help="outdir")
	ap.add_argument("--threshold", type=int, help="threshold")
	args= vars(ap.parse_args())
	main(args["indir"], args["outdir"], args['threshold'])