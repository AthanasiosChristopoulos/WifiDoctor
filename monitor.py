import sys
from collections import defaultdict
import csv
import os

import numpy as np

class PerformanceMonitor:

    def __init__(self, beacon_file, data_file):
        
        self.data_out_dir = "data_out"
        os.makedirs(self.data_out_dir, exist_ok=True)
        
        self.beacon_file = beacon_file
        self.data_file = data_file
        self.beacon_data = defaultdict(list)
        self.bssid_data = defaultdict(list)
        self.channel_switch_count = defaultdict(int)


# ======================================================================================================
# ======================================================================================================
# ======================================================================================================
# ======================================================================================================
# beacon packets (1.1):

    def load_data_beacon(self):
        try:
            with open(self.beacon_file, 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) < 5:
                        continue  

                    bssid = parts[0]
                    phy_type = parts[1]
                    channel = int(parts[2])
                    frequency = int(parts[3])
                    signal_strength = int(parts[4])

                    if self.beacon_data[bssid]:
                        last_channel = self.beacon_data[bssid][-1][1]  
                        if last_channel != channel:
                            self.channel_switch_count[bssid] += 1  

                    self.beacon_data[bssid].append([phy_type, channel, frequency, signal_strength])


        except FileNotFoundError:
            print(f"Error: File {self.data_file} not found!")
            sys.exit(1)

# ======================================================================================================

    def reduce_data_beacon(self):

        reduced_data = {}

        for bssid, instances in self.beacon_data.items():

            avg_signal_strength = sum(entry[3] for entry in instances) / len(instances)

            latest_channel = instances[-1][1]  

            reduced_data[bssid] = [
                instances[0][0],  
                latest_channel,  
                instances[0][2],  
                avg_signal_strength,
                self.channel_switch_count[bssid]  
            ]

        self.beacon_data = reduced_data  # beacon data will be by default reduced

        self.write_reduced_data_to_csv_beacon()

# ======================================================================================================

    def write_reduced_data_to_csv_beacon(self):
        
        with open('data_out/reduced_data_beacon.csv', 'w', newline='') as csvfile:
            fieldnames = ['BSSID', 'PHY Type', 'Channel', 'Frequency', 'Average Signal Strength', 'Channel Switch Count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for bssid, data in self.beacon_data.items():
                writer.writerow({
                    'BSSID': bssid,
                    'PHY Type': data[0],
                    'Channel': data[1],
                    'Frequency': data[2],
                    'Average Signal Strength': data[3],
                    'Channel Switch Count': data[4]
                })

# ======================================================================================================

    def save_channel_density_to_csv(channel_density):
        
        with open("data_out/channel_density.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Channel", "Density"])
            for channel, density in sorted(channel_density.items()):
                writer.writerow([channel, density])

# ======================================================================================================

    def estimate_density(self):

        if not self.beacon_data:
            return 0
        
        # ===================================================================================
        # Unique SSIDs:
        
        ssid_strength_score = sum((100 + data[3]) for data in self.beacon_data.values())

        # ===================================================================================
        # Overlapping channels:

        channel_density = defaultdict(int)
        same_AP_2_4 = []
        same_AP_5 = []
        for bssid, data in self.beacon_data.items():
            
            channel = data[1]
            
            if (channel <= 36):
                if (not (bssid[:15] in same_AP_2_4)):
                    for ch in range(channel - 2, channel + 3):  
                        channel_density[ch] += 1
                    same_AP_2_4.append(bssid[:15])
            else:        
                if (not (bssid[:15] in same_AP_5)):
                    for ch in range(channel - 4, channel + 5):  
                        channel_density[ch] += 1            
                    same_AP_5.append(bssid[:15])
                    
                                   
        overlap_score = sum(count**2 - 1 for count in channel_density.values() if count > 1)

        # ===================================================================================
        # Amount of Channel Switches:
        
        channel_switch_impact = sum(self.channel_switch_count.values()) 

        PerformanceMonitor.save_channel_density_to_csv(channel_density)

        return (ssid_strength_score * 0.1) + (overlap_score * 0.5) + (channel_switch_impact * 1), ssid_strength_score, overlap_score, channel_switch_impact

