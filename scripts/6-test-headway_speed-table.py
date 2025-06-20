import pandas as pd
import matplotlib.pyplot as plt
import glob
import re
import os

# Set up mapping for speed to color and headway to line style
speed_colors = {10: 'tab:blue', 20: 'tab:orange', 30: 'tab:green'}
headway_styles = {0.6: 'solid', 0.9: 'dashed', 1.2: 'dotted'}

directory = "../output_transitory/raw_follower_cacc/"
all_files = glob.glob(os.path.join(directory, "*.csv"))
pattern = re.compile(
    r"^consensus_cacc_speed\d+_headway\d+(?:\.\d+)?_sinu_topology1_.*\.csv$"
)
files = [f for f in all_files if pattern.match(os.path.basename(f))]
print("Filepaths found:", files)

# Data for plotting
plot_data = {'gap_spacing': {}, 'speed': {}, 'acceleration': {}}

for file in files:
    basename = os.path.basename(file)
    speed = int(basename.split('_')[2].replace('speed', ''))
    headway = float(basename.split('_')[3].replace('headway', ''))

    df = pd.read_csv(file)
    # Filter for vehicle IDs that start with 'p2'
    p2_mask = df['vehicle_id'].str.startswith('p2')
    df_p2 = df[p2_mask]

    # Average by timestamp
    label = f"Speed {speed}, Headway {headway}"
    avg_gap = df_p2.groupby('timestamp')['gap_spacing'].mean()
    avg_speed = df_p2.groupby('timestamp')['speed'].mean()
    avg_acc = df_p2.groupby('timestamp')['acceleration'].mean()

    plot_data['gap_spacing'][label] = (avg_gap.index, avg_gap.values, speed, headway)
    plot_data['speed'][label] = (avg_speed.index, avg_speed.values, speed, headway)
    plot_data['acceleration'][label] = (avg_acc.index, avg_acc.values, speed, headway)

for metric, ylabel in zip(['gap_spacing', 'speed', 'acceleration'],
                          ['Average Gap Spacing (m)', 'Average Speed (m/s)', 'Average Acceleration (m/s²)']):
    plt.figure(figsize=(10, 6))
    for label, (x, y, speed, headway) in plot_data[metric].items():
        plt.plot(x, y,
                 label=label,
                 color=speed_colors[speed],
                 linestyle=headway_styles[headway],
                 linewidth=2)
    plt.xlabel('Time (s)')
    plt.ylabel(ylabel)
    plt.title(f"Time vs. {ylabel} for p2 Vehicles")
    plt.legend(title='Condition')
    plt.tight_layout()
    plt.show()

import pandas as pd
import numpy as np
import glob
import os
import re

speeds = [10, 20, 30]
headways = [0.6, 0.9, 1.2]
scenarios = ["sinu"]
leader_controller = "consensus"
follower_controller = "cacc"
base_dir = f"../output_transitory/raw_follower_{follower_controller}"
plot_dir = "../output_transitory/plots"
os.makedirs(plot_dir, exist_ok=True)
summary_rows = []

for scenario in scenarios:
    for speed in speeds:
        for headway in headways:
            pattern = f"{leader_controller}_{follower_controller}_speed{speed}_headway{headway}_{scenario}_topology1_*.csv"
            filepaths = sorted(glob.glob(os.path.join(base_dir, pattern)))
            if not filepaths:
                print(f"No file found for speed={speed}, headway={headway}")
                continue
            for filepath in filepaths:
                df = pd.read_csv(filepath)
                expected_end_time = 100
                if scenario == 'brake':
                    df = df[df['timestamp'] < 59]
                    expected_end_time = 58.9
                topology_type = re.search(r'topology(\d+)', filepath).group(1)
                df = df[df['timestamp'] > 15]
                p2veh1 = df[df['vehicle_id'] == 'p2veh1'].copy()
                if scenario == 'brake':
                    cond_leader = (np.abs(p2veh1['gap_spacing'] - p2veh1['safe_distance']) < 15)
                else:
                    cond_leader = (np.abs(p2veh1['gap_spacing'] - p2veh1['safe_distance']) < 0.5)
                leader_merge_times = p2veh1.loc[cond_leader, 'timestamp']
                other_p2 = df[(df['vehicle_id'].str.startswith('p2')) & (df['vehicle_id'] != 'p2veh1')]
                full_merge_time = None
                for t in leader_merge_times:
                    group = other_p2[other_p2['timestamp'] == t]
                    if not group.empty:
                        mean_gap = group['gap_spacing'].mean()
                        mean_safe = group['safe_distance'].mean()
                        if abs(mean_gap - mean_safe) < 10:
                            full_merge_time = t
                            print(f"Full merged at t={t:.2f} (leader merged & all p2 mean gap≈safe_dist)")
                            break
                if leader_merge_times.empty:
                    print("No leader-merged time found.")
                if full_merge_time is None:
                    print("No full-merged time found.")
                merged_time = full_merge_time if full_merge_time is not None else 0
                t_end = merged_time + 5 if merged_time != 0 else df['timestamp'].max()
                time_filter = df['timestamp'] <= t_end
                mask_p2 = df['vehicle_id'].str.startswith('p2')
                df_p2 = df[mask_p2 & time_filter]
                jerk_vals = df_p2['jerk']
                jerk_rms = np.sqrt(np.mean(jerk_vals ** 2)) if not jerk_vals.empty else np.nan
                jerk_max = jerk_vals.max() if not jerk_vals.empty else np.nan
                jerk_min = jerk_vals.min() if not jerk_vals.empty else np.nan
                min_gap_p2veh1 = p2veh1['gap_spacing'].min() if not p2veh1.empty else np.nan
                mask_p2f = mask_p2 & (df['vehicle_id'] != 'p2veh1') & time_filter
                avg_gap_spacing_others = df[mask_p2f]['gap_spacing'].mean() if not df[mask_p2f].empty else np.nan
                crash_flag = False
                if df['timestamp'].max() < expected_end_time - 2:
                    print(f"Likely crash in {filepath}: max timestamp is {df['timestamp'].max():.2f}")
                    crash_flag = True
                max_timestamp = df['timestamp'].max()
                summary_rows.append({
                    "leader_controller": leader_controller,
                    "follow_controller": follower_controller,
                    "scenario": scenario,
                    "topology": topology_type,
                    "speed": speed,
                    "headway": headway,
                    "leader_merged_time": leader_merge_times.iloc[0] if not leader_merge_times.empty else np.nan,
                    "full_merged_time": full_merge_time,
                    "jerk_rms": jerk_rms,
                    "jerk_max": jerk_max,
                    "jerk_min": jerk_min,
                    "min_gap_p2veh1": min_gap_p2veh1,
                    "avg_gap_spacing_p2_others": avg_gap_spacing_others,
                    "crash": crash_flag,
                    "max_timestamp": max_timestamp
                })

summary_df = pd.DataFrame(summary_rows)
print(summary_df)
summary_df.to_csv(os.path.join(plot_dir, f"6-consensus-cacc.csv"), index=False)
