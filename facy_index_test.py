h,w = (10,10)
floodFill_mask = np.zeros((h+2, w+2), np.uint8)
floodFill_mask[1:-1,1:-1][4,4] = 1
floodFill_mask[1:-1,1:-1][4,5] = 1
predict_time = np.ones((h,w), dtype='uint8')
predict_time[2,1:4]=5
predict_time[4,4]=10
len(predict_time[predict_time > 1])
expand_window = (3,3,5,5)
expand_topleft_x, expand_topleft_y, expand_w, expand_h = expand_window
predict_time[expand_topleft_y:expand_topleft_y+expand_h, expand_topleft_x:expand_topleft_x+expand_w]\
  [floodFill_mask[1:-1,1:-1][expand_topleft_y:expand_topleft_y+expand_h, expand_topleft_x:expand_topleft_x+expand_w] == 1] +=3
predict_time
len(predict_time[predict_time > 1])
 
 
