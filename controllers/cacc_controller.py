def cacc_controller(ego_speed, ego_accel, pred_speed, pred_accel, leader_accel, d_gap, d_safe):

    """
    Cooperative Adaptive Cruise Control (CACC) controller for vehicle platooning.

    Calculates the desired acceleration for a vehicle based on CACC control law using the ego, predecessor, and leader vehicle states.

    Args:
        ego_speed (float): Ego vehicle speed.
        ego_accel (float): Ego vehicle acceleration.
        pred_speed (float): Preceding vehicle speed.
        pred_accel (float): Preceding vehicle acceleration.
        leader_accel (float): Leader vehicle acceleration.
        d_gap (float): Gap to preceding vehicle.
        d_safe (float): Safe gap to preceding vehicle.

    Returns:
        float: Desired acceleration for the ego vehicle.
    """
    
    kp = 1.88  
    kv = 12 
    ka = 1
    kd = 3 

    gap_error = d_gap - d_safe
    speed_error = pred_speed - ego_speed
    accel_error = pred_accel - ego_accel
    a_des = (kp * gap_error) + (kv * speed_error) + (ka * leader_accel) + (kd * accel_error)

    return a_des
