import sys
from collections import defaultdict, Counter
import csv
import os
from data_in.constants import phy_map
import pandas as pd


class WiFiAnalyzer:

    def __init__(self, collected_data_file, reduced_data_file, network_density_file):
        
        self.collected_data_file = collected_data_file
        self.reduced_data_file = reduced_data_file
        self.network_density_file = network_density_file
        
        self.data_rate = None
        self.bandwidth = None
        self.channel_frequency = None
        self.shortGI = None
        self.mcs_index = None
        self.throughput = None
        self.avg_signal_strength = None
        self.avg_rate_gap = None
        self.avg_error_rate = None
        
        self.signal_strength_array = [-82,-79,-77,-74,-70,-66,-65,-64,-59,-57]
        
        self.message_hardware_good = "PHY protocol used is fine, meaning your AP / Wificard hardware are up to date"
        self.message_hardware_bad = "Either your AP or Wificard is outdated, causing you to be stack using slower modulation protocols."
        
        self.positive_comments = []
        self.negative_comments = []
        self.comments = []
        
        self.network_density = None
        self.network_density_status = None

        self.phy_type_connection = ""
        self.connection_status = None
        
        self.rssi_status = None
        self.throughput_status = None
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
        if throughput_mbps > 400:
            return "Excellent Connection"
        elif throughput_mbps > 130:
            return "Good Connection"
        elif throughput_mbps > 60:
            return "Moderate Connection"
        elif throughput_mbps > 20:
            return "Slow Connection"
        else:
            return "Very Poor Connection"

# ======================================================================================================

    def classify_network_density(self, network_density):
        
        if network_density > 80:
            return "Very Congested"
        elif network_density > 60:
            return "Congested"
        elif network_density > 30:
            return "Moderate Traffic"
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
        
