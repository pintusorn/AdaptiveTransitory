import os
import argparse
import traci
import time
import csv
import math
import numpy as np
import pandas as pd
import re
from datetime import datetime

from config.parser import parse_arguments
from controllers import cacc_controller, pid_controller, consensus_controller, hinf_controller, dmpc_controller, calculate_hinf_gain
from utils.logging_utils import initialize_logging, log_vehicle_data
from utils.rou_utils import generate_rou_file
from utils.plot_utils import plot_results

args = parse_arguments()
simulation_size = args.size
platoon1_controller = args.platoon1
platoon2_controller = args.platoon2 if args.platoon2 else None

topology = args.topology
topology_adapt = topology
headway = args.headway
headway_adapt = headway
speed = args.speed
inter_gap = args.inter_gap
disturbance = args.disturbance
gap = int(speed * headway) + 4
time_step = 0.01
num_veh = math.floor(simulation_size / 2)
step = 0
flag_merge = 0
flag_disturbance = 0
if disturbance == "sinu": max_step = args.total_time
elif disturbance == "brake": max_step = args.total_time
elif disturbance == "speed_up": max_step = args.total_time
elif disturbance == "slow_down": max_step = args.total_time
else: max_step = args.total_time
prev_accel_dict = {}
int_gap_error = 0
leader_mode = "none"

transitory_switch = 0

generate_rou_file(args.scenario_type, simulation_size, num_veh, gap, inter_gap, speed, headway, disturbance, platoon1_controller, platoon2_controller)

def record_prev_accel(vehicle_id, accel_val):
    """
    Records the last acceleration of the given vehicle.
    """
    global prev_accel_dict
    prev_accel_dict[vehicle_id] = accel_val

def get_prev_accel(vehicle_id):
    """
    Retrieves the last acceleration of the given vehicle.
    Returns 0 if the vehicle has no previous record.
    """
    global prev_accel_dict
    return prev_accel_dict.get(vehicle_id, 0)

