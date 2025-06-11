import os
import time
import csv

def initialize_logging(controller1, controller2, speed, headway, disturbance, scenario_type, timestamp_file, topology, method,inter_gap,simulation_size):
    """
    Initializes logging for the simulation and creates a CSV file to store vehicle data.
    """


    if(method == "baseline"): output_folder="output"
    elif(method == "transitory"): output_folder="output_transitory"

    if scenario_type == "two_platoon":
        log_dir = f"{output_folder}/two_platoon/raw_follower_{controller2}"
        file_name = f"{controller1}_{controller2}_speed{speed}_headway{headway}_{disturbance}_topology{topology}_mergingDist{inter_gap}_size{simulation_size}_{timestamp_file}.csv"
    else:
        log_dir = f"{output_folder}/one_platoon/raw_{controller1}"
        file_name = f"{controller1}_speed{speed}_headway{headway}_{disturbance}_topology{topology}_{timestamp_file}.csv"

    os.makedirs(log_dir, exist_ok=True)
    file_path = os.path.join(log_dir, file_name)

    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "vehicle_id", "speed", "acceleration", "jerk", "gap_spacing", "safe_distance", "ego_pos","leader_pos","d_safe_leader","gap2leader","leader_mode"])

    return file_path


def log_vehicle_data(file_path, timestamp, veh_id, ego_speed, ego_accel, prev_accel, d_gap, d_safe, ego_pos,leader_pos,d_safe_leader,gap2leader, leader_mode):
    
    jerk = (ego_accel - prev_accel) / 0.1
    formatted_data = [
        f"{timestamp:.4f}", 
        veh_id, 
        f"{ego_speed:.4f}", 
        f"{ego_accel:.4f}", 
        f"{jerk:.4f}", 
        f"{d_gap:.4f}", 
        f"{d_safe:.4f}",
        f"{ego_pos:.4f}",
        f"{leader_pos:.4f}",
        f"{d_safe_leader:.4f}",
        f"{gap2leader:.4f}",
        leader_mode
    ]
        # Open the file in append mode and log the data
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(formatted_data)
