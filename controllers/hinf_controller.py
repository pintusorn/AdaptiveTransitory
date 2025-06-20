import numpy as np

def hinf_controller(gap_error, speed_error, accel_error, leader_speed_diff, d_gap_leader, d_safe_leader, leader_accel_diff):
    
    K = np.array([1.12*2.122, 3.425, 2.501])
    K = K
    x = np.array([
        gap_error,    
        speed_error,   
        accel_error,  
    ])

    K = np.array([1.12*2.122, 4*3.425, 2.501])
    x2 = np.array([
        d_gap_leader-d_safe_leader,     
        leader_speed_diff,  
        leader_accel_diff,   
    ])

    a_des =  float(np.dot(K, x2)) + float(np.dot(K, x))

    return a_des