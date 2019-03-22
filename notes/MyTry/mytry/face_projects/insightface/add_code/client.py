
import requests
import json
import cv2

addr = 'http://localhost:18080'
test_url = addr + '/ver'

# prepare headers for http request
content_type = 'image/jpeg'
headers = {'content-type': content_type}
src = tar = '/home/cuongvm/Resources/datasets/faces/vn_celeb_face_recognition/test/7fffa54e8d624ff9aa83f93206028d5d.png'
# src = tar = '/home/cuongvm/Pictures/obama.jpg'
src_img = cv2.imread(src)
tar_img = cv2.imread(tar)
# encode image as jpeg
# _, src_img_encoded = cv2.imencode('.jpg', src_img)
# _, tar_img_encoded = cv2.imencode('.jpg', tar_img)
# send http request with image and receive response
# response = requests.post(test_url, data=img_encoded.tostring(), headers=headers)
# data = {'source': src_img_encoded.tostring(), 'target': tar_img_encoded.tostring()}
data = {'source': {'url': src}, 'target': {'url': tar}}

data = json.dumps(data, encoding='latin1')
print('data: ', data)
response = requests.post(test_url, data=data, headers=headers)
# decode response
print(json.loads(response.text))

# expected output: {u'message': u'image received. size=124x124'}