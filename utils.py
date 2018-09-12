def train_test_split(X, y, test_size):
    class_set = set(y)
    X_svm, X_h, y_svm, y_h = [], [], [], []

    class_svm_count = dict()
    class_h_count = dict()
    for class_element in class_set:
        class_svm_count[class_element] = 0
        class_h_count[class_element] = 0

    for x, y_element in zip(X, y):
        if class_svm_count[y_element] > class_h_count[y_element]:
            X_h.append(x)
            y_h.append(y_element)
            class_h_count[y_element] += 1
        else:
            X_svm.append(x)
            y_svm.append(y_element)
            class_svm_count[y_element] += 1

    curr_test_size = len(y_h)
    ratio = 1.0*curr_test_size / test_size
    assert ratio >= 1
    expected_class_h_count = dict()
    for key, value in class_h_count.items():
        expected_class_h_count[key] = value //ratio
    X_h_new, y_h_new = [], []
    for x, y_element in zip(X_h, y_h):
        if class_h_count[y_element] > expected_class_h_count[y_element] and class_h_count[y_element] >= 2:
            X_svm.append(x)
            y_svm.append(y_element)
            class_h_count[y_element] -= 1
        else:
            X_h_new.append(x)
            y_h_new.append(y_element)
    return X_svm, X_h_new, y_svm, y_h_new