# ======================================================================================================
    def print_density_report_beacon(self):

        network_density, ssid_strength_score, overlap_score, channel_switch_impact = self.estimate_density()
        
        csv_filename = "data_out/network_density.csv"
        # Open file in write mode
        with open(csv_filename, mode="w", newline="") as file:
            writer = csv.writer(file)  # Create CSV writer
            
            # Ensure writing happens within the context manager
            writer.writerow(["Weighted SSID Score", "Channel Overlap Score", 
                            "Channel Switch Impact", "Final Network Density"])
            writer.writerow([f"{ssid_strength_score:.2f}", f"{overlap_score:.2f}", 
                            f"{channel_switch_impact:.2f}", f"{network_density:.2f}"])
        

# ======================================================================================================
# ======================================================================================================
# ======================================================================================================
# ======================================================================================================
# data packets (1.2):

    def load_data(self):

        try:
            with open(self.data_file, 'r') as f:
                first_line = 1

                for line in f:
                    
                    if (first_line == 1):
                        first_line = 0
                        continue

                    parts = line.strip().split(',')
                    if len(parts) < 7:  
                        continue

                    bssid = parts[0]
                    phy_type = parts[1]
                    channel = int(parts[2])
                    frequency = int(parts[3])
                    signal_strength = int(parts[4])
                    
                    if str(parts[5]).lower() in ['true', '1']:
                        retry = 1
                    else:
                        retry = 0

                    number = int(parts[6])  
                    data_rate = float(parts[7])
                    
                    # short GI:
                    if str(parts[8]).lower() in ['true', '1']:
                        short_GI = 1
                    else:
                        short_GI = 0    
                        
                    mcs_index = int(parts[9])   
                    
                    time_arrived = float(parts[10])
                    packet_size =  int(parts[11])
                                
                    if self.bssid_data[bssid]:
                        last_channel = self.bssid_data[bssid][-1][1]
                        if last_channel != channel:
                            self.channel_switch_count[bssid] += 1

                    self.bssid_data[bssid].append([phy_type, channel, frequency, signal_strength, retry, number, # 0,1,2,3,4,5
                                                   data_rate, short_GI, mcs_index, time_arrived, packet_size])   # 6,7,8,9,10 
                
                self.save_collected_data_to_csv()

                # print(self.bssid_data)

        except FileNotFoundError:
            print(f"Error: File {self.data_file} not found!")
            sys.exit(1)
            
# ======================================================================================================

    def save_collected_data_to_csv(self):
        
        with open('data_out/collected_data.csv', 'w', newline='') as csvfile:
            
            fieldnames = ['BSSID', 'PHY Type', 'Channel', 'Frequency', 'Signal Strength', 'Retry', 'Number', 'Data Rate',
                          'Short GI', 'MCS index', 'Time Arrived', 'Packet Arrived']
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            
            for bssid, instances in self.bssid_data.items():
                for instance in instances:
                    writer.writerow({
                        'BSSID': bssid,
                        'PHY Type': instance[0],
                        'Channel': instance[1],
                        'Frequency': instance[2],
                        'Signal Strength': instance[3],
                        'Retry': instance[4],
                        'Number': instance[5],
                        'Data Rate': instance[6],
                        'Short GI': instance[7],
                        'MCS index': instance[8],
                        'Time Arrived': instance[9],
                        'Packet Arrived': instance[10],
                    })

