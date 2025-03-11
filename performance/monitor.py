import sys
from collections import defaultdict
import csv
class PerformanceMonitor:

    def __init__(self, data_file):

        self.data_file = data_file
        self.bssid_data = defaultdict(list)
        self.channel_width = 20
        self.channel_switch_count = defaultdict(int)
        self.throughput = defaultdict(int)

# ======================================================================================================

    def load_data(self):

        try:
            
            with open(self.data_file, 'r') as f:

                for line in f:
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

    def reduce_data(self):

        reduced_data = {}

        for bssid, instances in self.bssid_data.items():
            
            #==================================================================================

            avg_signal_strength = sum(entry[3] for entry in instances) / len(instances)
            avg_data_rate = sum(entry[6] for entry in instances) / len(instances)

            #==================================================================================
            # Retry Rate:
            
            retry_count = 0
            non_retry_count = 0

            for entry in instances:
                retry = entry[4]
                if retry == 1:
                    retry_count += 1
                else:
                    non_retry_count += 1

            if non_retry_count > 0:
                retry_rate = retry_count / non_retry_count
            else:
                retry_rate = 0

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
            
            #==================================================================================
            latest_channel = instances[-1][1]

            reduced_data[bssid] = [
                instances[-1][0],
                latest_channel,
                instances[-1][2],
                avg_signal_strength,
                self.channel_switch_count[bssid],
                retry_rate,
                avg_data_rate,
                instances[-1][7],
                instances[-1][8]
            ]

        self.bssid_data = reduced_data
        
        self.write_reduced_data_to_csv()

# ======================================================================================================

    def save_collected_data_to_csv(self):
        
        with open('collected_data.csv', 'w', newline='') as csvfile:
            
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

    def write_reduced_data_to_csv(self):
        with open('reduced_data.csv', 'w', newline='') as csvfile:
            
            fieldnames = ['BSSID', 'PHY Type', 'Channel', 'Frequency', 'Average Signal Strength', 'Channel Switch Count', 
                          'Retry Rate', 'Data Rate', 'Short GI', 'MCS index']
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
                    'Short GI': data[7],
                    'MCS index': data[8]
                    
                })

# ======================================================================================================

    def save_channel_density_to_csv(channel_density):
        with open("channel_density.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Channel", "Density"])
            for channel, density in sorted(channel_density.items()):
                writer.writerow([channel, density])

# ======================================================================================================

    def calculations(self):

        if not self.bssid_data:
            return 0

        ssid_strength_score = sum((100 + data[3]) for data in self.bssid_data.values())

        # =======================================================================================================

        channel_density = defaultdict(int)
        
        for data in self.bssid_data.values():
            channel = data[1]
            for ch in range(channel - 2, channel + 3):
                channel_density[ch] += 1
                
        PerformanceMonitor.save_channel_density_to_csv(channel_density)
                
        overlap_score = sum(count**2 - 1 for count in channel_density.values() if count > 1)
        channel_switch_impact = sum(self.channel_switch_count.values())

        # =======================================================================================================
        
        for bssid, instances in self.bssid_data.items():
            self.throughput[bssid] = instances[6]* (1 - instances[5])
        
        print(f"Throughtput: {self.throughput}")
        return (ssid_strength_score * 0.1) + (overlap_score * 0.5) + (channel_switch_impact * 1), ssid_strength_score, overlap_score, channel_switch_impact

# ======================================================================================================

    def print_density_report(self):
        
        network_density, ssid_strength_score, overlap_score, channel_switch_impact = self.calculations()
        print("\n========= Wi-Fi Density Report =========")
        print(f"Weighted SSID Score: {ssid_strength_score:.2f}")
        print(f"Channel Overlap Score: {overlap_score:.2f}")
        print(f"Channel Switch Impact: {channel_switch_impact:.2f}")
        print(f"Final Network Density: {network_density:.2f}")
        print("========================================")

# ======================================================================================================

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python performance_monitor.py <data_file>")
        sys.exit(1)

    monitor = PerformanceMonitor(sys.argv[1])

    monitor.load_data()
    print("========================================")
    monitor.reduce_data()
    print("========================================")
    monitor.print_density_report()
