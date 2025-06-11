import pandas as pd
import matplotlib.pyplot as plt

def plot_results(file_path, output_path, plot_flag):
    """
    Plots time vs gap spacing, speed, and jerk from the simulation log.
    """
    data = pd.read_csv(file_path)

    # if gap_only or merge_log:
    param = [("gap2leader", "Gap to Leader"),("speed", "Speed"), ("acceleration", "Acceleration")]
    # else: 
    # param = [("gap2leader", "Gap to Leader"), ("speed", "Speed"), ("acceleration", "Acceleration"), ("jerk", "Jerk")]
    for y, ylabel in param:
        save_plot(data, y, ylabel, file_path, output_path, plot_flag)


def save_plot(data, y, ylabel, file_path, output_path, plot_flag):
    """
    Saves a plot for the given metric (gap, speed, or jerk) from the data.
    """
    plt.figure(figsize=(10, 5))
    for vid in data['vehicle_id'].unique():
        vehicle_data = data[data['vehicle_id'] == vid]
        plt.plot(vehicle_data['timestamp'], vehicle_data[y], label=vid)
    plt.xlabel('Time')
    plt.ylabel(ylabel)
    plt.title(f'Time vs {ylabel}')
    plt.grid(True)
    plt.legend(title="Vehicle ID", loc='center right')
    plot_filename = output_path.replace(".csv", f"_{ylabel}.pdf")
    plt.savefig(plot_filename)
    if(plot_flag):
        plt.show()  # Display the plot on the screen

    plt.close()
    print(f'Saved plot: {plot_filename}')
