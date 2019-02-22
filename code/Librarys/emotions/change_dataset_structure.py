import os
import glob
import cv2
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

def preprocessing(indir, outdir, img_size=100):
	folder = indir
	if os.path.exists(outdir):
		os.system("rm -rf " + outdir)
	os.mkdir(outdir)

		
	all_file_paths, all_emotions = [], []
	people = os.listdir(folder)
	for person in people:
		if not os.path.isdir(os.path.join(folder, person)):
			print("Skip %s beacause of not a directory", person)
			continue
		print("#person: ", person)
		movies = os.listdir(os.path.join(folder, person))
		for movie in movies:
			if not os.path.isdir(os.path.join(folder, person, movie)):
				print("Skip %s beacause of not a directory", movie )
				continue
			print("#movie: %s, of person: %s", movie, person)
			images_path = os.path.join(os.path.join(folder, person, movie, "images"))
			
			
			if os.path.isdir(images_path):
				img_file_names, emotions_of_file_name = os.listdir(images_path), dict()
				img_paths = [os.path.join(os.path.join(folder, person, movie, "images", file_name)) for file_name in img_file_names]
				print("#img file names = ", img_file_names)
				movie_path = os.path.join(os.path.join(folder, person, movie))
				print("os.listdir(movie_path): ", os.listdir(movie_path))
				# files = list(filter(endswith('.txt'),os.listdir(movie_path)))
				files = glob.glob(movie_path + '/*.txt')
				print(files)
				if len(files) != 1:
					print('Skip movie because of assert len(files) == 1!!!!')
					continue
				infor_file = files[0]
				with open(infor_file) as f:
					lines = f.readlines()
					print(lines)
					for line in lines:
						print('line=', line)
						print('line.split() = ', line.split('\t'))
						colums = line.split('\t')
						if len(colums) > 11:
							emotions_of_file_name[colums[2]]=colums[11]
				print("emotions_of_file_name: ", emotions_of_file_name)
				emotions = []
				for file_path in img_paths:
					file_name = os.path.split(file_path)[1]
					if file_name in emotions_of_file_name.keys():
						emotions.append(emotions_of_file_name[file_name])
					else:
						print("REMOVE: ", file_name)
						img_paths.remove(file_path)
				# emotions = [emotions_of_file_name[] for file_path in img_paths]
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
		assert one_type_emotions.count(one_type_emotions[0]) == len(one_type_emotions)
		emotion = one_type_emotions[0]
		print("emotion = ", emotion)
		print("all_file_paths_of_emotion = ", all_file_paths_of_emotion)
		emotion_folder = os.path.join(outdir, emotion)
		os.system("mkdir " + emotion_folder)
		for file_path_of_emotion in all_file_paths_of_emotion:
			os.system("cp " + file_path_of_emotion + ' ' + emotion_folder)
		for img_path in glob.glob(emotion_folder + '/*'):
			img = cv2.imread(img_path)
			resized_img = cv2.resize(img, (100, 100))
			cv2.imwrite(img_path, resized_img)
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
    preprocessing(args["indir"], args["outdir"])
    # main(args["outdir"])