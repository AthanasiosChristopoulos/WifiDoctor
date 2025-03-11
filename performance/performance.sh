#!/bin/bash

clear

PCAP_FILE="HowIWiFi_PCAP.pcap"
BSSID_FILE="bssid_list.txt"

echo "Extracting BSSID data from PCAP..."
python3 parser.py "$PCAP_FILE" "$BSSID_FILE"

echo "Analyzing Wi-Fi density..."
python3 monitor.py "$BSSID_FILE"

echo "Visualizing Results..."
python3 visualizer.py