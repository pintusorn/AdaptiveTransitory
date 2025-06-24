import numpy as np

def hinf_controller(gap_error, speed_error, accel_error, leader_speed_diff, d_gap_leader, d_safe_leader, leader_accel_diff):
    """
    H-infinity controller for vehicle platooning.

    Calculates the desired acceleration for a vehicle based on errors and leader information using two sets of gains.

    Args:
        gap_error (float): Gap error between ego and preceding vehicle.
        speed_error (float): Speed error between ego and preceding vehicle.
        accel_error (float): Acceleration error between ego and preceding vehicle.
        leader_speed_diff (float): Speed difference between leader and ego vehicle.
        d_gap_leader (float): Distance from ego to leader.
        d_safe_leader (float): Safe distance to leader (scaled by vehicle index).
        leader_accel_diff (float): Acceleration difference between leader and ego vehicle.

    Returns:
        float: Desired acceleration for the ego vehicle.
    """
    # Gains for the first state vector
    K1 = np.array([1.12*2.122, 3.425, 2.501])
    x1 = np.array([
        gap_error,    
        speed_error,   
        accel_error,  
    ])

    # Gains for the second state vector
    K2 = np.array([1.12*2.122, 4*3.425, 2.501])
    x2 = np.array([
        d_gap_leader - d_safe_leader,     
        leader_speed_diff,  
        leader_accel_diff,   
    ])

    a_des = float(np.dot(K1, x1)) + float(np.dot(K2, x2))
    return a_des