import os, glob, cv2, random
from zemcy import support_lib as sl
def edit_des_file(indir, outdir):
	print("##Split data function")
	indir = os.path.expanduser(indir)
	outdir = os.path.expanduser(outdir)
	if os.path.exists(outdir):
		os.system("rm -rf " + outdir)
	os.mkdir(outdir)

	for root, _, file_names in os.walk(indir):
		print('#Root:',root)
		print('#file_names: ', file_names)
		root_part_path = os.path.relpath(root, indir)
		print('#root_part_path: ', root_part_path)
		print(file_names)
		des_file_names = list(filter(lambda x: x.endswith('.txt'), file_names))
		des_file_paths = [os.path.join(root, e) for e in des_file_names]
		print('ndes_file_names', len(des_file_names))
		os.mkdir(os.path.join(outdir, root_part_path))
		for des_file_name, des_file_path in zip(des_file_names, des_file_paths):
			with open(des_file_path) as f:
				lines = f.readlines()
				text = ''
				print(lines)
				for line in lines:
					print('line=', line)
					line = line + ','
					text += line
					if line != lines[-1]:
						text += '\n'
				with open(os.path.join(outdir, root_part_path, des_file_name), 'w') as wf:
					wf.write(text)

if __name__=='__main__':
	import argparse
	ap = argparse.ArgumentParser()
	ap.add_argument("--indir", help="indir")
	ap.add_argument("--outdir", help="outdir")
	args= vars(ap.parse_args())
	edit_des_file(args["indir"], args["outdir"])