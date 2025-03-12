import pyshark
import sys
from collections import defaultdict
import os
from data_in.constants import phy_map

max_packets = 100
my_packet = 0

def get_phy_type(phy_value):

    return phy_map.get(phy_value, "Unknown PHY Type")

# =========================================================================================================================
# =========================================================================================================================
# Beacon Packets

def parse_pcap_beacon(file_path, beacon_file):
    print(file_path)
    filter_string = (
        "wlan.fc.type_subtype == 0x0008"
    )

    cap = pyshark.FileCapture(file_path, display_filter=filter_string)

    beacon_data = defaultdict(list)
    packet_count = 0

    for pkt in cap:

        try:
            wlan_layer = pkt.wlan
            wlan_radio = pkt.wlan_radio

            bssid = getattr(wlan_layer, 'bssid', 'N/A')
            phy_type = get_phy_type(int(getattr(wlan_radio, 'phy', '0')))
            channel = getattr(wlan_radio, 'channel', 'N/A')
            if channel == 'N/A':
                channel = 1  # Default to channel 1 if not available
                frequency = 2412  # Corresponding frequency for channel 1
            else:
                frequency = getattr(wlan_radio, 'frequency', 'N/A')
                
            
            channel = getattr(wlan_radio, 'channel', '1')
            frequency = getattr(wlan_radio, 'frequency', '2412')
            
            if not hasattr(wlan_radio, 'channel') and beacon_data[bssid]:
                channel = beacon_data[bssid][-1][1] 
                frequency = beacon_data[bssid][-1][2]
                                        
            signal_strength = getattr(wlan_radio, 'signal_dbm', '-50')
            
            if not hasattr(wlan_radio, 'signal_dbm') and beacon_data[bssid]:
                signal_strength = beacon_data[bssid][-1][3] 
                
            beacon_data[bssid].append([phy_type, channel, frequency, signal_strength])

            packet_count += 1
            if packet_count >= max_packets:
                break  

        except AttributeError:
            continue
    
    cap.close()
    
    with open(beacon_file, 'w') as f:
        for bssid, data_list in beacon_data.items():
            for entry in data_list:
                f.write(f"{bssid},{','.join(map(str, entry))}\n")
                
    
# =========================================================================================================================
# =========================================================================================================================
# Data Packets
            
def parse_pcap_data(file_path, data_file):

    if(my_packet == 0):
        filter_string = (
            "wlan and not eapol and "
            "wlan.ta == 2C:F8:9B:DD:06:A0 and "
            "wlan.da == 00:20:A6:FC:B0:36 and "
            "wlan.fc.type_subtype == 0x20 or wlan.fc.type_subtype == 0x28"
        )
    else: 
        filter_string = (
            "wlan and not eapol and "
             "wlan.fc.type_subtype == 0x20 or wlan.fc.type_subtype == 0x28"
            # "wlan.fc.type == 0x2"
            # "wlan.fc.type_subtype == 0x28"
        )
        
    cap = pyshark.FileCapture(file_path, display_filter=filter_string)
    
    bssid_data = defaultdict(list)
    packet_count = 0

    for pkt in cap:
        try:
            wlan_layer = pkt.wlan
            wlan_radio = pkt.wlan_radio
                
            frame_type_subtype = getattr(wlan_layer, 'fc_type_subtype', 'N/A')
            bssid = getattr(wlan_layer, 'bssid', 'N/A')
            phy_type = get_phy_type(int(getattr(wlan_radio, 'phy', '0')))
            retry = getattr(wlan_layer, 'fc_retry', 'N/A')
            number = pkt.number
            data_rate = getattr(wlan_radio, 'data_rate', 'N/A')
            short_GI = getattr(wlan_radio, '11n_short_gi', 'N/A')
            time_arrived = pkt.sniff_time.timestamp()
            packet_size = pkt.length
            
            channel = getattr(wlan_radio, 'channel', '1')
            frequency = getattr(wlan_radio, 'frequency', '2412')
            if not hasattr(wlan_radio, 'channel') and bssid_data[bssid]:
                channel = bssid_data[bssid][-1][1] 
                frequency = bssid_data[bssid][-1][2]
            
            signal_strength = getattr(wlan_radio, 'signal_dbm', '-50')
            if not hasattr(wlan_radio, 'signal_dbm') and bssid_data[bssid]:
                signal_strength = bssid_data[bssid][-1][3] 
            
            mcs_index = getattr(wlan_radio, '11n_mcs_index', '7')
            if not hasattr(wlan_radio, '11n_mcs_index') and bssid_data[bssid]:
                mcs_index = bssid_data[bssid][-1][8] 
            
            short_GI = getattr(wlan_radio, '11n_short_gi', '0')
            if not hasattr(wlan_radio, '11n_short_gi') and bssid_data[bssid]:
                short_GI = bssid_data[bssid][-1][7] 
                
            bssid_data[bssid].append([
                phy_type, channel, frequency, signal_strength, retry, number, data_rate, short_GI, mcs_index, time_arrived, packet_size
            ]) # 0          1          2             3           4      5        6          7          8           9            10

            packet_count += 1
            if packet_count >= max_packets:
                break  

        except AttributeError:
            continue
    
    cap.close()
    
    with open(data_file, 'w') as f:
        f.write("bssid, phy_type, channel, frequency, signal_strength, retry, number, data_rate, short_GI, mcs_index, time_arrived, packet_size\n")
        for bssid, data_list in bssid_data.items():
            for entry in data_list:
                f.write(f"{bssid},{','.join(map(str, entry))}\n")
                
# ======================================================================================================

if __name__ == "__main__":
    print("Executing Parser")

    pcap_file_beacon = sys.argv[1]
    pcap_file = sys.argv[2]
    beacon_file = sys.argv[3]
    data_file = sys.argv[4]
    my_packet = int(sys.argv[5])
    
    print(pcap_file_beacon)
    print(pcap_file)


    parse_pcap_beacon(pcap_file_beacon, beacon_file)
    parse_pcap_data(pcap_file, data_file)

