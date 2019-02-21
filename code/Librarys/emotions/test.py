import os
import glob
class ImageClass():
    "Stores the paths to images for a given class"
    def __init__(self, name, image_paths):
        self.name = name
        self.image_paths = image_paths
  
    def __str__(self):
        return self.name + ', ' + str(len(self.image_paths)) + ' images'
  
    def __len__(self):
        return len(self.image_paths)

def main(paths):
	dataset = get_dataset(paths)
	# print(dataset)

def get_dataset(paths):
	print("##Test function")
	dataset = []
	for path in paths.split(':'):
		print("#path: ", path)
		path_exp = os.path.expanduser(path)
		print("#path_exp: ", path_exp)
		classes = os.listdir(path_exp)
		print('#classes: ', classes)
		classes.sort()
		print('#classes: ', classes)
		nrof_classes = len(classes)
		for i in range(nrof_classes):
			class_name = classes[i]
			facedir = os.path.join(path_exp, class_name)
			if os.path.isdir(facedir):
				images = os.listdir(facedir)
		images.sort()
		images = [img for img in images if img.endswith('.jpg') or img.endswith('.png')]
		image_paths = [os.path.join(facedir,img) for img in images]
		print('class_name: ', class_name)
		print('image_paths: ', image_paths)
		dataset.append(ImageClass(class_name, image_paths))
  
	return dataset

def preprocessing(indir, outdir):
	folder = indir
	all_file_paths, all_emotions = [], []
	people = os.listdir(folder)
	for person in people:
		print("#person: ", person)
		movies = os.listdir(os.path.join(folder, person))
		for movie in movies:
			print("#movie: ", movie)
			images_path = os.path.join(os.path.join(folder, person, movie, "images"))
			
			
			if os.path.isdir(images_path):
				img_file_names, emotions = os.listdir(images_path), []
				img_paths = [os.path.join(os.path.join(folder, person, movie, "images", file_name)) for file_name in img_file_names]
				print("#img file names = ", img_file_names)
				movie_path = os.path.join(os.path.join(folder, person, movie))
				print("???", os.listdir(movie_path))
				# files = list(filter(endswith('.txt'),os.listdir(movie_path)))
				files = glob.glob(movie_path + '/*.txt')
				print(files)
				assert len(files) == 1
				infor_file = files[0]
				with open(infor_file) as f:
					lines = f.readlines()
					print(lines)
					for line in lines:
						print('line=', line)
						print('line.split() = ', line.split('\t'))
						colums = line.split('\t')
						if len(colums) > 11:
							emotions.append(colums[11])
				print("emotions: ", emotions)
				all_file_paths.extend(img_paths)
				all_emotions.extend(emotions)
			else:
				print("!!# failed", person, movie)
	import random
	pairs = list(zip(all_file_paths, all_emotions))
	# random.shuffle(b)
	random.shuffle(pairs)
	from itertools import groupby
	res = [list(v) for l,v in groupby(sorted(pairs, key=lambda x:x[1]), lambda x: x[1])]
	n_class = len(res)
	print(n_class)
	for class_paris in res:
		all_file_paths_of_emotion, one_type_emotions = zip(*class_paris)
		emotion = one_type_emotions[0]
		print("emotion = ", emotion)
		print("all_file_paths_of_emotion = ", all_file_paths_of_emotion)
		emotion_folder = os.path.join(outdir, emotion)
		os.system("mkdir " + emotion_folder)
		for file_path_of_emotion in all_file_paths_of_emotion:
			os.system("cp " + file_path_of_emotion + ' ' + emotion_folder)
	print(res[0])
	# all_file_paths, all_emotions = zip(*pairs)
	# print(all_file_paths)
	# print(all_emotions)
	# mkdir

	


if __name__=='__main__':
    import argparse
    ap = argparse.ArgumentParser()
    # ap.add_argument("--paths", help="paths")
    ap.add_argument("--indir", help="indir")
    ap.add_argument("--outdir", help="outdir")
    args= vars(ap.parse_args())
    # main(args["paths"])
    preprocessing(args["indir"], args["outdir"])