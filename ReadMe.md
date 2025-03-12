Run the project (in Linux) using:
    1) go to the project directory ../WifiDoctor$
    2) Run ./performance.sh

From the bashscript performance.sh, you can edit:
    1) Number of packets to be read (NUMBER_OF_PACKETS)
    2) which pcap files (PCAP_FILE_beacon (1.1) and PCAP_FILE (1.2)) to read

Description of project components:

    parser: Is responsible for selecting and writing the fields from wireshark packets that are of interest to the WifiDoctor System
        Input (data_in): 
            1) PCAP_FILE_beacon
            2) PCAP_FILE        
        Output (data_out):
            1) beacon_file.txt
            2) data_file.txt

    monitor: Uses the parsed data, editing it and calculating aggregated data 
        Input (data_out): 
            1) beacon_file.txt
            2) data_file.txt
        Output (data_out):
            1) channel_density.csv
            2) collected_data.csv
            3) reduced_data.csv
            4) reduced_data_beacon.csv

    analyser: Makes the final analysis based on aggregated data and mcs_ind       
        Input (data_in, data_out): 
            1) collected_data.csv
            2) reduced_data.csv
            3) network_density.csv
            4) mcs_table.csv
        Output: prints analysis in the command line
            
    visualizer: Uses the data to create visual results to suplement the analysis       
        Input (data_out): 
            1) collected_data.csv
            2) reduced_data.csv
            3) reduced_data_beacon.csv
        Outputs visual elements in the following directories:
            1) ../graphs
            2) ../tables

