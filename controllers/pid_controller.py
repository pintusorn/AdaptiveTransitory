def pid_controller(ego_speed, pred_speed, pred_accel, leader_speed, leader_accel, d_gap, d_safe, d_gap_leader, d_safe_leader):
    """
    PID controller for vehicle platooning.

    Calculates the desired acceleration for a vehicle based on PID control using both the leader and predecessor vehicles.

    Args:
        ego_speed (float): Ego vehicle speed.
        pred_speed (float): Preceding vehicle speed.
        pred_accel (float): Preceding vehicle acceleration.
        leader_speed (float): Leader vehicle speed.
        leader_accel (float): Leader vehicle acceleration.
        d_gap (float): Gap to preceding vehicle.
        d_safe (float): Safe gap to preceding vehicle.
        d_gap_leader (float): Gap to leader vehicle.
        d_safe_leader (float): Safe gap to leader vehicle (scaled by vehicle index).

    Returns:
        float: Desired acceleration for the ego vehicle.
    """
    kp_front = 285  
    kp_leader = 120  
    ki_leader = 9  
    ki_front = 67   
    kd = 2.4   

    # Calculate errors
    vel_error_leader = leader_speed - ego_speed
    vel_error_pred = pred_speed - ego_speed
    gap_error = d_gap - d_safe
    gap_error_leader = d_gap_leader - d_safe_leader

    # Acceleration from leader and predecessor
    accel_sum = leader_accel + pred_accel

    # Compute numerator for PID formula
    numerator = (
        accel_sum * kd +
        vel_error_leader * kp_leader +
        vel_error_pred * kp_front +
        gap_error_leader * ki_leader +
        gap_error * ki_front
    )

    # Simplified denominator
    denominator = (0.01*ego_speed)+(2 * kd)

    # Calculated desired acceleration
    a_des = numerator / denominator

    return a_des
