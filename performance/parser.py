import pyshark
import sys
from collections import defaultdict

max_packets = 200

def get_phy_type(phy_value):
    phy_map = {
        0: "Reserved",
        1: "802.11a (OFDM)",
        2: "802.11b (CCK",
        3: "802.11g (ERP)",
        4: "802.11n (HT)",
        5: "802.11ac (VHT)",
        6: "802.11g (ERP)",  
        7: "802.11n (HT)",
        8: "802.11ac (VHT)",
        9: "802.11ax (HE)",
        10: "Proprietary Mode",
    }
    return phy_map.get(phy_value, "Unknown PHY Type")

# ======================================================================================================

def parse_pcap(file_path, output_file):

    # wireshark filter wlan.fc.type_subtype == 40 and _ws.col.protocol == "802.11" and wlan.ta == 2C:F8:9B:DD:06:A0 and wlan.da == 00:20:A6:FC:B0:36
        
    filter_string = (
        "wlan and not eapol and "
        "wlan.ta == 2C:F8:9B:DD:06:A0 and "
        "wlan.da == 00:20:A6:FC:B0:36 and "
        "wlan.fc.type_subtype == 0x28"
    )

    cap = pyshark.FileCapture(file_path, display_filter=filter_string)

    bssid_data = defaultdict(list)
    packet_count = 0
    last_time = 0

    for pkt in cap:
        
        try:
            
            wlan_layer = pkt.wlan
            wlan_radio = pkt.wlan_radio
            
            frame_type_subtype = getattr(wlan_layer, 'fc_type_subtype', 'N/A')
            
            if frame_type_subtype != "0x0028":  
                continue  
            
            # print(pkt.sniff_time.timestamp())
            # print(pkt.number)
            # print(pkt.length)
            # last_time = pkt.sniff_time.timestamp()
            # print(pkt.sniff_time.timestamp() - last_time)
            # print(pkt.frame_info.field_names)
            
            
            #===================================================================================

            bssid = getattr(wlan_layer, 'bssid', 'N/A')
            phy_type = get_phy_type(int(getattr(wlan_radio, 'phy', '0')))
            channel = getattr(wlan_radio, 'channel', 'N/A')
            frequency = getattr(wlan_radio, 'frequency', 'N/A')
            
            if hasattr(wlan_radio, 'signal_dbm'):
                signal_strength = getattr(wlan_radio, 'signal_dbm')
            else:
                signal_strength = bssid_data[bssid][-1][3] if bssid_data[bssid] else "-50"
                
            retry = getattr(wlan_layer, 'fc_retry', 'N/A')
            number = pkt.number
            data_rate = getattr(wlan_radio, 'data_rate', 'N/A')
            short_GI = getattr(wlan_radio, '11n_short_gi', 'N/A')
            mcs_index = getattr(wlan_radio, '11n_mcs_index', 'N/A')
            time_arrived = pkt.sniff_time.timestamp()            
            packet_size = pkt.length
            
            #===================================================================================
            
            bssid_data[bssid].append([phy_type, channel, frequency, signal_strength, retry, number, 
                                      data_rate, short_GI, mcs_index, time_arrived, packet_size])
            
            packet_count += 1
            if packet_count >= max_packets:
                break  
        except AttributeError:
            continue
    
    cap.close()
    

    with open(output_file, 'w') as f:
        
        for bssid, data_list in bssid_data.items():
            for entry in data_list:
                line = f"{bssid},{','.join(map(str, entry))}\n"
                f.write(line)  # Write to file

# ======================================================================================================

if __name__ == "__main__":
    print("Executing Parser")

    if len(sys.argv) < 3:
        print("Usage: python pcap_parser.py <pcap_file> <output_file>")
        sys.exit(1)

    pcap_file = sys.argv[1]
    output_file = sys.argv[2]
    parse_pcap(pcap_file, output_file)
