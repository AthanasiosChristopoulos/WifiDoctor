import sys
from collections import defaultdict
import csv

class PerformanceMonitor:

    def __init__(self, data_file):
        self.data_file = data_file
        self.bssid_data = defaultdict(list)
        self.channel_width = 20
        self.channel_switch_count = defaultdict(int)

# ======================================================================================================

    def load_data(self):
        try:
            with open(self.data_file, 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) < 5:
                        continue  

                    bssid = parts[0]
                    phy_type = parts[1]
                    channel = int(parts[2])
                    frequency = int(parts[3])
                    signal_strength = int(parts[4])

                    if self.bssid_data[bssid]:
                        last_channel = self.bssid_data[bssid][-1][1]  
                        if last_channel != channel:
                            self.channel_switch_count[bssid] += 1  

                    self.bssid_data[bssid].append([phy_type, channel, frequency, signal_strength])

                print(self.bssid_data)

        except FileNotFoundError:
            print(f"Error: File {self.data_file} not found!")
            sys.exit(1)

# ======================================================================================================

    def reduce_data(self):

        reduced_data = {}

        for bssid, instances in self.bssid_data.items():

            avg_signal_strength = sum(entry[3] for entry in instances) / len(instances)

            latest_channel = instances[-1][1]  

            reduced_data[bssid] = [
                instances[0][0],  
                latest_channel,  
                instances[0][2],  
                avg_signal_strength,
                self.channel_switch_count[bssid]  
            ]

        self.bssid_data = reduced_data
        print(self.bssid_data)

        # Write reduced data to CSV file
        self.write_reduced_data_to_csv()

# ======================================================================================================

    def write_reduced_data_to_csv(self):
        with open('reduced_data.csv', 'w', newline='') as csvfile:
            fieldnames = ['BSSID', 'PHY Type', 'Channel', 'Frequency', 'Average Signal Strength', 'Channel Switch Count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for bssid, data in self.bssid_data.items():
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
        
        with open("channel_density.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Channel", "Density"])
            for channel, density in sorted(channel_density.items()):
                writer.writerow([channel, density])

# ======================================================================================================

    def estimate_density(self):

        if not self.bssid_data:
            return 0
        
        ssid_strength_score = sum((100 + data[3]) for data in self.bssid_data.values())

        # ===================================================================================

        channel_density = defaultdict(int)
        for data in self.bssid_data.values():
            channel = data[1]
            for ch in range(channel - 2, channel + 3):  
                channel_density[ch] += 1


        overlap_score = sum(count**2 - 1 for count in channel_density.values() if count > 1)

        # ===================================================================================

        channel_switch_impact = sum(self.channel_switch_count.values()) 

        PerformanceMonitor.save_channel_density_to_csv(channel_density)

        return (ssid_strength_score * 0.1) + (overlap_score * 0.5) + (channel_switch_impact * 1), ssid_strength_score, overlap_score, channel_switch_impact

# ======================================================================================================

    def print_density_report(self):
        network_density, ssid_strength_score, overlap_score, channel_switch_impact = self.estimate_density()
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

