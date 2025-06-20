import pandas as pd
import numpy as np
import glob
import os
import re

speed = 20
headway = 0.9
scenarios = ["sinu", "brake", "speed_up", "slow_down", "none"]
leader_controllers = ["dmpc", "pid", "consensus", "hinf", "cacc"]
follower_controllers = ["dmpc", "pid", "consensus", "hinf", "cacc"]
base_dir = "../output/raw_follower_{follower_controller}"
plot_dir = "../output/plots"
os.makedirs(plot_dir, exist_ok=True)
summary_rows = []

for scenario in scenarios:
    for leader_controller in leader_controllers:
        for follower_controller in follower_controllers:
            folder = base_dir.format(follower_controller=follower_controller)
            pattern = f"*{leader_controller}_{follower_controller}_speed{speed}_headway{headway}_{scenario}_topology1_*.csv"

            filepaths = sorted(glob.glob(os.path.join(folder, pattern)))
            if not filepaths:
                continue
            for i, filepath in enumerate(filepaths):
                df = pd.read_csv(filepath)
                expected_end_time = 100
                topology_type = re.search(r'topology(\d+)', filepath).group(1)

                # --- Fast vectorized search for LEADER MERGED ---
                df = df[df['timestamp'] > 15]

                # First, find all timestamps where p2veh1's gap-spacing ≈ safe_distance
                p2veh1 = df[df['vehicle_id'] == 'p2veh1'].copy()
                if scenario == 'brake':
                    cond_leader = (np.abs(p2veh1['gap_spacing'] - p2veh1['safe_distance']) < 15)
                else:
                    cond_leader = (np.abs(p2veh1['gap_spacing'] - p2veh1['safe_distance']) < 0.5)
                leader_merge_times = p2veh1.loc[cond_leader, 'timestamp']

                # Now, for those times, check if all other p2 vehicles also "merge"
                # (mean gap_spacing ≈ mean safe_distance, at that timestamp)

                # Get all other p2 vehicles (except p2veh1)
                other_p2 = df[(df['vehicle_id'].str.startswith('p2')) & (df['vehicle_id'] != 'p2veh1')]

                full_merge_time = None

                for t in leader_merge_times:
                    # All other p2 vehicles at this timestamp
                    group = other_p2[other_p2['timestamp'] == t]
                    if not group.empty:
                        mean_gap = group['gap_spacing'].mean()
                        mean_safe = group['safe_distance'].mean()
                        if abs(mean_gap - mean_safe) < 10:
                            full_merge_time = t
                            print(f"Full merged at t={t:.2f} (leader merged & all p2 mean gap≈safe_dist)")
                            break  # Stop at the first found

                # Results
                if leader_merge_times.empty:
                    print("No leader-merged time found.")
                if full_merge_time is None:
                    print("No full-merged time found.")

                # For metrics, use full_merged_time if available, else whole file
                merged_time = full_merge_time if full_merge_time is not None else 0
                t_end = merged_time + 5 if merged_time != 0 else df['timestamp'].max()
                time_filter = df['timestamp'] <= t_end

                mask_p2 = df['vehicle_id'].str.startswith('p2')
                df_p2 = df[mask_p2 & time_filter]
                jerk_vals = df_p2['jerk']
                jerk_rms = np.sqrt(np.mean(jerk_vals ** 2)) if not jerk_vals.empty else np.nan
                jerk_max = jerk_vals.max() if not jerk_vals.empty else np.nan
                jerk_min = jerk_vals.min() if not jerk_vals.empty else np.nan

                # Min gap spacing for p2veh1
                min_gap_p2veh1 = p2veh1['gap_spacing'].min() if not p2veh1.empty else np.nan

                # Avg gap for other p2
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
summary_df.to_csv(os.path.join(plot_dir, f"6-summary_speed{speed}_headway{headway}.csv"), index=False)
