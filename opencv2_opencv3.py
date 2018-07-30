# sudo pip3 install opencv-contrib-python
if imutils.is_cv2():
  mog = cv2.BackgroundSubtractorMOG(history=50, nmixtures=3, backgroundRatio=0.8)
elif imutils.is_cv3():
  mog = cv2.bgsegm.createBackgroundSubtractorMOG(history=50, nmixtures=3, backgroundRatio=0.8)
  
 
 if imutils.is_cv2():
      contours, _ = cv2.findContours(
          mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  elif imutils.is_cv3():
      _, contours, _ = cv2.findContours(
          mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