# ======================================================================================================

    def analyze_signal_strength(self):

        with open(self.reduced_data_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
                    
            for row in reader:
                
                self.mcs_index = round(float(row["MCS index"].strip()))
                self.data_rate = float(row["Data Rate"].strip())
                shortGIPercentage = row["Short GI"].strip()
                if(float(shortGIPercentage) > 50):
                    shortGI = 400
                else:
                    shortGI = 800
                    
                self.shortGI = shortGI
                
                self.channel_frequency = int(float(row["Frequency"].strip()) / (10**3))               
                if(self.channel_frequency == 2):
                    self.channel_frequency = 2.4
                else:
                    self.channel_frequency = 5

                self.bandwidth = int(row["Bandwidth"].strip())
                self.phy_type_connection = row["PHY Type"].strip()
        
                self.avg_signal_strength = float(row["Average Signal Strength"].strip())
                self.throughput = float(row["Throughput"].strip())
                self.avg_rate_gap = float(row["Rate Gap"].strip())
                self.avg_error_rate = float(row["Retry Rate"].strip())
                
        self.connection_status = self.classify_phy_type(self.phy_type_connection)
        self.rssi_status = self.classify_rssi(float(self.avg_signal_strength))
        self.throughput_status = self.classify_throughput(float(self.throughput))

# ======================================================================================================

    def analyze_network_density(self):
        
        with open(self.network_density_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
                    
            for row in reader:
                self.network_density = float(row["Final Network Density"].strip())

        self.network_density_status = self.classify_network_density(self.network_density)

# ======================================================================================================

    def get_wifi_params(self, mcs_index, bandwidth, short_gi, data_rate, file_path="data_in/mcs_table.csv"):
        
        if(self.phy_type_connection == "802.11n (HT)"):
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
        modulation_method = matching_row.iloc[0]['modulation_method']
        coding_rate = matching_row.iloc[0]['coding_rate']
        return bandwidth_column_index,spatial_streams, modulation_method, coding_rate, classified_data_rate

# ======================================================================================================

    def final_analysis(self):
        
        print("\n============= Connection Charateristics: =============")

        (bandwidth_column_index, spatial_streams, modulation_method, coding_rate, classified_data_rate) = (
            self.get_wifi_params(self.mcs_index, self.bandwidth, self.shortGI, self.throughput)
        )

        ss_index = int((bandwidth_column_index - 4) / 2)
        increase_signal_strenth_factor = 3
        mcs_index = self.mcs_index
        mcs_index_threshold = 7
        if(self.phy_type_connection == "802.11n (HT)"):
            mcs_index = self.mcs_index % 8
            mcs_index_threshold = 5
        expected_signal_strength = self.signal_strength_array[mcs_index] + ss_index * increase_signal_strenth_factor
        # print(f"aveage_signal_strength:{self.avg_signal_strength}")
        # print(f"expected_signal_strength:{expected_signal_strength}")
        
        print(f"MCS Index: {self.mcs_index}, Modulation: {modulation_method}, Coding Rate: {coding_rate}")
        print(f"Spatial Streams: {spatial_streams}, Bandwidth: {self.bandwidth}, Short GI: {self.shortGI}")
        print(f"Data Rate: {self.data_rate}, Classified Data Rate: {classified_data_rate}")
            
        print("\n============= Metric Evalutation: =============")
        
        print(f"Network Density => status: {self.network_density_status}, metric: {self.network_density}")
        print(f"Signal Strength => status: {self.rssi_status}, metric: {self.avg_signal_strength}")
        print(f"PHY connection status: {self.connection_status}, PHY type: {self.phy_type_connection}")
        print(f"Signal Throughput => status: {self.throughput_status}, metric: {self.throughput}")

        print("\n============= Analysis: =============")

        if self.phy_type_connection in {"802.11n (HT)", "802.11ac (VHT)", "802.11ax (HE)"}:
            print(self.message_hardware_good)

            # =================================== Network Congestion Evaluation ==================================
            
            congested_network = 0
            if self.network_density <= 30:
                self.positive_comments.append(f"The Network Congestion / Interference evaluation: {self.network_density_status}")
            elif self.network_density >= 60:
                congested_network = 1
                self.negative_comments.append(f"The Network Congestion / Interference evaluation: {self.network_density_status}")
                
            str1 = ""
            if(congested_network):
                str1 = "due to congestion"
            else:
                str1 = "due to Rate Adaptation dynamics (fluctuations)"            
                                
            # =================================== Signal Strength Evaluation ======================================
        
            if(mcs_index > mcs_index_threshold):
                self.positive_comments.append(("Signal Strength is fine (its not limiting the performance)"))
            elif mcs_index <= mcs_index_threshold:
                if(self.avg_signal_strength > expected_signal_strength):    # you have higher signal strength, than what you are utilizing, like Rate Gap > 0
                                                                            # expected_mcs_index > actuall_mcs_index => Rate Gap > 0, undershooting
                    if(congested_network):
                        self.negative_comments.append(("Data Rate may be limited by network interference"))
                else:
                    self.negative_comments.append(("Weak Signal Strength might be reducing your Data Rate. This could be due to distance or obstacles between you and your router.")) 
            
            # =================================== Rate Gap Evaluation ======================================
            
            if(self.avg_rate_gap > 0.5): # expected_mcs_index > actuall_mcs_index
                    self.negative_comments.append((f"Undershooting the optimal rate, {str1}")) # Might be because of interference
            elif(self.avg_rate_gap < -0.5): # expected_mcs_index < actuall_mcs_index
                if(self.avg_error_rate >= 0.05):
                    self.negative_comments.append(("Overshooting the optimal rate. This harms the connection, creating significant error rate"))
                elif (self.avg_error_rate > 0.05):
                    self.comments.append(("Overshooting the optimal rate, but it doesnt harm the connection")) 

            # =================================== Channel Evaluation ==============================================
              
            if(self.channel_frequency == 2.4 and self.bandwidth == 20):
                self.negative_comments.append(("The data rate is limited by the operating frequency of 2.4 GHz (and the resulting 20 MHz bandwidth)."))
            else:
                if(self.bandwidth >= 80):
                    self.positive_comments.append(("High Bandwidth (in 5GHz) is utilized to achieve higher performance"))
                else:
                    possible_problems = "Despite 5GHz, a lower Bandwidth is used due to: "
                    hardware_support_issue = 1
                    if(congested_network):
                        hardware_support_issue = 0
                        possible_problems += "network congestion,"
                    if(self.avg_signal_strength < -75):
                        hardware_support_issue = 0
                        possible_problems += "weak Signal Strength,"
                    if(hardware_support_issue == 1):
                        possible_problems += "insufficient hardware support"
                        
                    possible_problems = possible_problems.rstrip(', ')
                    self.negative_comments.append(possible_problems)
                    
            # =================================== Spatial Stream Evaluation =======================================

            if spatial_streams > 1:
                self.positive_comments.append("The Hardware supports MIMO technology.")
            else:
                if(congested_network):
                    self.negative_comments.append("Your AP or device may not use MIMO functionality due to network congestion.")
                else:
                    self.negative_comments.append("Your AP or device does not support MIMO functionality.")
                    
            # ======================================================================================================
            # Print Analysis:
            
            if(len(self.positive_comments) != 0):
                print("Positives:")
                i = 1
                for comment in self.positive_comments:
                    print(f"\t{i}) {comment}")
                    i = i + 1
            if(len(self.negative_comments) != 0):
                print("Negatives:")
                i = 1
                for comment in self.negative_comments:
                    print(f"\t{i}) {comment}")
                    i = i + 1
            if(len(self.comments) != 0):
                print("Additional Comments:")
                i = 1
                for comment in self.comments:
                    print(f"\t{i}) {comment}")
                    i = i + 1
        else:
            print(f"PHY Type: {self.phy_type_connection}")
            print(self.message_hardware_bad)

            

# ======================================================================================================

if __name__ == "__main__":

    collected_data_file = sys.argv[1]
    reduced_data_file = sys.argv[2]
    network_density_file = sys.argv[3]

    analyzer = WiFiAnalyzer(collected_data_file, reduced_data_file, network_density_file)
    
    analyzer.analyze_phy_type()
    analyzer.analyze_signal_strength()
    analyzer.analyze_network_density()
    analyzer.final_analysis()
