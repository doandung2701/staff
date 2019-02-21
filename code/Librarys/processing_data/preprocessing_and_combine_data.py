import glob
import argparse
import os
from zemcy import support_lib as sl
def main(indir, outdir):
    print('##Combind function')
    print('foler: ', indir)
    os.system('rm -rf ' +  outdir)
    os.system('mkdir ' + outdir)
    img_paths = glob.glob(os.path.join(indir,'**'), recursive=True)
    print('n raw file:',len(img_paths))
    origin_img_paths = list(filter(sl.is_img_type, img_paths))
    img_paths = [img_path.replace('(', '').replace(')', '').replace(' ', '').replace('&','__') for img_path in origin_img_paths]
    print('n img:',len(img_paths))
    for origin_img_path, img_path in zip(origin_img_paths, img_paths):
        os.rename(origin_img_path, img_path)
        os.system('cp ' + img_path + ' ' + outdir)


if __name__=='__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("--indir", help="indir")
    ap.add_argument("--outdir", help="indir")
    args= vars(ap.parse_args())
    main(args["indir"], args["outdir"])
    
