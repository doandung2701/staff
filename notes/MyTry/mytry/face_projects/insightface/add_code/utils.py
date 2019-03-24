from sklearn import model_selection, svm
import cv2 

def svm_classify(X, Y):
    svc = svm.SVC(probability=True, kernel='linear', class_weight='balanced')
    parameters = {'C': [0.1, 1, 2]}
    gs_model = model_selection.GridSearchCV(svc, parameters, n_jobs=-1)
    gs_model.fit(X, Y)
    return gs_model

def get_person_images(idx, idx2path):
    return [cv2.imread(path) for path in idx2path[str(idx)]]

def get_batch_number(datalen, batch_size, floor=False):
	if not floor:
		return int(math.ceil(1.0 * datalen / batch_size))
	else:
		return int(math.floor(1.0 * datalen / batch_size))

def get_slice_of_batch(datalen, batch_size, batch_index, floor=False):
	start = batch_index * batch_size
	if not floor:
		end = min((batch_index + 1) * batch_size, datalen) 
	else:
		if (batch_index + 2) * batch_size > datalen:
			end = datalen
		else:
			end = (batch_index + 1) * batch_size
	return start, end