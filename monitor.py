import sys
from collections import defaultdict
import csv
import os
from collections import Counter
import pandas as pd

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
        
        # ==============================================
        
        self.unique_bssid_weight = 0.3
        self.overlap_weight = 0.8
        self.channel_switch_weight = 2
        self.phy_type_penalty_weight = 1
        self.unique_ssid_score_weight = 5
        self.max_density_score = 200
        self.min_density_score = 0
        
        self.phy_type_penalty = {
            "802.11b (HR/DSSS)": 3,     # High congestion due to long air-time usage
            "802.11g (ERP)": 1.5,       # Medium congestion (depends on protection mechanisms)
            "802.11a (OFDM)": 0.7,      # Less congestion (shorter air-time, less interference)
        }

        self.signal_strength_array = [-82,-79,-77,-74,-70,-66,-65,-64,-59,-57]
        self.n_mcs_index_1 = [0,1,2,3,4,5,6,7]
        self.n_mcs_index_2 = [8,9,10,11,12,13,14,15]
        self.n_mcs_index_3 = [16,17,18,19,20,21,22,23]

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
                    ssid = parts[5]
                    
                    if self.beacon_data[bssid]:
                        last_channel = self.beacon_data[bssid][-1][1]  
                        if last_channel != channel:
                            self.channel_switch_count[bssid] += 1  

                    self.beacon_data[bssid].append([phy_type, channel, frequency, signal_strength, ssid]) # 3 => RSSI, 4 => SSID

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
                self.channel_switch_count[bssid],  
                instances[0][4]  
            ]

        self.beacon_data = reduced_data  # beacon data will be by default reduced

        self.write_reduced_data_to_csv_beacon()

