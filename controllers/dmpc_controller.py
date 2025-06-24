import numpy as np

def dmpc_controller(veh_num, ego_speed, ego_pos, pred_speed, pred_pos, pred_accel, 
                   leader_speed, leader_pos, leader_accel, d_safe, leader_prev_accel, pred_prev_accel):
    """
    Distributed Model Predictive Controller for vehicle following.

    Args:
        veh_num (int): Vehicle index in the platoon.
        ego_speed (float): Ego vehicle speed.
        ego_pos (float): Ego vehicle position.
        pred_speed (float): Preceding vehicle speed.
        pred_pos (float): Preceding vehicle position.
        pred_accel (float): Preceding vehicle acceleration.
        leader_speed (float): Leader vehicle speed.
        leader_pos (float): Leader vehicle position.
        leader_accel (float): Leader vehicle acceleration.
        d_safe (float): Desired safe distance.
        leader_prev_accel (float): Previous acceleration of the leader.
        pred_prev_accel (float): Previous acceleration of the predecessor.

    Returns:
        float: Desired acceleration for the ego vehicle.
    """
    q_d_leader = 10.15    
    q_d_front  = 7   
    q_v_front  = 9    
    q_a_front  = 1.8   
    q_v_leader = 9 
    
    dt = 0.1
    horizon = 4
    j_leader = leader_prev_accel - leader_accel
    j_pred = pred_prev_accel - leader_accel
   
    best_acc = 0.0
    min_cost = float('inf')

    possible_accels = np.arange(-40, 40.1, 0.1)
    for a in possible_accels:
        cost = 0.0
        v_ego, d_ego = ego_speed, ego_pos
        v_pred, d_pred = pred_speed, pred_pos
        v_leader, d_leader = leader_speed, leader_pos
        a_leader = leader_accel
        a_pred = pred_accel

        for k in range(horizon):
            v_ego_next = v_ego + a * dt
            d_ego_next = d_ego + v_ego * dt + 0.5 * a * dt ** 2

            v_pred_next = v_pred + pred_accel * dt
            d_pred_next = d_pred + v_pred * dt + 0.5 * pred_accel * dt ** 2
            a_pred_next = a_pred + (dt * j_pred)

            v_leader_next = v_leader + a_leader * dt
            d_leader_next = d_leader + v_leader * dt + 0.5 * a_leader * dt ** 2
            a_leader_next = a_leader + (dt * j_leader)

            d_pred_next_diff = d_pred_next - d_ego_next - d_safe
            v_pred_next_diff = v_pred_next - v_ego_next
            a_pred_next_diff = a_pred_next - a
            d_leader_next_diff = d_leader_next - d_ego_next - (d_safe * (veh_num))
            v_leader_next_diff = v_leader_next - v_ego_next
            a_leader_next_diff = a_leader_next - a

            cost += (
                (q_d_leader * (d_leader_next_diff ** 2)) +
                (q_d_front * (d_pred_next_diff ** 2)) +
                (q_v_front * (v_pred_next_diff ** 2)) +
                (q_a_front * ((a_leader_next_diff + a_pred_next_diff) / 2) ** 2) + 
                (q_v_leader * (v_leader_next_diff ** 2))
            )
            
            v_ego = v_ego_next
            d_ego = d_ego_next
            v_pred = v_pred_next
            d_pred = d_pred_next
            a_pred = a_pred_next
            v_leader = v_leader_next
            d_leader = d_leader_next
            a_leader = a_leader_next

        if cost < min_cost:
            min_cost = cost
            best_acc = a
            
    a_des = best_acc
   
    return a_des
