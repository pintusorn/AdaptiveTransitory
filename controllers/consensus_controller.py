def consensus_controller(veh_num, ego_speed, leader_speed, d_gap, d_safe, d_gap_leader, d_safe_leader):

    if veh_num == 1:
        B = 30
        K_pred =5.41
        K_leader = 0
        d_i = 1
    elif veh_num > 1:
        B = 30
        K_leader = 5.41
        K_pred = 5.41
        d_i = 2
    else:
        B = 45
        K_leader = K_pred = d_i = 0
    # if veh_num == 1:
    #     B = 12
    #     K_pred =2
    #     K_leader = 0
    #     d_i = 1
    # elif veh_num > 1:
    #     B = 12
    #     K_leader = 2
    #     K_pred = 2
    #     d_i = 2
    # else:
    #     B = 25
        K_leader = K_pred = d_i = 0

    # Compute the dynamic error term
    dynamicError = -B * ((ego_speed - leader_speed))

    # Calculate desired distance
    desiredDistance_leader = K_leader * d_safe_leader if veh_num > 1 else 0
    desiredDistance_pred = K_pred * d_safe
    desiredDistance = (-desiredDistance_leader - desiredDistance_pred) / max(d_i, 1)

    # Calculate actual distance
    actualDistance_leader = K_leader * d_gap_leader if veh_num > 1 else 0
    actualDistance_pred = K_pred * d_gap
    actualDistance = (actualDistance_leader + actualDistance_pred) / max(d_i, 1)

    # Final control law for desired acceleration
    a_des = (dynamicError + desiredDistance + actualDistance)

    return a_des
