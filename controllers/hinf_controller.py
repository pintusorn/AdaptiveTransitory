# controllers/hinf_controller.py

import numpy as np
import cvxpy as cp

def calculate_hinf_gain(A, B1, B2, C1, gamma_d, veh_num):
    
    try:
        # Set the size of Q based on the number of states
        Q = cp.Variable((3, 3), symmetric=True) if veh_num == 1 else cp.Variable((5, 5), symmetric=True)
        alpha = cp.Variable()

        # LMI Formulation
        LMI = cp.bmat([
            [A @ Q + Q @ A.T - alpha * B1 @ B1.T, B2],
            [B2.T, -gamma_d**2 * np.eye(1)]
        ])

        # Constraints and objective
        constraints = [Q >> 0, LMI << 0]
        objective = cp.Minimize(alpha)

        # Solve the LMI problem
        problem = cp.Problem(objective, constraints)
        problem.solve()

        if problem.status == cp.OPTIMAL:
            Q_opt = Q.value
            K = (1/2) * B1.T @ np.linalg.inv(Q_opt)
            return K.flatten()
        else:
            return None
    except Exception as e:
        print(f"H-infinity gain calculation failed: {e}")
        return None


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