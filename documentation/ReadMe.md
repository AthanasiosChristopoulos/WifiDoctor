parser:

    Input (data_in): 
        1) HowIWiFi_PCAP.pcap
        2) my_capture_beacon.pcap
    
    Output (data_out):
        1) beacon_file.txt
        2) data_file.txt

monitor:

    Input (data_out): 
        1) beacon_file.txt
        2) data_file.txt
    
    Output (data_out):
        1) channel_density.csv
        2) collected_data.csv
        3) reduced_data.csv

visualizer:        

    Input (data_out): 
        1) collected_data.csv
        2) reduced_data.csv
    
    Output (data_out):

