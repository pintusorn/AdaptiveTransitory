import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import glob
import os
import re
import matplotlib.ticker as ticker
# plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(5))


plt.rcParams['font.family'] = 'Times New Roman'
# plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 20
plt.rcParams['axes.labelsize'] = 20
plt.rcParams['legend.fontsize'] = 30
plt.rcParams['xtick.labelsize'] = 18
plt.rcParams['ytick.labelsize'] = 18

base_dir = "../output_transitory/raw_follower_hinf/"
plot_dir = "../output_transitory/plots"
os.makedirs(plot_dir, exist_ok=True)

all_files = glob.glob(os.path.join(base_dir, "*.csv"))
pattern = re.compile(r"pid_hinf_speed20_headway0\.9_none_topology1_mergingDist200_size\d+.*\.csv")
filepaths = [f for f in all_files if pattern.search(os.path.basename(f))]
print("Filepaths found:", filepaths)

metrics = [
    ("gap2leader", "Gap to Leader (m)"),
    ("speed", "Speed (m/s)"),
    ("acceleration", "Acceleration (m/s²)")
]

def vehicle_id_to_label(vid):
    m = re.match(r'p2veh(\d+)', vid)
    if m:
        return f"{m.group(1)}"
    return vid


for filepath in filepaths:
    df = pd.read_csv(filepath)
    p2_vehicles = df[df['vehicle_id'].str.startswith('p2')]
    unique_p2_ids = p2_vehicles['vehicle_id'].unique()
    m = re.search(r'size(\d+)', filepath)
    size_value = m.group(1) if m else "?"

#     for metric, ylabel in metrics:
#         plt.figure(figsize=(8, 4))
#         N = len(unique_p2_ids)
#         color_map = plt.get_cmap('tab20', N)  # You can change to 'nipy_spectral' or others for more colors

#         for idx, vid in enumerate(unique_p2_ids):
#             thisveh = p2_vehicles[p2_vehicles['vehicle_id'] == vid]
#             label = vehicle_id_to_label(vid)
#             plt.plot(
#                 thisveh['timestamp'], thisveh[metric],
#                 label=label,
#                 color=color_map(idx)
#             )

#         plt.xlabel("Time (s)")
#         plt.ylabel(ylabel)
#         import math
#         ncol = math.ceil(len(unique_p2_ids) / 2)
#         if metric == "speed":
#             plt.legend(
#                 title="Vehicle ID",
#                 ncol=ncol,
#                 loc='upper center',
#                 bbox_to_anchor=(0.5, 1.4),
#                 frameon=False,
#                 handletextpad=0.5,
#                 columnspacing=0.8,
#                 borderaxespad=0.2,
#                 labelspacing=0.3,
#                 borderpad=0.2
#             )


#         plt.xlim(20, 80)
#         plt.tight_layout()


#         plt.tight_layout()
#         # Save file: plots/metric_sizeXX_FILENAME.png
#         filename = os.path.basename(filepath).replace('.csv', f'_{metric}.pdf')
#         savepath = os.path.join(plot_dir, filename)
#         plt.savefig(savepath)
#         plt.close()
#         print(f"Saved: {savepath}")


    for metric, ylabel in metrics:
        plt.figure(figsize=(8, 3))
        leader_label = "Leader of the joining platoon"
        follower_label = "Followers in the joining platoon"
        leader_plotted = False
        follower_plotted = False

        for idx, vid in enumerate(unique_p2_ids):
            thisveh = p2_vehicles[p2_vehicles['vehicle_id'] == vid]
            if vid == 'p2veh1':
                # Only add label to legend once
                label = leader_label if not leader_plotted else "_nolegend_"
                plt.plot(
                    thisveh['timestamp'], thisveh[metric],
                    label=label,
                    color='red',
                    linewidth=2.0
                )
                leader_plotted = True
            else:
                # Only add label to legend once
                label = follower_label if not follower_plotted else "_nolegend_"
                plt.plot(
                    thisveh['timestamp'], thisveh[metric],
                    label=label,
                    color='black',
                    linewidth=1.0
                )
                follower_plotted = True

        # plt.xlabel("Time (s)")
        plt.xlabel("Time (s)")
        plt.ylabel(ylabel)
        import matplotlib.ticker as ticker
        plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(5))

        # plt.ylabel(ylabel)

        if metric == "speed":
            plt.legend(
                loc='upper right',
                frameon=False,
                fontsize=18
            )

        plt.xlim(20, 60)
        plt.tight_layout()
        

        filename = os.path.basename(filepath).replace('.csv', f'_{metric}.pdf')
        savepath = os.path.join(plot_dir, filename)
        plt.savefig(savepath, bbox_inches='tight')
        plt.close()
        print(f"Saved: {savepath}")
