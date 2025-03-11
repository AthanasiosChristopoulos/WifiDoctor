import pyshark
import sys

def get_phy_type(phy_value):

    phy_map = {
        0: "Reserved",
        1: "802.11a (OFDM)",
        2: "802.11b (CCK)",
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

def parse_pcap(file_path, output_file, max_packets=10):
    cap = pyshark.FileCapture(file_path, display_filter="wlan")

    packet_count = 0
    bssids = set()  

    with open(output_file, 'w') as f:

        for pkt in cap:
            
            try:

                wlan_layer = pkt.wlan
                wlan_radio = pkt.wlan_radio

                frame_type_subtype = getattr(wlan_layer, 'fc_type_subtype', 'N/A')

                if frame_type_subtype != "0x0008": 
                    continue  

                bssid = getattr(wlan_layer, 'bssid', 'N/A')
                transmitter_mac = getattr(wlan_layer, 'ta', 'N/A')
                phy_type = get_phy_type(int(getattr(wlan_radio, 'phy', '0')))
                channel = getattr(wlan_radio, 'channel', 'N/A')
                frequency = getattr(wlan_radio, 'frequency', 'N/A')
                signal_strength = getattr(wlan_radio, 'signal_dbm', 'N/A')

                # f.write(f"{bssid},{transmitter_mac},{phy_type},{channel},{frequency},{signal_strength}\n")
                f.write(f"{bssid},{phy_type},{channel},{frequency},{signal_strength}\n")

                packet_count += 1
                if packet_count >= max_packets:
                    break  

            except AttributeError:
                continue

    cap.close()

# ======================================================================================================

if __name__ == "__main__":

    print("Executing Parser")

    if len(sys.argv) < 3:
        print("Usage: python pcap_parser.py <pcap_file> <output_file>")
        sys.exit(1)

    pcap_file = sys.argv[1]
    output_file = sys.argv[2]
    parse_pcap(pcap_file, output_file)
