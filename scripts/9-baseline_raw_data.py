import pandas as pd

# Load the data
df = pd.read_csv("../output/two_platoon/plots/6-summary_speed20_headway0.9.csv")

# Define unique controllers and scenarios
controllers = sorted(df['follow_controller'].unique())
scenarios = df['scenario'].unique()

# Define metrics and base file names
metrics = {
    'jerk_rms': 'rms_jerk_table',
    'min_gap_p2veh1': 'inter_gap_table',
    # 'avg_gap_spacing_p2_others': 'intra_gap_table',
    'leader_merged_time': 'merged_time_table'
}


# Group and export
for scenario in scenarios:
    df_scenario = df[df['scenario'] == scenario]
    grouped = df_scenario.groupby(['follow_controller', 'leader_controller']).mean(numeric_only=True).reset_index()
    for metric, base_filename in metrics.items():
        table = grouped.pivot(index='leader_controller', columns='follow_controller', values=metric)
        table = table.reindex(index=controllers, columns=controllers)
        table.to_csv(f"{base_filename}_{scenario}.csv")
