import pyshark
import os
import platform

bandwidth_map = {
    "0": "20 MHz",
    "1": "40 MHz",
    "2": "80 MHz",
    "3": "160 MHz"
}

# Clear the terminal based on the operating system
def clear_terminal():
    if platform.system() == 'Windows':
        os.system('cls')  # Windows
    else:
        os.system('clear')  # macOS/Linux

clear_terminal()

def get_phy_type(phy_value):
    # Mapping the PHY numeric values to full string representations
    phy_map = {
        0: "Reserved",
        1: "802.11a (OFDM)",
        2: "802.11b (CCK)",
        3: "802.11g (ERP)",
        4: "802.11n (HT)",
        5: "802.11ac (VHT)",
        6: "802.11g (ERP)",  # This is the value you mentioned
        7: "802.11n (HT)",
        8: "802.11ac (VHT)",
        9: "802.11ax (HE)",
        10: "Proprietary Mode",
        # Add more mappings here as needed
    }
    return phy_map.get(phy_value, "Unknown PHY Type")

def parse_pcap(file_path, max_packets=1):
    cap = pyshark.FileCapture(file_path, display_filter="wlan")

    packet_count = 0
    first_packet_time = None  # To store the timestamp of the first packet

    counter = 10 

    for pkt in cap:
        try:
            # Extract WLAN and RadioTap layers
            wlan_layer = pkt.wlan
            wlan_radio = pkt.wlan_radio
            radio_layer = pkt.radiotap
            # mgt = pkt['wlan.mgt']

            # Extract frame type/subtype
            frame_type_subtype = getattr(wlan_layer, 'fc_type_subtype', 'N/A')

            if frame_type_subtype not in ["0x0028"]:
                continue

            if counter != 0:
                counter -= 1
                continue

            print(frame_type_subtype)

            if first_packet_time is None:
                first_packet_time = pkt.sniff_time

            relative_time = pkt.sniff_time - first_packet_time
            # print(pkt)
            print("====================================================================================")

            print("Time:", relative_time)
            print("BSSID:", getattr(wlan_layer, 'bssid', 'N/A'))
            print("Transmitter MAC:", getattr(wlan_layer, 'ta', 'N/A'))
            print("Receiver MAC:", getattr(wlan_layer, 'ra', 'N/A'))
            print("Type/Subtype:", frame_type_subtype, "(QoS Data)")

            print("PHY Type:", get_phy_type(int(getattr(wlan_radio, 'phy', 'N/A'))))
            print("Data Rate:", getattr(wlan_radio, 'data_rate', 'N/A'))
            print("Channel:", getattr(wlan_radio, 'channel', 'N/A'))
            print("Frequency:", getattr(wlan_radio, 'frequency', 'N/A'))
            print("Signal Strength:", getattr(wlan_radio, 'signal_dbm', 'N/A'), "dBm")

            print("Signal/Noise Ratio:", getattr(radio_layer, 'db_antsignal', 'N/A'), "dB")

            # print(wlan_radio)
            # print(wlan_radio.field_names)
            
            print("MCS index:", getattr(wlan_radio, '11n_mcs_index', 'N/A'))
            print("Bandwidth:", getattr(wlan_radio, '11n_bandwidth', 'N/A'))
            # bandwidth_raw = getattr(wlan_radio, '11n_bandwidth', 'N/A')
            print("Bandwidth:", bandwidth_map.get(getattr(wlan_radio, '11n_bandwidth', 'N/A'), f"N/A"))
            print("Short GI:", getattr(wlan_radio, '11n_short_gi', 'N/A'))

            print("====================================================================================")

            packet_count += 1

            if packet_count >= max_packets:
                break  

        except AttributeError:
            continue  

    cap.close()

# Example usage
pcap_file = "given_QoS_Data.pcap"

# pcap_file = "HowIWiFi_PCAP.pcap"  # Replace with actual file path
parse_pcap(pcap_file)
