import csv
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from scipy import interpolate
from tabulate import tabulate
from scipy import stats
# import great_tables as gt

DATA_OUT_DIR = "data_out"
GRAPH_DIR = "graphs"
REDUCED_DATA_BEACON_FILE = os.path.join(DATA_OUT_DIR, "reduced_data_beacon.csv")
COLLECTED_DATA_FILE = os.path.join(DATA_OUT_DIR, "collected_data.csv")

os.makedirs(DATA_OUT_DIR, exist_ok=True)
# signal_strength_array = [-82,-79,-77,-74,-70,-66,-65,-64,-59,-57]
signal_strength_array = [-82,-79,-74,-70,-65,-57]

# ======================================================================================================

def visualize_data():
    df = pd.read_csv(REDUCED_DATA_BEACON_FILE)

# ======================================================================================================

def channel_to_frequency_range(channel):
    
    if 1 <= channel <= 14:  
        center_freq = 2412 + (channel - 1) * 5  
        low = center_freq - 10          # 20MHz Bandwidth
        high = center_freq + 10
    elif 36 <= channel <= 64 or 100 <= channel <= 165:  
        center_freq = 5000 + channel * 5  
        low = center_freq - 20          # 40MHz Bandwidth
        high = center_freq + 20
    else:
        return None  

    return [low, center_freq - 5, center_freq, center_freq + 5, high]

# ======================================================================================================

def my_read_csv(file_path):
    
    bssid_data = {}

    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            bssid = row['BSSID']
            ssid = row['SSID']
            channel = int(row['Channel'])
            signal_strength = float(row['Average Signal Strength']) + 100  

            frequency_range = channel_to_frequency_range(channel)
            if frequency_range:
                bssid_data[bssid] = (frequency_range, signal_strength, ssid)
    
    return bssid_data

# ======================================================================================================


def plot_bssid_channels(bssid_data):
    
    # Plot for 2.4 GHz range
    sorted_bssids_24ghz = sorted((bssid for bssid, (freq_range, strength, ssid) in bssid_data.items() if freq_range[0] < 2500), key=lambda x: bssid_data[x][1])

    same_AP = []
            
    if sorted_bssids_24ghz:  
        
        fig1, ax1 = plt.subplots(figsize=(8, 6))
        ax1.set_ylim([-10, 80])
        ax1.set_xlim([2402, 2472])
        ax1.set_xticks(np.arange(2402, 2472, 5))
        ax1.set_xlabel('Frequency (MHz)')
        ax1.set_ylabel('Signal Strength (+100 dBm)')
        ax1.grid(True)

        for bssid in sorted_bssids_24ghz:
            if (not (bssid[:15] in same_AP)):
                freq_range, strength, ssid = bssid_data[bssid]
                x_values = [freq_range[0], freq_range[0], freq_range[-1], freq_range[-1]]
                y_values = [0, strength, strength, 0]
                ax1.fill_between(x_values, y_values, step="mid", alpha=0.7, label=f"{bssid}, {ssid}")
                same_AP.append(bssid[:15])

        if ax1.has_data():
            ax1.legend(loc='best', fontsize=8)
            plt.suptitle('2.4 GHz BSSID Frequency Occupancy')
            fig1.savefig(os.path.join(GRAPH_DIR, "2.4GHz_Occupancy.png"), dpi=300)
        else:
            plt.close(fig1)  

        # ==========================================================================================
        # ==========================================================================================

        same_AP = []

        # Plot for 5 GHz range
        sorted_bssids_5ghz = sorted((bssid for bssid, (freq_range, strength, ssid) in bssid_data.items() if freq_range[0] >= 2500), key=lambda x: bssid_data[x][1])

        if sorted_bssids_5ghz:  
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            ax2.set_ylim([-10, 80])
            ax2.set_xlim([5160, 5845])
            ax2.set_xticks([5180, 5200, 5220, 5240, 5260, 5280, 5300, 5320, 
                            5500, 5520, 5540, 5560, 5580, 5600, 5620, 5640, 
                            5660, 5680, 5700, 5720, 5745, 5765, 5785, 5805, 5825])
            ax2.set_xlabel('Frequency (MHz)')
            ax2.set_ylabel('Signal Strength (+100 dBm)')
            ax2.grid(True)

            for bssid in sorted_bssids_5ghz:
                if (not (bssid[:15] in same_AP)):
                    freq_range, strength, ssid = bssid_data[bssid]
                    x_values = [freq_range[0], freq_range[0], freq_range[-1], freq_range[-1]]
                    y_values = [0, strength, strength, 0]
                    ax2.fill_between(x_values, y_values, step="mid", alpha=0.7, label=f"{bssid}, {ssid}")
                    same_AP.append(bssid[:15])

            if ax2.has_data(): 
                ax2.legend(loc='best', fontsize=8)
                plt.suptitle('5 GHz BSSID Frequency Occupancy')
                fig2.savefig(os.path.join(GRAPH_DIR, "5GHz_Occupancy.png"), dpi=300)
                
            else:
                plt.close(fig2)      
                                         
            # plt.show()


