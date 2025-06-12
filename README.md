# Adaptive Transitory Controller for Vehicle Platooning

## Abstract

This work aims to investigate and study how would different platoon controller needs to react without any intermeditary especially for merging scenario. Different controller platoon merging presents in mismatch controller type and may cause 


## Raw Result
### Inter-Platoon Gap Results (`min_gap_p2veh1`)

| Leader \ Follower | cacc    | consensus | dmpc    | hinf    | pid     |
|-------------------|---------|-----------|---------|---------|---------|
| **cacc**          | 19.4053 | 19.4490   | 19.2619 | 19.4464 | 19.4614 |
| **consensus**     | 19.3868 | 19.4425   | 19.2555 | 19.4395 | 19.4545 |
| **dmpc**          | 19.4149 | 19.4549   | 19.2899 | 19.4525 | 19.4657 |
| **hinf**          | 19.4176 | 19.4567   | 19.2797 | 19.4543 | 19.4663 |
| **pid**           | 19.4079 | 19.4516   | 19.2612 | 19.4491 | 19.4620 |

### Intra-Platoon Gap Results (`avg_gap_spacing_p2_others`)

| Leader \ Follower | cacc     | consensus | dmpc     | hinf     | pid      |
|-------------------|----------|-----------|----------|----------|----------|
| **cacc**          | 22.5042  | 23.2131   | 22.9780  | 23.1249  | 23.2348  |
| **consensus**     | 22.7203  | 23.2591   | 23.2465  | 23.1886  | 23.2696  |
| **dmpc**          | 22.5272  | 23.2049   | 23.1148  | 23.1126  | 23.2188  |
| **hinf**          | 22.5697  | 23.2138   | 23.1391  | 23.1321  | 23.2293  |
| **pid**           | 22.6633  | 23.2493   | 23.2114  | 23.1688  | 23.2600  |

### Merge Time Results (`leader_merged_time`)

| Leader \ Follower | cacc    | consensus | dmpc    | hinf    | pid     |
|-------------------|---------|-----------|---------|---------|---------|
| **cacc**          | 50.7000 | 51.0333   | 51.3667 | 50.9667 | 50.9667 |
| **consensus**     | 48.8333 | 48.8667   | 49.0000 | 48.8333 | 48.7667 |
| **dmpc**          | 49.3667 | 49.4000   | 49.4000 | 49.3667 | 49.2667 |
| **hinf**          | 49.2667 | 49.3333   | 49.3000 | 49.2667 | 49.1667 |
| **pid**           | 49.0000 | 49.0333   | 49.0000 | 49.0000 | 48.9000 |

### RMS Jerk Results (`jerk_rms`)

| Leader \ Follower | cacc     | consensus | dmpc     | hinf     | pid      |
|-------------------|----------|-----------|----------|----------|----------|
| **cacc**          | 0.4880   | 0.9819    | 2.0916   | 0.8760   | 1.5284   |
| **consensus**     | 1.5360   | 3.2208    | 2.8032   | 5.0980   | 5.2983   |
| **dmpc**          | 1.2934   | 2.4692    | 2.6555   | 3.9308   | 5.0369   |
| **hinf**          | 1.3350   | 2.6209    | 2.6800   | 4.1656   | 5.2325   |
| **pid**           | 1.4403   | 2.9522    | 2.7451   | 4.6663   | 5.3600   |




## Analysis

- The adaptive controller achieves **58.38% average improvement** in jerk RMS across all joining scenarios.
- Largest improvements:
  - PID (braking): 76%
  - DMPC (normal + oscillation): ~79%
- These improvements are obtained without affecting the gap-spacing, maintaining safety.

## Relative Improvement Summary

| Controller | Scenario   | Baseline Jerk RMS | Adaptive Jerk RMS | Relative Improvement (%) |
|------------|------------|-------------------|-------------------|---------------------------|
| CACC       | brake      | 2.6504            | 1.9984            | 24.60%                    |
| CACC       | none       | 0.4999            | 0.4999            | 0.00%                     |
| CACC       | sinu       | 0.5054            | 0.5054            | 0.00%                     |
| Consensus  | brake      | 5.7743            | 2.3007            | 60.16%                    |
| Consensus  | none       | 0.7725            | 0.5990            | 22.45%                    |
| Consensus  | sinu       | 0.8002            | 0.6058            | 24.29%                    |
| DMPC       | brake      | 2.2539            | 2.2539            | 0.00%                     |
| DMPC       | none       | 2.7614            | 0.5928            | 78.53%                    |
| DMPC       | sinu       | 2.7700            | 0.5993            | 78.37%                    |
| H-infinity | brake      | 9.7686            | 2.7506            | 71.84%                    |
| H-infinity | none       | 0.7216            | 0.6592            | 8.65%                     |
| H-infinity | sinu       | 0.7519            | 0.6668            | 11.32%                    |
| PID        | brake      | 11.1388           | 2.7164            | 75.61%                    |
| PID        | none       | 1.0925            | 0.6660            | 39.04%                    |
| PID        | sinu       | 1.2424            | 0.6902            | 44.45%                    |

*Note: Relative improvement is calculated as  
\[
\text{Improvement} = \frac{\text{Baseline} - \text{Adaptive}}{\text{Baseline}} \times 100\%
\]*

## Folder organization
All experimental results are stored in the `data/` directory. These include:
- Simulation logs
- Metrics like jerk RMS and inter-vehicle gap
- Baseline vs. adaptive results for all scenario combinations
- 

1. config : contain parser, telling which parameter is required when running a simulation to set
2. Controller: this folder contain 5 controller that is used in this work.
   -PID
   - CACC
   -Consensus
  - H-infinity (use predefined weight/gain)
   - DMPC
3. network: file for the simulation config for running via SUMO
3. output: the output of baseline result from running all experiment on how two platoon controller merge without any intermeditary
4. output_transitory: this output is when adaptive transitory controller is used the result format is the same as output
5. scripts: keep all the bash file of running experiment, and python for help analyze result into table organize and plot
6. Util: keep the code for logging data method, plot default data, and how to setup SUMO files for running simulation



### Prerequisites

Install dependencies using the provided environment:

```bash
conda create -n AdaptiveTransitory python=3.10
conda activate AdaptiveTransitory
pip install -r requirements.txt
```
## How to Run
Example command format

python main.py --speed=20 --headway=0.9 --platoon1=cacc --platoon2=pid --disturbance=brake --save_log --size=16 --scenario_type=two_platoon --inter_gap=200 --topology=1 --method=baseline --merging_time=2.0 --disturbance_time=1.0 --total_time=10.0