# Generate platoon IDs dynamically
def define_platoon(prefix, size):
    return [f"{prefix}veh{i+1}" for i in range(size // 2)]

platoon1 = define_platoon("p1", simulation_size)
platoon2 = define_platoon("p2", simulation_size) if platoon2_controller else []

# Setup SUMO binary
sumo_binary = "sumo-gui" if args.gui else "sumo"
if args.scenario_type == "two_platoon":
    sumoCmd = [sumo_binary, "-c", f"network/two_platoon/two_platoon_{simulation_size}.sumocfg"]
else:
    sumoCmd = [sumo_binary, "-c", f"network/one_platoon/one_platoon_{simulation_size}.sumocfg"]

traci.start(sumoCmd)
if args.gui:
    traci.gui.setZoom("View #0", 2500)
    traci.gui.trackVehicle("View #0", "p1veh1")

timestamp_file = time.strftime("%Y%m%d-%H%M%S")

log_file = initialize_logging(platoon1_controller, platoon2_controller, speed, headway, disturbance, args.scenario_type, timestamp_file, topology, args.method, inter_gap, simulation_size)

flag_merge_time=0

def get_controller_function(veh_id, controller, platoon, leader_id, headway):
    global int_gap_error, flag_merge_time, leader_mode, transitory_switch

    if controller == "dmpc": time_step = 0.1
    else: time_step = 0.01

    ego_speed = traci.vehicle.getSpeed(veh_id)
    ego_accel = traci.vehicle.getAcceleration(veh_id)
    ego_pos = traci.vehicle.getPosition(veh_id)[0]

    pred_speed = traci.vehicle.getSpeed(platoon[platoon.index(veh_id) - 1])
    pred_accel = traci.vehicle.getAcceleration(platoon[platoon.index(veh_id) - 1])
    pred_pos = traci.vehicle.getPosition(platoon[platoon.index(veh_id) - 1])[0]

    leader_speed = traci.vehicle.getSpeed(leader_id) 
    leader_accel = traci.vehicle.getAcceleration(leader_id)
    leader_pos = traci.vehicle.getPosition(leader_id)[0]
    most_leader_pos = traci.vehicle.getPosition("p1veh1")[0]



    d_gap = max(0, traci.vehicle.getPosition(platoon[platoon.index(veh_id) - 1])[0] - traci.vehicle.getPosition(veh_id)[0])

    d_safe = max((headway * ego_speed) + 4,14)
    veh_num = platoon.index(veh_id)
    d_gap_leader = leader_pos - ego_pos
    d_safe_leader = (d_safe * (veh_num))

    # Calculate errors
    gap_error = d_gap - d_safe
    if(veh_id == "p2veh1" and gap_error < 0.5 and flag_merge_time == 0):

            print("merging time is at ", step)
            flag_merge_time = 1
    int_gap_error = int_gap_error + (gap_error * 0.01)
    speed_error = pred_speed - ego_speed
    accel_error = pred_accel - ego_accel
    leader_speed_diff = leader_speed - ego_speed
    leader_accel_diff = leader_accel - ego_accel
    adaptive_factor = np.tanh(abs(gap_error) / 5) * (1 - np.tanh(abs(leader_accel_diff) / 3))


    if controller == "cacc":
        a_des = cacc_controller(ego_speed, ego_accel, pred_speed, pred_accel, leader_accel, d_gap, d_safe)

    elif controller == "hinf":
        a_des = hinf_controller(gap_error, speed_error, accel_error, leader_speed_diff, d_gap_leader, d_safe_leader, leader_accel_diff)

    elif controller == "pid":
        a_des = pid_controller(ego_speed, pred_speed, pred_accel, leader_speed, leader_accel, d_gap, d_safe, d_gap_leader, d_safe_leader)

    elif controller == "consensus":
        a_des = consensus_controller(veh_num, ego_speed, leader_speed, d_gap, d_safe, d_gap_leader, d_safe_leader)

    elif controller == "dmpc":
        a_des = dmpc_controller(veh_num, ego_speed, ego_pos, pred_speed, pred_pos, pred_accel, leader_speed, leader_pos, leader_accel, d_safe, get_prev_accel(leader_id), get_prev_accel(f"p1veh{int(veh_id[-1]) - 1}"))

    if(args.method == "transitory" and veh_id == "p2veh1"):
        if(flag_merge_time == 0):
            if(transitory_switch == 0):

                if(ego_speed-leader_speed > 5):
                    transitory_switch = 1
                else: 
                    transitory_switch = 2
                
        
            if(transitory_switch == 1 and platoon2_controller != "dmpc"):
                leader_mode = "dmpc"
                time_step = 0.1
                a_des = dmpc_controller(veh_num, ego_speed, ego_pos, pred_speed, pred_pos, pred_accel, leader_speed, leader_pos, leader_accel, d_safe, get_prev_accel(leader_id), get_prev_accel(f"p1veh{int(veh_id[-1]) - 1}"))
            elif(transitory_switch == 2 and platoon2_controller != "cacc"):
                leader_mode = "cacc"
                time_step = 0.01
                a_des = cacc_controller(ego_speed, ego_accel, pred_speed, pred_accel, leader_accel, d_gap, d_safe)
    
    a_max = 25.5 
    a_min = -300.5 

    a_des_limit = max(min(a_des, a_max), a_min)

    traci.vehicle.setAcceleration(veh_id, a_des_limit, time_step)

    log_vehicle_data(log_file, traci.simulation.getTime(), veh_id, ego_speed, ego_accel, get_prev_accel(veh_id), d_gap, d_safe, ego_pos,leader_pos,d_safe_leader,most_leader_pos-ego_pos,leader_mode)

while step < max_step:
    traci.simulationStep()
    # print("step:", step)
    for veh_id in platoon1:
        if veh_id in traci.vehicle.getIDList():
            # Disable automatic speed and lane management
            traci.vehicle.setSpeedMode(veh_id, 0)  
            traci.vehicle.setLaneChangeMode(veh_id, 0)  

            # Set the deceleration explicitly and eliminate driver imperfection
            traci.vehicle.setDecel(veh_id, 5.0)   
            traci.vehicle.setImperfection(veh_id, 0.0)  


            if veh_id == "p1veh1":
                traci.vehicle.setSpeedMode(veh_id, 0)

                ego_speed = traci.vehicle.getSpeed(veh_id)
                ego_accel = traci.vehicle.getAcceleration(veh_id)
                ego_pos = traci.vehicle.getPosition(veh_id)[0]
                log_vehicle_data(log_file, traci.simulation.getTime(), veh_id, ego_speed, ego_accel, get_prev_accel(veh_id), 0, 0, ego_pos, ego_pos,0,0,leader_mode)


                if flag_disturbance == 1:
                    # print("should be in here now for sinu")
                    if disturbance == "brake":
        
                        current_speed = traci.vehicle.getSpeed(veh_id)
                        target_speed = max(0, current_speed - 0.5)  # Reduce speed by 0.5 m/s each step
                        traci.vehicle.setSpeed(veh_id, target_speed)

                        # print("Brake!!!! with id ", veh_id, " | traci.vehicle.getAcceleration(veh_id): " , traci.vehicle.getAcceleration(veh_id))
                    elif disturbance == "sinu":
                        frequency = 1/20
                        omega = 2 * math.pi * frequency
                        amplitude = 2.5
                        current_time = traci.simulation.getTime()
                        acceleration = amplitude * math.sin(omega * current_time - math.pi-0.60)
                        traci.vehicle.setAcceleration("p1veh1", acceleration, time_step)
                    
                    record_prev_accel(veh_id, traci.vehicle.getAcceleration(veh_id))
                else:
                    traci.vehicle.setSpeed("p1veh1", speed)
                    record_prev_accel(veh_id, traci.vehicle.getAcceleration(veh_id))
            else:
                leader_id = "p1veh1"
                get_controller_function(veh_id, platoon1_controller, platoon1, leader_id, headway)
                record_prev_accel(veh_id, traci.vehicle.getAcceleration(veh_id))

        else:
            print(f"Vehicle {veh_id} not in simulation yet.")

    if args.platoon2: 
        for veh_id_2 in platoon2:
            if veh_id_2 in traci.vehicle.getIDList():
                traci.vehicle.setSpeedMode(veh_id_2, 0)  # Disable automatic speed management
                traci.vehicle.setLaneChangeMode(veh_id_2, 0)  # Disable automatic lane change safety
                traci.vehicle.setImperfection(veh_id_2, 0.0)  # Eliminate driver imperfection
                traci.vehicle.setDecel(veh_id_2, 0.0)  # Set deceleration to zero (not recommended)
                if veh_id_2 == "p2veh1": 
                    if flag_merge == 0:
                        traci.vehicle.setSpeed(veh_id_2, speed)
                        # print("step: " , step , " | speed of p2veh1: ", traci.vehicle.getSpeed(veh_id_2) )
                        record_prev_accel(veh_id_2, traci.vehicle.getAcceleration(veh_id_2))
                        ego_speed = traci.vehicle.getSpeed(veh_id_2)
                        ego_accel = traci.vehicle.getAcceleration(veh_id_2)
                        ego_pos = traci.vehicle.getPosition(veh_id_2)[0]
                        log_vehicle_data(log_file, traci.simulation.getTime(), veh_id_2, ego_speed, ego_accel, get_prev_accel(veh_id_2), traci.vehicle.getPosition("p1veh1")[0] - traci.vehicle.getPosition(veh_id_2)[0], 0, ego_pos, ego_pos,0,0,leader_mode)

                    elif flag_merge == 1:
                        leader_id = platoon1[-1]

                        if (topology_adapt == 1):
                            
                            platoon_inter = [leader_id,"p2veh1"]
                            get_controller_function(veh_id_2, platoon2_controller, platoon_inter, leader_id, headway_adapt)
                            
                        elif (topology_adapt == 3):
                            
                            platoon_inter  = [platoon1[-1]] + platoon2
                            get_controller_function(veh_id_2, platoon2_controller, platoon_inter, leader_id, headway_adapt)
                        
                        record_prev_accel(veh_id_2, traci.vehicle.getAcceleration(veh_id_2))
                            
                else:
                 
                    if(flag_merge == 1 and topology_adapt ==3):
                        leader_id = platoon1[-1]
                        platoon_inter  = [platoon1[-1]] + platoon2
                        get_controller_function(veh_id_2, platoon2_controller, platoon_inter, leader_id, headway_adapt)
                    
                    else:
                        leader_id = "p2veh1"
                        get_controller_function(veh_id_2, platoon2_controller, platoon2, leader_id, headway_adapt)
                    record_prev_accel(veh_id_2, traci.vehicle.getAcceleration(veh_id_2))
            else:
                print(f"Vehicle {veh_id_2} not in simulation yet.")
        
    if step > args.merging_time and flag_merge == 0:

        flag_merge = 1
    
    if step > args.disturbance_time and flag_disturbance == 0:
        flag_disturbance = 1


    time.sleep(time_step)
    step += time_step

traci.close()
print("Simulation ended.")

if args.method == "baseline": output_folder = "output"
elif args.method == "transitory": output_folder = "output_transitory"

# else: output_folder = "output"

# Define directories and file names
if args.scenario_type == "two_platoon":
    log_dir = f"{output_folder}/two_platoon/raw_follower_{platoon2_controller}"
    save_dir = f"{output_folder}/two_platoon/plots_follower_{platoon2_controller}"
    file_name_base = f"{platoon1_controller}_{platoon2_controller}_speed{speed}_headway{headway}_{disturbance}_topology{topology}_mergingDist{inter_gap}_size{simulation_size}"

else:
    
    log_dir = f"{output_folder}/one_platoon/raw_{platoon1_controller}"
    save_dir = f"{output_folder}/one_platoon/plots_{platoon1_controller}"
    file_name_base = f"{platoon1_controller}_speed{speed}_headway{headway}_{disturbance}_topology{topology}"
os.makedirs(log_dir, exist_ok=True)
    
file_path = os.path.join(log_dir, f"{file_name_base}_{timestamp_file}.csv")
output_path = os.path.join(save_dir, f"{file_name_base}.csv")

plot_results(file_path, output_path, args.plot)

