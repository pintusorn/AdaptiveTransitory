import pandas as pd
import numpy as np
import glob
import os
import re

scenarios = ["none"]
leader_controller = "pid"
follower_controller = "hinf"
base_dir = f"../output_transitory/two_platoon/raw_follower_{follower_controller}"
plot_dir = "../output_transitory/two_platoon/plots"
os.makedirs(plot_dir, exist_ok=True)
summary_rows = []

for scenario in scenarios:
    all_files = glob.glob(os.path.join(base_dir, "*.csv"))
    # Change mergingDist to size in regex pattern
    pattern = re.compile(r"pid_hinf_speed20_headway0\.9_none_topology1_mergingDist200_size\d+.*\.csv")
    filepaths = [f for f in all_files if pattern.search(os.path.basename(f))]
    print("Filepaths found:", filepaths)

    summary_rows = []

    for filepath in filepaths:
        # Extract size instead of mergingDist
        m = re.search(r'size(\d+)', filepath)
        size_value = int(m.group(1)) if m else None

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
            "size": size_value,  # changed key here
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
summary_df.to_csv(os.path.join(plot_dir, f"8-pid-hinf.csv"), index=False)
