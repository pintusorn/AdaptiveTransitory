import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

plt.rcParams["font.family"] = "Times New Roman"

# Load CSV file
# rms_output_baseline
file_path = "../output/plots/6-summary_speed20_headway0.9.csv"
df = pd.read_csv(file_path)

df = df[~df['scenario'].isin(['slow_down', 'speed_up'])]


controller_order = ['pid', 'cacc', 'consensus', 'hinf', 'dmpc']
df['follow_controller'] = pd.Categorical(df['follow_controller'],
                                         categories=controller_order,
                                         ordered=True)

# Assign consistent colors and hatch patterns
metric_colors = {'jerk_rms': 'orange', 'min_gap_p2veh1': 'lightblue'}
scenarios = sorted(df['scenario'].unique())

hatch_patterns = {
    
    'brake': 'xxxx',
    'none': '',
    'sinu': '///'
    # ,
    # 'slow_down': '.....',
    # 'speed_up': '\\\\\\'
    
}

scenarios = ['none', 'brake', 'sinu']
df = df[df['scenario'].isin(scenarios)]
df['scenario'] = pd.Categorical(df['scenario'], categories=scenarios, ordered=True)

# Calculate mean across different leader_controller for each follow_controller and scenario
df_avg = df.groupby(['follow_controller', 'scenario'], as_index=False)[['jerk_rms', 'min_gap_p2veh1']].mean()
print(df_avg)
# Plot
fig, ax1 = plt.subplots(figsize=(8, 3.2))
# fig, ax1 = plt.subplots_adjust(top=0.72)  # or try top=0.7, 0.65 for even more space
plt.tight_layout(rect=(0, 0, 1, 0.7))  # (left, bottom, right, top as fraction of figure)

ax2 = ax1.twinx()

bar_group_width = 0.85


metrics = ['jerk_rms','min_gap_p2veh1']
n_bars = len(scenarios) * len(metrics)
bar_width = bar_group_width / n_bars

for i, (scenario, scenario_data) in enumerate(df_avg.groupby("scenario")):
    for _, row in scenario_data.iterrows():
        x = list(df['follow_controller'].cat.categories).index(row['follow_controller'])
        for j, metric in enumerate(metrics):
            key_index = i * len(metrics) + j
            x_pos = x - bar_group_width / 2 + key_index * bar_width + bar_width / 2
            value = row[metric]

            # Determine axis and color
            ax = ax1 if metric == 'jerk_rms' else ax2

            # Plot bar
            ax.bar(
                x_pos, value,
                width=bar_width,
                color=metric_colors[metric],
                hatch=hatch_patterns[scenario],
                edgecolor='black'
            )

            ax.text(
                x_pos+0.009, value,
                f" {value:.2f}",
                ha='center', va='bottom',
                fontsize=12,
                rotation=90  # makes the label vertical
            )

controller_name_map = {
    'cacc': 'CACC',
    'hinf': 'H∞',
    'consensus': 'CNS',
    'dmpc': 'DMPC',
    'pid': 'PID'
}

# Final plot settings
ax1.set_xticks(range(len(df['follow_controller'].cat.categories)))
ax1.set_xticklabels([controller_name_map.get(ctrl, ctrl) for ctrl in df['follow_controller'].cat.categories], fontsize=13)

# ax1.set_xticklabels(df['follow_controller'].cat.categories)
ax1.tick_params(axis='both', labelsize=13)
ax2.tick_params(axis='y', labelsize=13)
# If you want jerk_rms on left (primary), merging_time on right:
ax1.set_ylabel("Avg. RMS Jerk (m/s³)", fontsize=14, bbox=dict(facecolor='orange', alpha=0.3, edgecolor='none'))
ax2.set_ylabel("Avg. Inter Gap (m)", fontsize=14, bbox=dict(facecolor='lightblue', alpha=0.3, edgecolor='none'))


# ax2.set_ylabel("RMS Jerk", fontsize=14, bbox=dict(facecolor='orange', alpha=0.3, edgecolor='none'))
# ax1.set_ylabel("Merging Time", fontsize=14, bbox=dict(facecolor='lightblue', alpha=0.3, edgecolor='none'))
ax1.set_xlabel("Joining Controller\n(a)", fontsize=14)
# ax1.set_title("Avg RMS Jerk and Merging Time by Follow Controller ", fontsize=16)

ax1.set_ylim(0, 15)
ax1.set_yticks(range(0, 16, 3))  # Left Y-axis: every 2 units

ax2.set_ylim(0, 29)
ax2.set_yticks(range(0, 31, 5))  # Right Y-axis: every 5 units



scenario_name_map = {
    'none': 'No Disturbance',
    'brake': 'Sudden Braking',
    'sinu': 'Oscillating',
    'slow_down': 'Slow Down',
    'speed_up': 'Speed Up'
}
# Create legends
metric_legend = [mpatches.Patch(color=color, label=metric.replace('_', ' ').title())
                 for metric, color in metric_colors.items()]
# metric_legend = [mpatches.Patch(color=color, label=metric.replace('_', ' ').title())
#                  for metric, color in metric_colors.items()][::-1]


scenario_legend = [
    mpatches.Patch(
        facecolor='white',
        edgecolor='black',
        hatch=hatch_patterns[scen],
        label=scenario_name_map.get(scen, scen)  # fallback to original if not in map
    )
    for scen in scenarios
]


# Rename the metric labels
metric_labels = {
    'min_gap_p2veh1': 'Platoon 2 Leader Avg. Min. Gap Spacing \u2191',
    'jerk_rms': 'Avg. RMS Jerk \u2193'
}

# Create legends using renamed labels
metric_legend = [mpatches.Patch(color=color, label=metric_labels[metric])
                 for metric, color in metric_colors.items()]
# plt.tight_layout()

# Reserve top 35% of figure for legend(s)
# plt.subplots_adjust(top=0.75)  # 0.65 leaves 35% of vertical space above axes
# fig = plt.gcf()
# fig.set_size_inches(fig.get_size_inches()[0], fig.get_size_inches()[1] + 1.0)

# Add legends (these will now be in the whitespace at the top)
leg1 = ax1.legend(
    handles=metric_legend,
    loc="upper center",
    bbox_to_anchor=(0.5, 1.35),
    ncol=len(metric_legend),
    frameon=False,
    fontsize='13',
    title_fontsize='13'
)

leg2 = ax1.legend(
    handles=scenario_legend,
    loc="upper center",
    bbox_to_anchor=(0.5, 1.21),
    ncol=len(scenario_legend),
    frameon=False,
    fontsize='13',
)
ax1.add_artist(leg1)

# ----- Only call plt.tight_layout() AFTER all axes formatting -----
# But do NOT use rect or bbox_inches='tight', or your extra space will be removed!
 # adjust axes, but preserves your manual top space

output_filename = "plot2.jpg"
output_path = os.path.join(os.path.dirname(file_path), output_filename)
# plt.subplots_adjust(top=0.1) 
# plt.text(0.5, 1.05, '', transform=plt.gca().transAxes)  # Forces matplotlib to keep space above

# plt.savefig(output_path, bbox_inches='tight')
# plt.subplots_adjust(top=0.9)  # Adjust this value as needed (max=1.0)

plt.tight_layout() 
# fig = plt.gcf()
# fig.set_size_inches(fig.get_size_inches()[0], fig.get_size_inches()[1] + 1.0)  # add 1 inch height

# plt.savefig(output_path, bbox_inches='tight')



plt.savefig(output_path, dpi=300)
plt.close()