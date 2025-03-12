#!/bin/bash

clear

# NUMBER_OF_PACKETS=20000
# NUMBER_OF_PACKETS=500
NUMBER_OF_PACKETS=200

# PCAP_FILE_beacon="data_in/library_3.pcap"         
# PCAP_FILE_beacon="data_in/HowIWiFi_PCAP.pcap"    

# PCAP_FILE_beacon="data_in/home.pcap"                              

# PCAP_FILE_beacon="data_in/4_pcaps/home_2_4GHz.pcap" 
# PCAP_FILE_beacon="data_in/4_pcaps/lecture_2_4GHz.pcap"           
# PCAP_FILE_beacon="data_in/4_pcaps/home_5GHz.pcap"   
# PCAP_FILE_beacon="data_in/lecture.pcap"                
# PCAP_FILE_beacon="data_in/4_pcaps/lecture_5GHz.pcap"   

PCAP_FILE_beacon="data_in/distance_2.pcap"         
# PCAP_FILE_beacon="data_in/distance_10.pcap"         

MY_PACKET=1
if [ $MY_PACKET -eq 0 ]; then
    PCAP_FILE="data_in/HowIWiFi_PCAP.pcap"
else
    PCAP_FILE="data_in/library_3.pcap"
    # PCAP_FILE="data_in/library.pcap"
    # PCAP_FILE="data_in/home.pcap"
    # PCAP_FILE="data_in/lecture.pcap"
    PCAP_FILE="data_in/distance_2.pcap"         
    # PCAP_FILE="data_in/distance_10.pcap"  

fi

BEACON_FILE="data_out/beacon_file.txt"
DATA_FILE="data_out/data_file.txt"

COLLECTED_DATA="data_out/collected_data.csv"
REDUCED_DATA="data_out/reduced_data.csv"
NETWORK_DATA="data_out/network_density.csv"

echo "=========================================================================="
echo "Extracting BSSID data from PCAP..."
echo ""

python3 parser.py "$PCAP_FILE_beacon" "$PCAP_FILE" "$BEACON_FILE" "$DATA_FILE" $MY_PACKET $NUMBER_OF_PACKETS

echo "=========================================================================="
echo "Performing Network Analysis..."
echo ""
python3 monitor.py "$BEACON_FILE" "$DATA_FILE" $MY_PACKET

echo "=========================================================================="
echo "Performing Analysis..."
echo ""

python3 analyser.py "$COLLECTED_DATA" "$REDUCED_DATA" "$NETWORK_DATA"

echo "=========================================================================="
echo "Visualizing Results..."
echo ""

python3 visualizer.py "$REDUCED_DATA" "$COLLECTED_DATA" 