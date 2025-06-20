import os
from datetime import datetime

def generate_rou_file(num_veh, gap, inter_gap, speed, headway, disturbance, platoon1_controller, platoon2_controller):
    # Dynamic calculation of start position for p1veh4 (last vehicle of the first platoon)
    start_p2 = inter_gap + gap * (num_veh - 1)
    print("inter_gap should be 22: " , gap)
    print("inter_gap:", inter_gap)
    print("(num_veh - 1): ", (num_veh - 1))
    print("start_p2: " , start_p2)

    # Generate intra-platoon positions for Platoon 1
    positions_p1 = [start_p2 + gap * i for i in range(num_veh)]
    positions_p1 = list(reversed(positions_p1))

    # Generate intra-platoon positions for Platoon 2, starting from 0
    positions_p2 = [gap * i for i in range(num_veh)]
    positions_p2 = list(reversed(positions_p2))

    # File path for the .rou.xml
    output_rou_xml = f"network/two_platoon.rou.xml"
    os.makedirs(os.path.dirname(output_rou_xml), exist_ok=True)

    

    with open(output_rou_xml, 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(f'<!-- Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} -->\n')
        f.write('<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">\n\n')
        f.write('    <!-- Vehicle Types -->\n')
        f.write('    <vType id="CAV" accel="4.0" decel="50.0" maxSpeed="30" length="4" minGap="0.0" tau="0.01" color="1,1,0"/>\n')

        f.write('    <vType id="CAV2" accel="4.0" decel="50.0" maxSpeed="30" length="4" minGap="0.0" tau="0.01" color="0,1,1"/>\n')
        f.write('\n    <!-- Routes -->\n')
        f.write('    <route id="main" edges="highway"/>\n\n')

        for i in range(num_veh):
            veh_id = f'p1veh{i+1}'
            pos = positions_p1[i] 
            f.write(f'    <vehicle id="{veh_id}" type="CAV" depart="0.00" route="main" departSpeed="{speed}" departPos="{pos}"/>\n')


        for i in range(num_veh):
            veh_id = f'p2veh{i+1}'
            pos = positions_p2[i]
            f.write(f'    <vehicle id="{veh_id}" type="CAV2" depart="0.00" route="main" departSpeed="{speed}" departPos="{pos}"/>\n')

        f.write('</routes>\n')
    print(f"Generated {output_rou_xml} with {num_veh} vehicles at speed={speed}, headway={headway}, disturbance={disturbance}")
