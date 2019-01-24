# -*- coding: utf-8 -*-

import bottleneck as bn
from sklearn import model_selection, svm
import numpy as np
import util
DEBUG = False

def known_novelty_split_data(inclass_X, inclass_Y, known_class_set):
    inclass_X_known, inclass_Y_known = [], []
    inclass_X_novelty, inclass_Y_novelty = [], []
    for inclass_x, inclass_y in zip(inclass_X, inclass_Y):
        if inclass_y in known_class_set:
            inclass_X_known.append(inclass_x)
            inclass_Y_known.append(inclass_y)
        else:
            inclass_X_novelty.append(inclass_x)
            inclass_Y_novelty.append(inclass_y)
    return (inclass_X_known, inclass_Y_known), (inclass_X_novelty, inclass_Y_novelty)


def inclass_data_to_data(inclass_X, inclass_Y=None):
    X = []
    Y = []
    for i in range(len(inclass_X)):
        inclass_x = inclass_X[i]
        X.extend(inclass_x)
        if inclass_Y is not None:
            inclass_y = inclass_Y[i]
            Y.extend([inclass_y] * len(inclass_x))
    if inclass_Y is not None:
        return np.array(X), np.array(Y)
    else:
        return np.array(X)


def svm_classify(X, Y):
    svc = svm.SVC(probability=True, kernel='linear', class_weight='balanced')
    parameters = {'C': [0.1, 1, 2]}
    gs_model = model_selection.GridSearchCV(svc, parameters, n_jobs=-1)
    gs_model.fit(X, Y)
    return gs_model


def reindex_classes(classes):
    reindex_dict = dict()
    for new_index, class_element in enumerate(classes):
        reindex_dict[class_element] = new_index
    return reindex_dict


def get_X_of_label(X, Y, label):
    X_of_label = []
    for x, y in zip(X, Y):
        if y == label:
            X_of_label.append(x)
    return np.array(X_of_label)


def sequence_multi_probability_to_represent_element_mutil_probability(sequence_mutil_probability):
    represent_element_mutil_probability = bn.median(sequence_mutil_probability, axis=0)
    return represent_element_mutil_probability


def class_and_probability_for_sequence(sequence_mutil_probability):
    represent_element_mutil_probability = sequence_multi_probability_to_represent_element_mutil_probability(sequence_mutil_probability)
    sequence_class = np.argmax(represent_element_mutil_probability)
    probability = np.max(represent_element_mutil_probability)
    return sequence_class, probability

def get_theta_of_sequence_mutil_probability(sequence_mutil_probability):
    represent_element_mutil_probability = sequence_multi_probability_to_represent_element_mutil_probability(sequence_mutil_probability)
    sorted_represent_element_mutil_probability = sorted(represent_element_mutil_probability)
    theta = sorted_represent_element_mutil_probability[-1] / sorted_represent_element_mutil_probability[-2]
    return theta


def get_sample_number_of_inclass_data(inclass_X):
    sample_number = 0
    for inclass_x in inclass_X:
        sample_number += len(inclass_x)
    return sample_number


