def consensus_controller(veh_num, ego_speed, leader_speed, d_gap, d_safe, d_gap_leader, d_safe_leader):
    """
    Consensus-based controller for vehicle platooning.

    Calculates the desired acceleration for a vehicle based on consensus control using both the leader and predecessor vehicles.

    Args:
        veh_num (int): Index of the vehicle in the platoon (1 for first follower).
        ego_speed (float): Ego vehicle speed.
        leader_speed (float): Leader vehicle speed.
        d_gap (float): Gap to preceding vehicle.
        d_safe (float): Safe gap to preceding vehicle.
        d_gap_leader (float): Gap to leader vehicle.
        d_safe_leader (float): Safe gap to leader vehicle (scaled by vehicle index).

    Returns:
        float: Desired acceleration for the ego vehicle.
    """
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

    dynamicError = -B * ((ego_speed - leader_speed))

    desiredDistance_leader = K_leader * d_safe_leader if veh_num > 1 else 0
    desiredDistance_pred = K_pred * d_safe
    desiredDistance = (-desiredDistance_leader - desiredDistance_pred) / max(d_i, 1)

    actualDistance_leader = K_leader * d_gap_leader if veh_num > 1 else 0
    actualDistance_pred = K_pred * d_gap
    actualDistance = (actualDistance_leader + actualDistance_pred) / max(d_i, 1)

    a_des = (dynamicError + desiredDistance + actualDistance)

    return a_des
