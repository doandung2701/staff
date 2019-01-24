def update_drawed_regions((x1,y1), (x2,y2), (x3,y3), (x4, y4), (x_nose, y_nose), drawed_regions, frame):
    sl.draw_points(frame, [(x_nose,y_nose)], (0, 255, 0), radius=10, thickness=10)
    four_points = (x1,y1), (x2,y2), (x3,y3), (x4, y4)
    x_intersec, y_intersec = sl.center_of_4points(four_points)
    vector = (x_nose-x_intersec, y_nose-y_intersec)
    angle = sl.calculate_angle_vector_and_vertical_vector(vector)
    vector_length = np.linalg.norm(vector)
    region_number = int(angle/(math.pi/4))
    radius = max((r-l)*1, (b-t)*1)
    box = (c_x, c_y), (w, h), angle = ((l+r)//2, (b+t)//2), (radius*2, radius*2), 0
    cv2.ellipse(frame, box, (0, 0, 255), 100)
    frame =	cv2.arrowedLine(frame, (x_intersec, y_intersec), (x_nose, y_nose), color=(0,0,255), thickness=10)
    if (region_number not in [0,1,6,7] and vector_length > 40) or (region_number in [0,1,6,7] and vector_length > 5):
        for i in range(3):
            angle_i = (regions[region_number][0] + 15*i)/180.0*math.pi
            draw_point = int(c_x + math.sin(angle_i)*radius), int(c_y + math.cos(angle_i)*radius)
            if region_number not in drawed_regions:
                drawed_regions.append(region_number)
    for region_number in drawed_regions:
        for i in range(3):
            angle_i = (regions[region_number][0] + 15*i)/180.0*math.pi
            draw_point = int(c_x + math.sin(angle_i)*radius), int(c_y + math.cos(angle_i)*radius)
            sl.draw_points(frame, [draw_point], color=(0, 255, 0), radius=15, thickness=50)