# ======================================================================================================

    def write_reduced_data_to_csv_beacon(self):
        
        with open('data_out/reduced_data_beacon.csv', 'w', newline='') as csvfile:
            fieldnames = ['BSSID', 'PHY Type', 'Channel', 'Frequency', 'Average Signal Strength', 'Channel Switch Count', 'SSID']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for bssid, data in self.beacon_data.items():
                avg_signal_strength = round(data[3], 2)

                writer.writerow({
                    'BSSID': bssid,
                    'PHY Type': data[0],
                    'Channel': data[1],
                    'Frequency': data[2],
                    'Average Signal Strength': avg_signal_strength,
                    'Channel Switch Count': data[4],
                    'SSID': data[5]
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
        
        SSID_BSSID_list = []  

        for bssid, data in self.beacon_data.items():  
            SSID_BSSID_list.append((bssid, data[5]))  
            
        unique_ssid_score = len(set(SSID_BSSID_list)) 
        
        # ===================================================================================
        # Unique BSSIDs:
        
        unique_APs_2_4 = set()
        unique_APs_5 = set()

        bssid_strength_score = 0

        for bssid, data in self.beacon_data.items():
            ap_identifier = bssid[:15]
            channel = data[1]
            
            if (channel <= 14):
                if ap_identifier not in unique_APs_2_4:
                    unique_APs_2_4.add(ap_identifier)
                    bssid_strength_score += (100 + data[3])            
            else:
                if ap_identifier not in unique_APs_5:
                    unique_APs_5.add(ap_identifier)
                    bssid_strength_score += (100 + data[3])
                    
        # ===================================================================================
        # Overlapping channels:

        channel_density = defaultdict(int)
        same_AP_2_4 = []
        same_AP_5 = []
        for bssid, data in self.beacon_data.items():
            
            channel = data[1]
            
            if (channel <= 14):
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
        
        channel_switches_score = sum(self.channel_switch_count.values()) 

        # ===================================================================================
        # PHY penalty:
        
        # phy_penalty_score = 0
        # same_AP_2_4 = []
        # same_AP_5 = []
        # for bssid, data in self.beacon_data.items():
        #     channel = data[1]
        #     if (channel <= 14):                          # if 2.4 GHz
        #         if(not (bssid[:15] in same_AP_2_4)):
        #             phy_penalty_score += self.phy_type_penalty.get(data[0], 1.0) 
        #             same_AP_2_4.append(bssid[:15])
        #     else:                                       # if 5 GHz
        #         if(not (bssid[:15] in same_AP_5)):
        #             phy_penalty_score += self.phy_type_penalty.get(data[0], 1.0) 
        #             same_AP_5.append(bssid[:15])
        phy_penalty_score = 0
     
        for bssid, data in self.beacon_data.items():
            phy_penalty_score += self.phy_type_penalty.get(data[0], 1.0) 
    
        # ===================================================================================

        PerformanceMonitor.save_channel_density_to_csv(channel_density)

        raw_score = (
            (bssid_strength_score * self.unique_bssid_weight) + (overlap_score * self.overlap_weight) +
            (channel_switches_score * self.channel_switch_weight) + (phy_penalty_score * self.phy_type_penalty_weight) +
            (unique_ssid_score * self.unique_ssid_score_weight)
        )

        normalized_score = max(0, min(100, ((raw_score - self.min_density_score) / (self.max_density_score - self.min_density_score)) * 100))
        
        # =========================================================================================================================================================================
                
        # print("Raw Score:")
        # print(f"bssid_strength_score: {bssid_strength_score}, overlap_score: {overlap_score}," 
        #       f" channel switches: {channel_switches_score}, phy_penalty_score: {phy_penalty_score}, unique_ssid_score: {unique_ssid_score}")
        print("Component Weighted Network Density Scores:")
        print(f"bssid_strength_score: {bssid_strength_score * self.unique_bssid_weight:.2f}, "
            f"overlap_score: {overlap_score * self.overlap_weight:.2f}, "
            f"channel switches: {channel_switches_score * self.channel_switch_weight:.2f}, "
            f"phy_penalty_score: {phy_penalty_score * self.phy_type_penalty_weight:.2f}, "
            f"unique_ssid_score: {unique_ssid_score * self.unique_ssid_score_weight:.2f}")
        print("")
        print("Final Network Density Score:")
        print(f"raw_score: {raw_score:.2f}, normalized_score: {normalized_score:.2f}")

        
        return normalized_score, bssid_strength_score, overlap_score, channel_switches_score, phy_penalty_score, unique_ssid_score
    
# ======================================================================================================

    def print_density_report_beacon(self):

        network_density, bssid_strength_score, overlap_score, channel_switches_score, phy_penalty_score, unique_ssid_score = self.estimate_density()
        
        csv_filename = "data_out/network_density.csv"

        with open(csv_filename, mode="w", newline="") as file:
            writer = csv.writer(file) 
            
            writer.writerow(["Weighted SSID Score", "Channel Overlap Score", 
                            "Channel Switch Impact", "PHY penalty score", "Unique SSIDs score", "Final Network Density"])
            writer.writerow([f"{(bssid_strength_score * self.unique_bssid_weight):.2f}", f"{(overlap_score * self.overlap_weight):.2f}", 
                            f"{(channel_switches_score * self.channel_switch_weight):.2f}", f"{(phy_penalty_score * self.phy_type_penalty_weight):.2f}",
                            f"{unique_ssid_score * self.unique_ssid_score_weight}", f"{network_density:.2f}"])
        
# ======================================================================================================
# ======================================================================================================

    def calculate_expected_data_rate(self,phy_type_connection, mcs_index, bandwidth, short_gi, actual_rssi, data_rate, file_path="data_in/mcs_table.csv"):

        if(phy_type_connection == "802.11n (HT)"):
            mcs_index = mcs_index % 8
            
        column_names = [
            'mcs_index', 'spatial_streams', 'modulation_method', 'coding_rate', 
            '20_800ns', '20_400ns', '40_800ns', '40_400ns', '80_800ns', '80_400ns', '160_800ns', '160_400ns'
        ]
        
        df = pd.read_csv(file_path)
        bandwidth_map = {20: 4, 40: 6, 80: 8, 160: 10}
        if bandwidth not in bandwidth_map:
            raise ValueError("Invalid Bandwidth")

        bandwidth_column_index = bandwidth_map[bandwidth] if short_gi == 800 else bandwidth_map[bandwidth] + 1
    
        # expected_signal_strength = self.signal_strength_array[mcs_index] + ss_index * increase_signal_strenth_factor
        
        bandwidth_column = column_names[bandwidth_column_index]
        matching_rows = df[df['mcs_index'] == mcs_index]

        if matching_rows.empty:
            raise ValueError(f"No matching entry for MCS index {mcs_index}")

        tolerance = 0.1
        matching_row = matching_rows[abs(matching_rows[bandwidth_column] - data_rate) < tolerance]
        
        while matching_row.empty and tolerance < 200:  
            tolerance += 2
            matching_row = matching_rows[abs(matching_rows[bandwidth_column] - data_rate) < tolerance]
        classified_data_rate = matching_row.iloc[0][bandwidth_column]
        if matching_row.empty:
            raise ValueError(f"No matching data rate found for MCS index {mcs_index}, Bandwidth {bandwidth}, GI {short_gi}, data rate {data_rate}")

        spatial_streams = matching_row.iloc[0]['spatial_streams']
        
        ss_index = int((bandwidth_column_index - 4) / 2)
        increase_signal_strenth_factor = 3
        # expected_signal_strength_array = self.signal_strength_array[mcs_index] + ss_index * increase_signal_strenth_factor
        expected_signal_strength_array = [
            strength + ss_index * increase_signal_strenth_factor for strength in self.signal_strength_array
        ]            
        min_error = -1
        min_index = 0
        index = 0
        for expected_rssi in expected_signal_strength_array:
            error = np.abs(expected_rssi - actual_rssi)
            if error <= min_error or min_error == -1:
                min_error = error
                min_index = index
            index = index + 1 
                
        expected_mcs_index = min_index
           
        if(phy_type_connection == "802.11n (HT)"):
            if(expected_mcs_index in [8,9]):
                expected_mcs_index = 7
                
            if(spatial_streams == 1):
               expected_mcs_index = self.n_mcs_index_1[expected_mcs_index]
            elif(spatial_streams == 2):
               expected_mcs_index = self.n_mcs_index_2[expected_mcs_index]   
            if(spatial_streams == 3):
                expected_mcs_index = self.n_mcs_index_3[expected_mcs_index]
        # print(f"spatial_streams: {spatial_streams}, mcs_index: {mcs_index}, bandwidth: {bandwidth}, short_gi: {short_gi},actual_rssi: {actual_rssi}, expected_mcs_index: {expected_mcs_index}")
        return expected_mcs_index
    
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
                    bandwidth =  int(parts[12])

                                
                    if self.bssid_data[bssid]:
                        last_channel = self.bssid_data[bssid][-1][1]
                        if last_channel != channel:
                            self.channel_switch_count[bssid] += 1
                            
                    # Calculate expected data rate
                    except_mcs_index = self.calculate_expected_data_rate(phy_type, mcs_index, bandwidth, short_GI, signal_strength, data_rate)

                    rate_gap = except_mcs_index - mcs_index
                    
                    self.bssid_data[bssid].append([phy_type, channel, frequency, signal_strength, retry, number, # 0,1,2,3,4,5
                                                   data_rate, short_GI, mcs_index, time_arrived, packet_size, bandwidth, rate_gap])   # 6,7,8,9,10,11,12 
                
                self.save_collected_data_to_csv()

                # print(self.bssid_data)

        except FileNotFoundError:
            print(f"Error: File {self.data_file} not found!")
            sys.exit(1)
            
# ======================================================================================================

    def save_collected_data_to_csv(self):
        
        with open('data_out/collected_data.csv', 'w', newline='') as csvfile:
            
            fieldnames = ['BSSID', 'PHY Type', 'Channel', 'Frequency', 'Signal Strength', 'Retry', 'Number', 'Data Rate',
                          'Short GI', 'MCS index', 'Time Arrived', 'Packet Arrived', 'Bandwidth', 'Rate Gap']
            
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
                        'Bandwidth': instance[11],
                        'Rate Gap': instance[12]

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
            avg_rate_gap = sum(entry[12] for entry in instances) / len(instances)

            phy_type_list = []
            bandwidth_list = []
            for entry in instances:
                phy_type_list.append(entry[0])
                bandwidth_list.append(entry[11])
            counter = Counter(phy_type_list)
            phy_type = counter.most_common(1)[0][0] 
            counter = Counter(bandwidth_list)
            bandwidth = counter.most_common(1)[0][0] 

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
            # Rate Gap:
            
            
            latest_channel = instances[-1][1]

            reduced_data[bssid] = [
                phy_type,
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
                f"{throughput_max:.2f}",
                f"{bandwidth}",
                f"{avg_rate_gap}"
            ]

        self.bssid_data = reduced_data
        
        self.write_reduced_data_to_csv()

    def write_reduced_data_to_csv(self):
        with open('data_out/reduced_data.csv', 'w', newline='') as csvfile:
            
            fieldnames = ['BSSID', 'PHY Type', 'Channel', 'Frequency', 'Average Signal Strength', 'Channel Switch Count', 
                          'Retry Rate', 'Data Rate', 'Throughput','Short GI', 'MCS index', 'MIN_Tht', 'Median_Tht', 
                          '75P_Tht', '95P_Tht', 'MAX_Tht','Bandwidth', 'Rate Gap']
            
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
                    'MAX_Tht': data[14],
                    'Bandwidth': data[15],
                    'Rate Gap': data[16]
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




