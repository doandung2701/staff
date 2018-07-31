h,w = (10,10)
floodFill_mask = np.zeros((h+2, w+2), np.uint8)
floodFill_mask[1:-1,1:-1][4,4] = 1
predict_time = np.ones((h,w), dtype='uint8')
expand_window = (3,3,5,5)
expand_topleft_x, expand_topleft_y, expand_w, expand_h = expand_window
predict_time[expand_topleft_y:expand_topleft_y+expand_h, expand_topleft_x:expand_topleft_x+expand_w]\
  [floodFill_mask[1:-1,1:-1][expand_topleft_y:expand_topleft_y+expand_h, expand_topleft_x:expand_topleft_x+expand_w] == 1] +=3
predict_time
 
 
