def cacc_controller(ego_speed, ego_accel, pred_speed, pred_accel, leader_accel, d_gap, d_safe):

    kp = 1.88  
    kv = 12 
    ka = 1
    kd = 3 

    # kp = 2
    # kv = 7.2
    # ka = 0.2
    # kd = 0.2
    
    gap_error = d_gap - d_safe
    speed_error = pred_speed - ego_speed
    accel_error = pred_accel - ego_accel
    a_des = (kp * gap_error) + (kv * speed_error) + (ka * leader_accel) + (kd * accel_error)

    return a_des