# =====================================================================================================

def combined_time_series():

    margin = 0.5
    window_size = 7
    
    df = pd.read_csv(COLLECTED_DATA_FILE)
    df = df.drop_duplicates(subset=['Time Arrived'])

    plt.style.use('bmh')

    df['Time Arrived'] = df['Time Arrived'].astype(float)
    df = df.sort_values(by='Time Arrived')

    averaged_time = []
    averaged_mcs_index = []
    averaged_signal_strength = []
    averaged_data_rate = []
    averaged_short_gi = []

    for i in range(0, len(df), window_size):
        
        group = df.iloc[i:i + window_size]
        avg_mcs_index = group['MCS index'].mean()
        avg_signal_strength = group['Signal Strength'].mean()
        avg_data_rate = group['Data Rate'].mean()
        avg_short_gi = group['Short GI'].mean()

        avg_time = group['Time Arrived'].mean()

        averaged_mcs_index.append(avg_mcs_index)
        averaged_signal_strength.append(avg_signal_strength)
        averaged_data_rate.append(avg_data_rate)
        averaged_short_gi.append(avg_short_gi)
        averaged_time.append(avg_time)

    averaged_df = pd.DataFrame({
        'Time Arrived': averaged_time,
        'MCS index avg': averaged_mcs_index,
        'Signal Strength avg': averaged_signal_strength,
        'Data Rate avg': averaged_data_rate,
        'Short GI avg': averaged_short_gi
    })

    # =========================== Normailized graphs ===========================
    
    mcs_index_min = averaged_df['MCS index avg'].min()
    mcs_index_max = averaged_df['MCS index avg'].max()
    if mcs_index_max == mcs_index_min:
        averaged_df['MCS index avg normalized'] = 0
    else:
        averaged_df['MCS index avg normalized'] = (averaged_df['MCS index avg'] - mcs_index_min) / (mcs_index_max - mcs_index_min)

    signal_strength_min = averaged_df['Signal Strength avg'].min()
    signal_strength_max = averaged_df['Signal Strength avg'].max()
    if signal_strength_max == signal_strength_min:
        averaged_df['Signal Strength avg normalized'] = 0
    else:
        averaged_df['Signal Strength avg normalized'] = (averaged_df['Signal Strength avg'] - signal_strength_min) / (signal_strength_max - signal_strength_min)

    data_rate_min = averaged_df['Data Rate avg'].min()
    data_rate_max = averaged_df['Data Rate avg'].max()
    if data_rate_max == data_rate_min:
        averaged_df['Data Rate avg normalized'] = 0
    else:
        averaged_df['Data Rate avg normalized'] = (averaged_df['Data Rate avg'] - data_rate_min) / (data_rate_max - data_rate_min)

    short_gi_min = averaged_df['Short GI avg'].min()
    short_gi_max = averaged_df['Short GI avg'].max()
    if short_gi_max == short_gi_min:
        averaged_df['Short GI avg normalized'] = 0
    else:
        averaged_df['Short GI avg normalized'] = (averaged_df['Short GI avg'] - short_gi_min) / (short_gi_max - short_gi_min)

    plots = [
        ('MCS index avg normalized', 'Signal Strength avg normalized', 'signal_strength_comparison_avg_normalized.png'),
        ('MCS index avg normalized', 'Data Rate avg normalized', 'data_rate_comparison_avg_normalized.png'),
        ('Signal Strength avg normalized', 'Short GI avg normalized', 'short_gi_comparison_avg_normalized.png')
    ]
    
    colors = ['#1f77b4', '#ff7f0e']  # Blue for first graph, Orange for second graph

    for y1, y2, filename in plots:
        fig, ax = plt.subplots(1, 1, figsize=(14, 6)) 
        ax.plot(averaged_df['Time Arrived'], averaged_df[y1], marker='o', linestyle='-', color=colors[0], label=y1)
        ax.plot(averaged_df['Time Arrived'], averaged_df[y2], marker='o', linestyle='-', color=colors[1], label=y2)

        y_min = min(averaged_df[y1].min(), averaged_df[y2].min())
        y_max = max(averaged_df[y1].max(), averaged_df[y2].max())
        y_margin = (y_max - y_min) * margin
        if y_min == y_max:
            ax.set_ylim( (y_min - 1), (y_max + 1))
        else:
            ax.set_ylim( (y_min - y_margin), (y_max + y_margin))
        ax.set_xlabel('Time Arrived (s)', fontsize=12)
        ax.set_ylabel('Normalized Values', fontsize=12)
        ax.set_title(f'{y1} and {y2} Over Time (Average every {window_size} samples)', fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.6)

        plt.tight_layout()
        plt.savefig(os.path.join(GRAPH_DIR, filename), dpi=300)
        # plt.show()

    # =========================== Subplot comparison ===========================
    
    df['MCS index avg'] = df['MCS index'].rolling(window=window_size).mean()
    df['Signal Strength avg'] = df['Signal Strength'].rolling(window=window_size).mean()
    df['Data Rate avg'] = df['Data Rate'].rolling(window=window_size).mean()
    df['Short GI avg'] = df['Short GI'].rolling(window=window_size).mean()

    plots2 = [
        ('MCS index avg', 'Signal Strength avg', 'signal_strength_comparison_avg.png'),
        ('MCS index avg', 'Data Rate avg', 'data_rate_comparison_avg.png'),
        ('Signal Strength avg', 'Short GI avg', 'short_gi_comparison_avg.png')
    ]

    for y1, y2, filename in plots2:
        fig, ax = plt.subplots(1, 2, figsize=(14, 6))

        for i, (y, color) in enumerate(zip([y1, y2], colors)):
            y_min = df[y].min()
            y_max = df[y].max()
            y_margin = (y_max - y_min) * margin
            ax[i].plot(df['Time Arrived'], df[y], marker='o', linestyle='-', linewidth=0.5, markersize=0.1, color=color, label=y)

            if y_min == y_max:
                ax[i].set_ylim( (y_min - 1), (y_max + 1))
            else:
                ax[i].set_ylim( (y_min - y_margin), (y_max + y_margin))
            ax[i].set_xlabel('Time Arrived (s)', fontsize=12)
            ax[i].set_ylabel(y, fontsize=12)
            ax[i].set_title(f'{y} Over Time (Average every {window_size} samples)', fontsize=14, fontweight='bold')
            ax[i].legend(loc='best', fontsize=10)
            ax[i].grid(True, linestyle='--', alpha=0.6)

        plt.tight_layout()
        plt.savefig(os.path.join(GRAPH_DIR, filename), dpi=300)
        # plt.show()
    


