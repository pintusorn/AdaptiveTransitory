import argparse
import sys

def parse_arguments():
    """
    Parses command-line arguments for the SUMO Simulation.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Run SUMO Simulation with Configurable Parameters")

    # Scenario Type
    parser.add_argument("--scenario_type", type=str, choices=["one_platoon", "two_platoon"], required=True,
                        help="Simulation type: one platoon or two platoon merging")

    # Platoon Configuration
    parser.add_argument("--platoon1", type=str, choices=["cacc", "pid", "consensus", "dmpc", "hinf"], required=True,
                        help="Controller function for Platoon 1")
    parser.add_argument("--platoon2", type=str, choices=["cacc", "pid", "consensus", "dmpc", "hinf"], default=None,
                        help="Controller function for Platoon 2 (only for two platoon scenario)")

    # Topology and Scenario Settings

    parser.add_argument("--size", type=int, choices=[8, 16,32], default=8,
                        help="Simulation size (8 or 16 vehicles)")
    
    parser.add_argument("--topology", type=int, choices=[1, 2, 3, 4], default=2,
                        help="Communication topology inter platoon")

    # Motion Parameters
    parser.add_argument("--headway", type=float, choices=[0.6, 0.9, 1.2], default=0.9,
                        help="Headway time (0.6, 0.9, 1.2 seconds)")
    parser.add_argument("--speed", type=int, choices=[10, 20, 30], default=20,
                        help="Vehicle speed (10, 20, 30 m/s)")
    parser.add_argument("--disturbance", type=str, choices=["brake", "sinu","speed_up", "slow_down","none"], default="brake",
                        help="Disturbance type (brake or sinusoidal)")

    # Merging and Gap Settings
    parser.add_argument("--inter_gap", type=int, choices=[100, 200, 300, 50], default=200,
                        help="Inter-platoon gap (100, 200, 300 m)")
    parser.add_argument("--merge_distance", type=float, choices=[0.3, 0.5, 0.7], default=0.5,
                        help="Merge distance as a fraction of total simulation length (0.3, 0.5, 0.7)")

    # Output Options
    parser.add_argument("--save_log", action="store_true",
                        help="Enable saving logs")
    parser.add_argument("--gui", action="store_true",
                        help="Enable GUI")
    parser.add_argument("--plot", action="store_true",
                        help="Enable plotting of results after simulation (requires --save_log)")
    parser.add_argument("--merging_time", type=float, default=0.05,
                        help="Time to start merging")
    parser.add_argument("--disturbance_time", type=float, default=0.6,
                        help="Time to start disturbance")
    parser.add_argument("--total_time", type=float, default=1.0,
                        help="Total time")

    parser.add_argument("--method", type=str, choices=["baseline", "transitory"], default=None,
                        help="transitory used or not")

    # Parse arguments
    args = parser.parse_args()

    # After parsing the arguments, validate the combination
    if args.plot and not args.save_log:
        parser.error("The --plot option requires --save_log to be specified.")

    # Validation - Ensure platoon2 is specified only for two platoon scenarios
    if args.scenario_type == "one_platoon" and args.platoon2:
        print("Error: 'platoon2' controller should not be specified for 'one_platoon' scenario.")
        sys.exit(1)

    if args.scenario_type == "two_platoon" and not args.platoon2:
        print("Error: 'platoon2' controller is required for 'two_platoon' scenario.")
        sys.exit(1)

    return args
