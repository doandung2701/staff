from sklearn import model_selection, svm
import cv2 

def svm_classify(X, Y):
    svc = svm.SVC(probability=True, kernel='linear', class_weight='balanced')
    parameters = {'C': [0.1, 1, 2]}
    gs_model = model_selection.GridSearchCV(svc, parameters, n_jobs=-1)
    gs_model.fit(X, Y)
    return gs_model

def get_person_images(idx, idx2path):
    return [cv2.imread(path) for path in idx2path[idx]]