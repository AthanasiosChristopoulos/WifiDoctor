# WifiDoctor System

## Overview
The **WifiDoctor System** is a tool designed to analyze and visualize Wi-Fi performance based on packet captures. It consists of four main components:

1. **Parser** - Extracts and writes relevant fields from Wireshark packet captures.
2. **Monitor** - Processes parsed data, calculates aggregated information, and produces reduced datasets.
3. **Analyser** - Performs final analysis based on aggregated data and modulation and coding scheme (MCS) indicators.
4. **Visualizer** - Generates visual representations of the processed data for enhanced analysis.

---

## Running the Project (Linux)
To run the WifiDoctor System, follow these steps:

1. **Navigate to the project directory:**  
```sh
cd ../WifiDoctor
```

2. **Execute the performance script:**  
```sh
./performance.sh
```

### Configuration Options
You can modify the following parameters in the `performance.sh` script:
- `NUMBER_OF_PACKETS`: Specifies the number of packets to be read.
- `PCAP_FILE_beacon` (1.1) & `PCAP_FILE` (1.2): Defines which pcap files to process.

---

## Project Components

### 1. Parser
The parser extracts relevant fields from Wireshark packet captures for further analysis.

- **Input (data_in):**  
  - `PCAP_FILE_beacon`
  - `PCAP_FILE`
- **Output (data_out):**  
  - `beacon_file.txt`
  - `data_file.txt`

### 2. Monitor
Processes parsed data, applies transformations, and calculates aggregated statistics.

- **Input (data_out):**  
  - `beacon_file.txt`
  - `data_file.txt`
- **Output (data_out):**  
  - `channel_density.csv`
  - `collected_data.csv`
  - `reduced_data.csv`
  - `reduced_data_beacon.csv`

### 3. Analyser
Performs final analysis based on aggregated data and MCS indicators.

- **Input (data_in, data_out):**  
  - `collected_data.csv`
  - `reduced_data.csv`
  - `network_density.csv`
  - `mcs_table.csv`
- **Output:**  
  - Analysis results printed in the command line.

### 4. Visualizer
Generates visual representations of the processed data to supplement the analysis.

- **Input (data_out):**  
  - `collected_data.csv`
  - `reduced_data.csv`
  - `reduced_data_beacon.csv`
- **Output:**  
  - Visuals saved in:
    - `../graphs`
    - `../tables`

---

## Directory Structure
```
WifiDoctor/
├── performance.sh
├── parser/
├── monitor/
├── analyser/
├── visualizer/
├── graphs/
├── tables/
```

---

## License
This project is licensed under the MIT License.

