#!/bin/bash

clear

# Define file paths
PCAP_FILE="my_capture_beacon.pcap"
BSSID_FILE="bssid_list.txt"

# Run PCAP Parser
echo "Extracting BSSID data from PCAP..."
python3 parser_density.py "$PCAP_FILE" "$BSSID_FILE"

# Run Performance Monitor
echo "Analyzing Wi-Fi density..."
python3 monitor_density.py "$BSSID_FILE"

echo "Visualizing Results..."
python3 visualizer.py