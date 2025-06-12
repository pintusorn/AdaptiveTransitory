import pandas as pd
import matplotlib.pyplot as plt
import os

# Load the data
df = pd.read_csv("../output/two_platoon/plots/6-summary_speed20_headway0.9.csv")

# Map controller names (optional: only if needed)
controller_map = {
    'cacc': 'CACC',
    'dmpc': 'DMPC',
    'pid': 'PID',
    'consensus': 'Consensus',
    'hinf': 'H-infinity'
}
df['follow_controller'] = df['follow_controller'].map(controller_map)
df['leader_controller'] = df['leader_controller'].map(controller_map)

# Define unique controllers and scenarios
controllers = sorted(df['follow_controller'].unique())
scenarios = df['scenario'].unique()

# Define metrics and file names
metrics = {
    'jerk_rms': 'rms_jerk_table',
    'min_gap_p2veh1': 'inter_gap_table',
    'leader_merged_time': 'merged_time_table'
}

output_dir = "jpg_tables_labeled"
os.makedirs(output_dir, exist_ok=True)

for scenario in scenarios:
    df_scenario = df[df['scenario'] == scenario]
    grouped = df_scenario.groupby(['follow_controller', 'leader_controller']).mean(numeric_only=True).reset_index()
    for metric, base_filename in metrics.items():
        table = grouped.pivot(index='leader_controller', columns='follow_controller', values=metric)
        table = table.reindex(index=controllers, columns=controllers)

        fig_width = max(6, len(controllers) * 1.2)
        fig_height = max(4, len(controllers) * 0.8 + 1)

        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        ax.axis('off')

        cell_text = []
        for row in table.index:
            row_vals = []
            for col in table.columns:
                val = table.loc[row, col]
                row_vals.append("" if pd.isna(val) else f"{val:.2f}")
            cell_text.append(row_vals)

        tbl = ax.table(
            cellText=cell_text,
            rowLabels=table.index,
            colLabels=table.columns,
            loc='center',
            cellLoc='center'
        )
        tbl.scale(1.2, 1.2)
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(10)

        # Set axis labels
        ax.set_title(f"{metric.replace('_', ' ').title()} – {scenario}", fontsize=12, pad=10)
        ax.text(-0.1, 0.5, "Leader Controller", va='center', rotation='vertical', fontsize=12, transform=ax.transAxes)
        ax.text(0.5, -0.1, "Follower Controller", ha='center', fontsize=12, transform=ax.transAxes)

        plt.tight_layout()
        plt.savefig(f"{output_dir}/{base_filename}_{scenario}.jpg", dpi=300, bbox_inches='tight')
        plt.close()