# ======================================================================================================

def display_tables():

    with open('data_out/reduced_data_beacon.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
    headers = reader.fieldnames
    table = [list(row.values()) for row in rows]
    
    df = pd.read_csv('data_out/reduced_data_beacon.csv')
    
    # gt.GT(df).show()
    
    with open('tables/reduced_data_beacon_table.txt', 'w') as file:
        file.write(tabulate(table, headers=headers, tablefmt="pretty", numalign="center", stralign="center"))

    # ===================================================================================================================
    
    with open('data_out/reduced_data.csv', newline='') as csvfile, \
         open('tables/reduced_data_table.txt', 'w') as output_file:
        
        reader = csv.DictReader(csvfile)
        
        table_data = []
        
        for row in reader:
            data = [
                ("BSSID", row['BSSID']),
                ("PHY Type", row['PHY Type']),
                ("Channel", row['Channel']),
                ("Frequency", row['Frequency']),
                ("Average Signal Strength", row['Average Signal Strength']),
                ("Channel Switch Count", row['Channel Switch Count']),
                ("Retry Rate", row['Retry Rate']),
                ("Data Rate", row['Data Rate']),
                ("Throughput", row['Throughput']),
                ("Short GI", row['Short GI']),
                ("MCS index", row['MCS index']),
                ("MIN_Tht", row['MIN_Tht']),
                ("Median_Tht", row['Median_Tht']),
                ("75P_Tht", row['75P_Tht']),
                ("95P_Tht", row['95P_Tht']),
                ("MAX_Tht", row['MAX_Tht']),
                ("Bandwidth", row['Bandwidth'])
            ]
            
            table_data.append(data)
        
        for row in table_data:
            table = tabulate(row, headers=["Metric", "Value"], tablefmt="pretty")
            # print(table)
            output_file.write(table + "\n\n") 
            
    # ===================================================================================================================

    with open('data_out/network_density.csv', newline='') as csvfile, \
         open('tables/network_density_table.txt', 'w') as output_file:

        reader = csv.DictReader(csvfile)

        table_data = []

        for row in reader:
            data = [
                ("Weighted SSID Score", row['Weighted SSID Score']),
                ("Channel Overlap Score", row['Channel Overlap Score']),
                ("Channel Switch Impact", row['Channel Switch Impact']),
                ("PHY Penalty Score", row['PHY penalty score']),
                ("Unique SSIDs Score", row['Unique SSIDs score']),
                ("Final Network Density", row['Final Network Density'])
            ]
            
            table_data.append(data)

        for row in table_data:
            table = tabulate(row, headers=["Metric", "Value"], tablefmt="pretty")
            output_file.write(table + "\n\n")    
                
# ==========================================================================================

def get_wifi_params(reduced_data_file, collected_data_file, file_path="data_in/mcs_table.csv"):
    
    with open(reduced_data_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
                
        for row in reader:
            
            mcs_index = round(float(row["MCS index"].strip()))
            avg_data_rate = float(row["Data Rate"].strip())
            shortGIPercentage = row["Short GI"].strip()
            if(float(shortGIPercentage) > 50):
                shortGI = 400
            else:
                shortGI = 800
            short_gi = shortGI       
            bandwidth = int(row["Bandwidth"].strip())
            avg_rssi = float(row["Average Signal Strength"].strip())
            phy_type_connection = row["PHY Type"].strip()

    # =============================================================================================================================================
    # Find relevant data in MCS table
    
    mcs_index = mcs_index
    if(phy_type_connection == "802.11n (HT)"):
        mcs_index = mcs_index % 8
        
    column_names = [
        'mcs_index', 'spatial_streams', 'modulation_method', 'coding_rate', 
        '20_800ns', '20_400ns', '40_800ns', '40_400ns', '80_800ns', '80_400ns', '160_800ns', '160_400ns'
    ]
    
    df = pd.read_csv(file_path)

    bandwidth_map = {20: 4, 40: 6, 80: 8, 160: 10}
    if bandwidth not in bandwidth_map:
        raise ValueError("Invalid Bandwidth")
    
    bandwidth_column_index_1 = bandwidth_map[bandwidth] if short_gi == 800 else bandwidth_map[bandwidth] + 1
    bandwidth_column_index_2 = bandwidth_column_index_1 + 1 if short_gi == 800 else bandwidth_column_index_1 - 1
    
    # find expected_data_rate
    ss_index = int((bandwidth_column_index_1 - 4) / 2)
    increase_signal_strenth_factor = 3
            
    expected_signal_strength_array = [
        strength + ss_index * increase_signal_strenth_factor for strength in signal_strength_array
    ]            

    # ==================================================================
    # Filter out irrelavant data (not close to samples)

    data_rates = sorted(set(float(x) for x in df[df.columns[[bandwidth_column_index_1, bandwidth_column_index_2]]].values.flatten()))
    
    filtered_data_rates = []
    for rate in data_rates:
        if not filtered_data_rates or abs(rate - filtered_data_rates[-1]) >= 11:
            filtered_data_rates.append(rate)

    # ==================================================================
    
    closest_index = min(range(len(filtered_data_rates)), key=lambda i: abs(filtered_data_rates[i] - avg_data_rate))
    lower_bound = max(0, closest_index - 3)
    upper_bound = min(len(filtered_data_rates), closest_index + 4)
    
    filtered_data_rates = filtered_data_rates[lower_bound:upper_bound]

    closest_index = min(range(len(expected_signal_strength_array)), key=lambda i: abs(expected_signal_strength_array[i] - avg_rssi))
    lower_bound = max(0, closest_index - 2)
    upper_bound = min(len(expected_signal_strength_array), closest_index + 3)
    
    expected_signal_strength_array = expected_signal_strength_array[lower_bound:upper_bound]
    if avg_rssi > -60:
        expected_signal_strength_array = sorted([-20, -30, -40, -50, -60])
    # expected_signal_strength_array = expected_signal_strength_array

    # =============================================================================================================================================
    # Find sampled data
    
    classifications_rate = []
    classifications_rssi = []
    with open(collected_data_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data_rate_sample = float(row["Data Rate"].strip())
            rssi_sample = float(row["Signal Strength"].strip())

            closest_rate = min(filtered_data_rates, key=lambda x: abs(x - data_rate_sample))
            closest_rssi = min(expected_signal_strength_array, key=lambda x: abs(x - data_rate_sample))
            
            classifications_rate.append(closest_rate)
            classifications_rssi.append(closest_rssi)

    
    # =============================================================================================================================================
    # Data Rate Histogram  
             
    plt.figure(figsize=(10, 6), facecolor='white')
    plt.gca().set_facecolor('lightgray')  
    bins = np.array(filtered_data_rates) 
    plt.hist(classifications_rate, bins=bins, rwidth=0.5, align='left', color='orange', edgecolor='black')
    plt.xticks(filtered_data_rates, rotation=45)
    plt.xlabel("Data Rate (Mbps)")
    plt.ylabel("Frequency")
    plt.title("Histogram of Classified ")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    # plt.grid(False)
    
    plt.savefig(os.path.join(GRAPH_DIR, "histogram_data_rate.png"), dpi=300)
    # plt.show()

    # =============================================================================================================================================
    # RSSI Histogram  
      
    plt.figure(figsize=(10, 6), facecolor='white')
    plt.gca().set_facecolor('lightgray')  
    bins = np.array(expected_signal_strength_array) 
    plt.hist(classifications_rssi, bins=bins, rwidth=0.5, align='left', color='purple', edgecolor='black')
    plt.xticks(expected_signal_strength_array, rotation=45)
    plt.xlabel("RSSI (dBm)")
    plt.ylabel("Frequency")
    plt.title("Histogram of Classified RSSI")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    # plt.grid(False)
    
    plt.savefig(os.path.join(GRAPH_DIR, "histogram_rssi.png"), dpi=300)
    # plt.show()
# ==========================================================================================

if __name__ == "__main__":
    
    visualize_data()
    bssid_data = my_read_csv(REDUCED_DATA_BEACON_FILE)
    plot_bssid_channels(bssid_data)
    combined_time_series()

    display_tables()
    reduced_data_file = sys.argv[1]
    collected_data_file = sys.argv[2]

    get_wifi_params(reduced_data_file, collected_data_file)



