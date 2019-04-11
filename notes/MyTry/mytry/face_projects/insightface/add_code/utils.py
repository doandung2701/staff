from sklearn import model_selection, svm
import cv2 , math

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

def tuple2iou(box1, box2):
	bb1, bb2= {}, {}
	bb1['x1'] = box1[0]
	bb1['y1'] = box1[1]
	bb1['x2'] = box1[2]
	bb1['y2'] = box1[3]
	bb2['x1'] = box2[0]
	bb2['y1'] = box2[1]
	bb2['x2'] = box2[2]
	bb2['y2'] = box2[3]
	return get_iou(bb1, bb2)

def get_iou(bb1, bb2):
    """
    Calculate the Intersection over Union (IoU) of two bounding boxes.

    Parameters
    ----------
    bb1 : dict
        Keys: {'x1', 'x2', 'y1', 'y2'}
        The (x1, y1) position is at the top left corner,
        the (x2, y2) position is at the bottom right corner
    bb2 : dict
        Keys: {'x1', 'x2', 'y1', 'y2'}
        The (x, y) position is at the top left corner,
        the (x2, y2) position is at the bottom right corner

    Returns
    -------
    float
        in [0, 1]
    """
    assert bb1['x1'] < bb1['x2']
    assert bb1['y1'] < bb1['y2']
    assert bb2['x1'] < bb2['x2']
    assert bb2['y1'] < bb2['y2']

    # determine the coordinates of the intersection rectangle
    x_left = max(bb1['x1'], bb2['x1'])
    y_top = max(bb1['y1'], bb2['y1'])
    x_right = min(bb1['x2'], bb2['x2'])
    y_bottom = min(bb1['y2'], bb2['y2'])

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    # The intersection of two axis-aligned bounding boxes is always an
    # axis-aligned bounding box
    intersection_area = (x_right - x_left) * (y_bottom - y_top)

    # compute the area of both AABBs
    bb1_area = (bb1['x2'] - bb1['x1']) * (bb1['y2'] - bb1['y1'])
    bb2_area = (bb2['x2'] - bb2['x1']) * (bb2['y2'] - bb2['y1'])

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = intersection_area / float(bb1_area + bb2_area - intersection_area)
    assert iou >= 0.0
    assert iou <= 1.0
    return iou

def get_time_id():
    time_string = str(dt.now())
    cvt_time_string = time_string.split('.')[0].replace(' ', '_').replace(':', '-')
    time_id = cvt_time_string + '_' + str(randint(0, 100000))
    return time_id

	