import pyshark

def parse_pcap(file_path):
    cap = pyshark.FileCapture(file_path, display_filter="wlan")
    
    for pkt in cap:
        try:
            # Access WLAN Management (Beacon frame)
            if 'wlan_mgt' in pkt:
                mgt = pkt['wlan_mgt']
                
                # Print out the full WLAN Management to check its structure
                print(mgt)

                # Access Fixed Parameters within the WLAN Management layer
                # The correct field names might be something like 'timestamp' or 'beacon_interval'
                # You should check the available fields by inspecting `mgt`
                
                # Access the Timestamp and Beacon Interval fields in the fixed parameters section
                timestamp = getattr(mgt, 'timestamp', 'N/A')
                beacon_interval = getattr(mgt, 'beacon_interval', 'N/A')

                print("Timestamp:", timestamp)
                print("Beacon Interval:", beacon_interval)
                
                print("-" * 50)
        
        except AttributeError:
            continue
    
    cap.close()

# Example usage
pcap_file = "HowIWiFi_PCAP.pcap"  # Replace with actual file path
parse_pcap(pcap_file)