# ======================================================================================================

    def reduce_data(self):

        reduced_data = {}

        for bssid, instances in self.bssid_data.items():
            
            #==================================================================================

            avg_signal_strength = sum(entry[3] for entry in instances) / len(instances)
            avg_data_rate = sum(entry[6] for entry in instances) / len(instances)
            avg_short_GI_percentage = (sum(entry[7] for entry in instances) / len(instances)) * 100
            avg_mcs_index = sum(entry[8] for entry in instances) / len(instances)

            print(f"avg_data_rate: {avg_data_rate}")

            #==================================================================================
            # Retry Rate:
            
            retry_count = 0
            all_packets = 0

            for entry in instances:
                retry = entry[4]
                if retry == 1:
                    retry_count += 1
                
                all_packets += 1

            if all_packets > 0:
                retry_rate = retry_count / all_packets
            else:
                retry_rate = 0

            #==================================================================================
            # Throughput:
            
            retry_count = 0
            all_packets = 0
            
            throughputs = []
            
            for entry in instances:
                
                retry = entry[4]
                
                if retry == 1:
                    retry_count += 1
                all_packets += 1
                
                retry_rate = retry_count / all_packets
                throughput = avg_data_rate * (1 - retry_rate)
                throughputs.append(throughput)

            # statistics for throughput
            throughput_min = np.min(throughputs)
            throughput_mean = np.mean(throughputs)
            throughput_median = np.median(throughputs)
            throughput_75p = np.percentile(throughputs, 75)
            throughput_95p = np.percentile(throughputs, 95)
            throughput_max = np.max(throughputs)
                
            #==================================================================================
            
            latest_channel = instances[-1][1]

            reduced_data[bssid] = [
                instances[-1][0],
                latest_channel,
                instances[-1][2],
                f"{avg_signal_strength:.2f}",
                self.channel_switch_count[bssid],
                f"{retry_rate:.5f}",
                f"{avg_data_rate:.2f}",
                f"{throughput_mean:.2f}",
                f"{avg_short_GI_percentage:.2f}",
                f"{avg_mcs_index:.2f}",
                f"{throughput_min:.2f}",
                f"{throughput_median:.2f}",
                f"{throughput_75p:.2f}",
                f"{throughput_95p:.2f}",
                f"{throughput_max:.2f}"
            ]

        self.bssid_data = reduced_data
        
        self.write_reduced_data_to_csv()

# ======================================================================================================

    def write_reduced_data_to_csv(self):
        with open('data_out/reduced_data.csv', 'w', newline='') as csvfile:
            
            fieldnames = ['BSSID', 'PHY Type', 'Channel', 'Frequency', 'Average Signal Strength', 'Channel Switch Count', 
                          'Retry Rate', 'Data Rate', 'Throughput','Short GI', 'MCS index', 'MIN_Tht', 'Median_Tht', '75P_Tht', '95P_Tht', 'MAX_Tht']
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            
            for bssid, data in self.bssid_data.items():
                writer.writerow({
                    'BSSID': bssid,
                    'PHY Type': data[0],
                    'Channel': data[1],
                    'Frequency': data[2],
                    'Average Signal Strength': data[3],
                    'Channel Switch Count': data[4],
                    'Retry Rate': data[5],
                    'Data Rate': data[6],
                    'Throughput': data[7],
                    'Short GI': data[8],
                    'MCS index': data[9],
                    'MIN_Tht': data[10], 
                    'Median_Tht': data[11], 
                    '75P_Tht': data[12], 
                    '95P_Tht': data[13], 
                    'MAX_Tht': data[14]
                })


# ======================================================================================================

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python performance_monitor.py <beacon_file> <data_file>")
        sys.exit(1)

    monitor = PerformanceMonitor(sys.argv[1], sys.argv[2])
    my_packet = sys.argv[3]

    monitor.load_data_beacon()
    monitor.reduce_data_beacon()
    monitor.print_density_report_beacon()

    monitor.load_data()
    monitor.reduce_data()




#==================================================================================
# Actuall Data Rate:

# total_data_size = 0
# total_time = 0
# first_packet = 1

# for entry in instances:
    
#     packet_length_bits = entry[10]
#     total_data_size += packet_length_bits
#     # print(total_data_size)
#     if first_packet == 0:
#         time_delta = float(entry[9] - last_time)
#         # print(time_delta)
#         total_time += time_delta
#     else:
#         first_packet = 0

#     last_time = entry[9]
    
# if total_time > 0:
    
#     data_rate = total_data_size * 8 / total_time
#     # print(data_rate)
#     print(f"Estimated Data Rate: {data_rate / 1e6} Mbps")
    
# else:
#     print("Error: Total time cannot be zero.")