class NoveltyDetectionSingle:

    def __init__(self, known_class, novelty_class, new_algorithm=False):
        self.known_class = known_class
        self.novelty_class = novelty_class
        self.theta_os = [0] * len(self.known_class)
        self.reindex_dict = reindex_classes(known_class)
        self.new_algorithm = new_algorithm
    
    def classify_return_probability(self, sequence):
        return self.classify_svm_model.predict_proba(sequence)
    
    
    def get_theta_of_sequence(self, sequence):
        sequence_mutil_probability = self.classify_return_probability(sequence)
        theta = get_theta_of_sequence_mutil_probability(sequence_mutil_probability)
        return theta

    def get_theta_and_result_of_sequence(self, sequence):
        sequence_mutil_probability = self.classify_return_probability(sequence)
        theta = get_theta_of_sequence_mutil_probability(sequence_mutil_probability)
        label, probability = class_and_probability_for_sequence(sequence_mutil_probability)
        return theta, label, probability



    def fit(self, inclass_data_known, inclass_data_novelty):
        (inclass_X_known, inclass_Y_known), (inclass_X_novelty, inclass_Y_novelty)\
         = inclass_data_known, inclass_data_novelty
        known_sample_n,  novelty_sample_n= get_sample_number_of_inclass_data(inclass_X_known), get_sample_number_of_inclass_data(inclass_X_novelty)
        if DEBUG:
            print 'known_sample_n, novelty_sample_n: ', known_sample_n, novelty_sample_n
        test_size = novelty_sample_n
        inclass_X_known_for_classify, inclass_X_known_for_novelty_classify, inclass_Y_known_for_classify, inclass_Y_known_for_novelty_classify \
            = util.train_test_split(inclass_X_known, inclass_Y_known, test_size=test_size)
        if DEBUG:
            print 'known sample for novelty classify: ', get_sample_number_of_inclass_data(inclass_X_known_for_novelty_classify)
        X_known_for_classify, Y_known_for_classify = inclass_data_to_data(inclass_X_known_for_classify, inclass_Y_known_for_classify)
        Y_known_for_classify_reindex = [self.reindex_dict[c] for c in Y_known_for_classify]
        self.classify_svm_model = svm_classify(X_known_for_classify, Y_known_for_classify_reindex)
        
        if not self.new_algorithm:
            # tính các giá trị theta_i (theta_os)
            for label in self.known_class:
                inclass_X_of_label = get_X_of_label(inclass_X_known_for_novelty_classify, inclass_Y_known_for_novelty_classify, label)
                X_of_label = inclass_data_to_data(inclass_X_of_label)
                theta = self.get_theta_of_sequence(X_of_label)
                self.theta_os[self.reindex_dict[label]] = theta
        
        # novelty classify
        novelty_classify_X, novelty_classify_Y = [], []
        for sequence, sequence_label in zip(inclass_X_known_for_novelty_classify, inclass_Y_known_for_novelty_classify):
            theta_s, reindex_label, probability = self.get_theta_and_result_of_sequence(sequence)
            if self.new_algorithm:
                sencond_feature = self.theta_os[reindex_label]
            else:
                sencond_feature = probability
            novelty_classify_X.append([theta_s, sencond_feature])
            novelty_classify_Y.append(0)
        
        for sequence, sequence_label in zip(inclass_X_novelty, inclass_Y_novelty):
            theta_s, reindex_label, _ = self.get_theta_and_result_of_sequence(sequence)
            if self.new_algorithm:
                sencond_feature = self.theta_os[reindex_label]
            else:
                sencond_feature = probability
            novelty_classify_X.append([theta_s, sencond_feature])
            novelty_classify_Y.append(1)
        # training SVM
        self.novelty_model = svm_classify(novelty_classify_X, novelty_classify_Y)

    def predict(self, inclass_X):
        ret = []
        for sequence in inclass_X:
            theta_s, label, probability = self.get_theta_and_result_of_sequence(sequence)
            if self.new_algorithm:
                sencond_feature = self.theta_os[label]
            else:
                sencond_feature = probability
            novelty_classify_X.append([theta_s, sencond_feature])
            ret.append(self.novelty_model.predict([[theta_s, sencond_feature]])[0])
        return ret


class PredictModel:
    def __init__(self, new_algorithm=False):
        self.ensemble = []
        self.new_algorithm = new_algorithm

    def fit(self, inclass_X, inclass_Y):
        class_ids = range(len(set(inclass_Y)))
        splitter = model_selection.KFold(n_splits=10)
        for know_class, novelty_class in splitter.split(class_ids):
            novelty_model = NoveltyDetectionSingle(know_class, novelty_class, self.new_algorithm)
            inclass_data_known, inclass_data_novelty = known_novelty_split_data(inclass_X, inclass_Y, know_class)
            novelty_model.fit(inclass_data_known, inclass_data_novelty)
            self.ensemble.append(novelty_model)

        X, Y = inclass_data_to_data(inclass_X, inclass_Y)
        classify_svm_model = svm_classify(X, Y)
        self.classify_svm_model = classify_svm_model


    def classify_return_probability(self, sequence):
        return self.classify_svm_model.predict_proba(sequence)


    def predict(self, inclass_X):
        ret = []
        for sequence in inclass_X:
            sequence_mutil_probability = self.classify_return_probability(sequence)
            sequence_class, probability = class_and_probability_for_sequence(sequence_mutil_probability)
            
            count = 0
            for novelty_model in self.ensemble:
                if sequence_class in novelty_model.known_class:
                    count += novelty_model.predict([sequence])[0]
            
            if count < 4:  # normal
                ret.append((sequence_class, probability))
            else:  # novelty
                ret.append((-1, count / 10.0))
        return ret
