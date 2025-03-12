import sys
from collections import defaultdict, Counter
import csv
import os
from data_in.constants import phy_map

class WiFiAnalyzer:

    def __init__(self, collected_data_file, reduced_data_file, network_density_file):
        self.collected_data_file = collected_data_file
        self.reduced_data_file = reduced_data_file
        self.network_density_file = network_density_file
        self.phy_type_connection = ""
        
        self.message_hardware_good = "PHY protocol used is fine, so your AP / wificard hardware is up to date"
        self.message_hardware_bad = "Either your AP or wificard is outdated, causing you to be stack using slower modulation procols"
        self.message_connection_good = "Your connection quality is fine"
        self.message_connection_bad = "Your connection quality is not good"
        self.message_connection_bad_physical = "Your signal strength is weak, the problem might be distance / physical obstruction from AP "
        self.message_connection_bad_network = "Your network is too congested"

# ======================================================================================================

    def classify_phy_type(self, phy_type_connection):
        phy_map_quality = {
            "802.11b (HR/DSSS)": "Very Bad", 
            "802.11a (OFDM)": "Bad", 
            "802.11g (ERP)": "Bad",   
            "802.11n (HT)": "Okay", 
            "802.11ac (VHT)": "Good",  
            "802.11ax (HEW)": "Great",  
        }
        return phy_map_quality.get(phy_type_connection, "Unknown")

# ======================================================================================================

    def classify_rssi(self, rssi):
        if rssi > -30:
            return "Very Good"
        elif rssi > -60:
            return "Good"
        elif rssi > -70:
            return "Okay"
        elif rssi > -80:
            return "Weak"
        elif rssi > -90:
            return "Very Weak"
        else:
            return "Unusable"

# ======================================================================================================

    def classify_throughput(self, throughput_mbps):
        if throughput_mbps > 130:
            return "Excellent Connection"
        elif throughput_mbps > 80:
            return "Good Connection"
        elif throughput_mbps > 40:
            return "Moderate Connection"
        elif throughput_mbps > 10:
            return "Slow Connection"
        else:
            return "Very Poor Connection"

# ======================================================================================================

    def classify_network_density(self, network_density):
        if network_density > 130:
            return "Very Congested"
        elif network_density > 80:
            return "Congested"
        elif network_density > 40:
            return "Acceptable"
        elif network_density > 10:
            return "Light Traffic"
        else:
            return "Ideal Networking Conditions"

# ======================================================================================================

    def analyze_phy_type(self):
        phy_types = []
        downgrade_count = 0
        
        with open(self.collected_data_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            prev_phy_rank = None
            
            for row in reader:
                phy_type = row["PHY Type"].strip()
                phy_types.append(phy_type)
                
                phy_rank = {v: k for k, v in phy_map.items()}.get(phy_type)
                
                if prev_phy_rank is not None and phy_rank is not None and phy_rank < prev_phy_rank:
                    downgrade_count += 1
                
                prev_phy_rank = phy_rank

        self.phy_type_connection = Counter(phy_types).most_common(1)[0][0] if phy_types else "Unknown"
        connection_status = self.classify_phy_type(self.phy_type_connection)

        print(f"PHY connection status: {connection_status}, PHY type: {self.phy_type_connection}")
        
        if connection_status in {"Bad", "Very Bad"}:
            print("Your Access Point or your WiFi Card hardware is outdated")
        
        print(f"Number of downgrades: {downgrade_count}")

# ======================================================================================================

    def analyze_signal_strength(self):

        with open(self.reduced_data_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
                    
            for row in reader:
                avg_signal_strength = row["Average Signal Strength"].strip()
                throughput = row["Throughput"].strip()
        
        rssi_status = self.classify_rssi(float(avg_signal_strength))
        throughput_status = self.classify_throughput(float(throughput))

        print(f"Signal Strength => status: {rssi_status}, metric: {avg_signal_strength}")
        print(f"Signal Throughput => status: {throughput_status}, metric: {throughput}")

# ======================================================================================================

    def analyze_network_density(self):
        
        with open(self.network_density_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
                    
            for row in reader:
                network_density = row["Final Network Density"].strip()

        network_density_status = self.classify_network_density(float(network_density))
        print(f"Network Density => status: {network_density_status}, metric: {network_density}")

# ======================================================================================================

    def final_analysis(self):

        print("\n============= Final Analysis: =============")

        if self.phy_type_connection in {"802.11n (HT)", "802.11ac (VHT)", "802.11ax (HE)"}:
            print(self.phy_type_connection)
            

# ======================================================================================================

if __name__ == "__main__":

    collected_data_file = sys.argv[1]
    reduced_data_file = sys.argv[2]
    network_density_file = sys.argv[3]

    analyzer = WiFiAnalyzer(collected_data_file, reduced_data_file, network_density_file)
    
    analyzer.analyze_phy_type()
    print("---------------")
    analyzer.analyze_signal_strength()
    print("---------------")
    analyzer.analyze_network_density()
    print("---------------")    
    analyzer.final_analysis()
