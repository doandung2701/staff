mog = cv2.BackgroundSubtractorMOG(history=50, nmixtures=3, backgroundRatio=0.8)
if imutils.is_cv2():
  mog = cv2.BackgroundSubtractorMOG(history=50, nmixtures=3, backgroundRatio=0.8)
elif imutils.is_cv3():
  mog = cv2.bgsegm.createBackgroundSubtractorMOG(history=50, nmixtures=3, backgroundRatio=0.8)
