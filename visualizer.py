import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from scipy import interpolate

# Define paths
DATA_OUT_DIR = "data_out"
REDUCED_DATA_BEACON_FILE = os.path.join(DATA_OUT_DIR, "reduced_data_beacon.csv")
COLLECTED_DATA_FILE = os.path.join(DATA_OUT_DIR, "collected_data.csv")

os.makedirs(DATA_OUT_DIR, exist_ok=True)

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

def read_csv(file_path):
    
    bssid_data = {}

    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            bssid = row['BSSID']
            channel = int(row['Channel'])
            signal_strength = float(row['Average Signal Strength']) + 100  

            frequency_range = channel_to_frequency_range(channel)
            if frequency_range:
                bssid_data[bssid] = (frequency_range, signal_strength)
    
    return bssid_data

# ======================================================================================================


def plot_bssid_channels(bssid_data):
    
    # Plot for 2.4 GHz range
    sorted_bssids_24ghz = sorted((bssid for bssid, (freq_range, strength) in bssid_data.items() if freq_range[0] < 2500), key=lambda x: bssid_data[x][1])

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
                freq_range, strength = bssid_data[bssid]
                x_values = [freq_range[0], freq_range[0], freq_range[-1], freq_range[-1]]
                y_values = [0, strength, strength, 0]
                ax1.fill_between(x_values, y_values, step="mid", alpha=0.7, label=bssid)
                same_AP.append(bssid[:15])

        if ax1.has_data():
            ax1.legend(loc='best', fontsize=8)
            plt.suptitle('2.4 GHz BSSID Frequency Occupancy')
            plt.show()
        else:
            plt.close(fig1)  

        # ==========================================================================================
        # ==========================================================================================

        same_AP = []

        # Plot for 5 GHz range
        sorted_bssids_5ghz = sorted((bssid for bssid, (freq_range, strength) in bssid_data.items() if freq_range[0] >= 2500), key=lambda x: bssid_data[x][1])

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
                    freq_range, strength = bssid_data[bssid]
                    x_values = [freq_range[0], freq_range[0], freq_range[-1], freq_range[-1]]
                    y_values = [0, strength, strength, 0]
                    ax2.fill_between(x_values, y_values, step="mid", alpha=0.7, label=bssid)
                    same_AP.append(bssid[:15])

            if ax2.has_data(): 
                ax2.legend(loc='best', fontsize=8)
                plt.suptitle('5 GHz BSSID Frequency Occupancy')
                plt.show()
            else:
                plt.close(fig2)


# =====================================================================================================

def time_series():
    
    df = pd.read_csv(COLLECTED_DATA_FILE)
    df = df.drop_duplicates(subset=['Time Arrived'])

    margin = 0.7
    plt.style.use('bmh')    # bmh
    
    # Signal Strength
    df['Time Arrived'] = df['Time Arrived'].astype(float)
    df = df.sort_values(by='Time Arrived')

    # ======================================================================================================
    # Create subplots (1 row, 2 columns)
    #  MCS Index Signal Strength
    fig, ax = plt.subplots(1, 2, figsize=(14, 6))

    y_min_mcs = df['MCS index'].min()
    y_max_mcs = df['MCS index'].max()
    y_margin_mcs = (y_max_mcs - y_min_mcs) * margin
    # ax[0].plot(df['Time Arrived'], df['MCS index'], marker='o', markersize=6, linestyle='-', color='#ff7f0e', label='MCS I ndex')
    ax[0].scatter(df['Time Arrived'], df['MCS index'], marker='o', linestyle='-', color='#ff7f0e', label='MCS Index')
    ax[0].set_ylim(y_min_mcs - y_margin_mcs, y_max_mcs + y_margin_mcs)
    ax[0].set_xlabel('Time Arrived (s)', fontsize=12)
    ax[0].set_ylabel('MCS Index', fontsize=12)
    ax[0].set_title('MCS Index Over Time (Original)', fontsize=14, fontweight='bold')
    ax[0].legend(loc='best', fontsize=10)
    ax[0].grid(True, linestyle='--', alpha=0.6)
    
    y_min_signal = df['Signal Strength'].min()
    y_max_signal = df['Signal Strength'].max()
    y_margin_signal = (y_max_signal - y_min_signal) * margin
    # ax[1].plot(df['Time Arrived'], df['Signal Strength'], marker='o', markersize=6, linestyle='-', color='#1f77b4', label='Signal Strength (dBm)')
    ax[1].scatter(df['Time Arrived'], df['Signal Strength'], marker='o', linestyle='-', color='#1f77b4', label='Signal Strength (dBm)')
    ax[1].set_ylim(y_min_signal - y_margin_signal, y_max_signal + y_margin_signal)
    ax[1].set_xlabel('Time Arrived (s)', fontsize=12)
    ax[1].set_ylabel('Signal Strength (dBm)', fontsize=12)
    ax[1].set_title('Signal Strength Over Time (Original)', fontsize=14, fontweight='bold')
    ax[1].legend(loc='best', fontsize=10)
    ax[1].grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    # plt.savefig(os.path.join(DATA_OUT_DIR, "signal_strength_comparison.png"), dpi=300)
    plt.show()

    # ======================================================================================================
    # MCS Index Data Rate
    fig, ax = plt.subplots(1, 2, figsize=(14, 6))

    y_min_mcs = df['MCS index'].min()
    y_max_mcs = df['MCS index'].max()
    y_margin_mcs = (y_max_mcs - y_min_mcs) * margin
    ax[0].plot(df['Time Arrived'], df['MCS index'], marker='o', markersize=6, linestyle='-', color='#ff7f0e', label='MCS Index')
    ax[0].set_ylim(y_min_mcs - y_margin_mcs, y_max_mcs + y_margin_mcs)
    ax[0].set_xlabel('Time Arrived (s)', fontsize=12)
    ax[0].set_ylabel('MCS Index', fontsize=12)
    ax[0].set_title('MCS Index Over Time (Original)', fontsize=14, fontweight='bold')
    ax[0].legend(loc='best', fontsize=10)
    ax[0].grid(True, linestyle='--', alpha=0.6)
    
    y_min_rate = df['Data Rate'].min()
    y_max_rate = df['Data Rate'].max()
    y_margin_rate = (y_max_rate - y_min_rate) * margin
    ax[1].plot(df['Time Arrived'], df['Data Rate'], marker='o', markersize=6, linestyle='-', color='#2ca02c', label='Data Rate (Mbps)')
    ax[1].set_ylim(y_min_rate - y_margin_rate, y_max_rate + y_margin_rate)
    ax[1].set_xlabel('Time Arrived (s)', fontsize=12)
    ax[1].set_ylabel('Data Rate (Mbps)', fontsize=12)
    ax[1].set_title('Data Rate Over Time (Original)', fontsize=14, fontweight='bold')
    ax[1].legend(loc='best', fontsize=10)
    ax[1].grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    # plt.savefig(os.path.join(DATA_OUT_DIR, "data_rate_comparison.png"), dpi=300)
    plt.show()

# ======================================================================================================

def printCSV():
    print("Running:")
    with open('data_out/reduced_data.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        
        with open('data_out/formatted_reduced_data.txt', 'w') as output_file:
            for row in reader:
                output_file.write(f"BSSID: {row['BSSID']}\n")
                output_file.write(f"PHY Type: {row['PHY Type']}\n")
                output_file.write(f"Channel: {row['Channel']}\n")
                output_file.write(f"Frequency: {row['Frequency']}\n")
                output_file.write(f"Average Signal Strength: {row['Average Signal Strength']}\n")
                output_file.write(f"Channel Switch Count: {row['Channel Switch Count']}\n")
                output_file.write(f"Retry Rate: {row['Retry Rate']}\n")
                output_file.write(f"Data Rate: {row['Data Rate']}\n")
                output_file.write(f"Throughput: {row['Throughput']}\n")
                output_file.write(f"Short GI: {row['Short GI']}\n")
                output_file.write(f"MCS index: {row['MCS index']}\n")
                output_file.write(f"MIN_Tht: {row['MIN_Tht']}\n")
                output_file.write(f"Median_Tht: {row['Median_Tht']}\n")
                output_file.write(f"75P_Tht: {row['75P_Tht']}\n")
                output_file.write(f"95P_Tht: {row['95P_Tht']}\n")
                output_file.write(f"MAX_Tht: {row['MAX_Tht']}\n")
                output_file.write("\n")  # Add a blank line between rows for readability

# ======================================================================================================

if __name__ == "__main__":
    
    visualize_data()
    bssid_data = read_csv(REDUCED_DATA_BEACON_FILE)
    plot_bssid_channels(bssid_data)
    # time_series()
    # printCSV()













# def time_series():

#     df = pd.read_csv(COLLECTED_DATA_FILE)

#     margin = 0.7
#     plt.style.use('bmh')    # bmh
    
#     # Signal Strength
#     df['Time Arrived'] = df['Time Arrived'].astype(float)
#     df = df.sort_values(by='Time Arrived')

#     y_min_signal = df['Signal Strength'].min()
#     y_max_signal = df['Signal Strength'].max()
#     y_margin_signal = (y_max_signal - y_min_signal) * margin

#     plt.figure(figsize=(10, 6))
#     plt.plot(df['Time Arrived'], df['Signal Strength'], marker='o', markersize=6, linestyle='-', color='#1f77b4', label='Signal Strength (dBm)')
    
#     plt.ylim(y_min_signal - y_margin_signal, y_max_signal + y_margin_signal)
    
#     plt.xlabel('Time Arrived (s)', fontsize=12)
#     plt.ylabel('Signal Strength (dBm)', fontsize=12)
#     plt.title('Signal Strength Over Time', fontsize=14, fontweight='bold')
#     plt.legend(loc='best', fontsize=10)
#     plt.grid(True, linestyle='--', alpha=0.6)
#     plt.tight_layout()
#     plt.savefig(os.path.join(DATA_OUT_DIR, "signal_strength_plot.png"), dpi=300)
#     plt.show()

#     # MCS Index
#     y_min_mcs = df['MCS index'].min()
#     y_max_mcs = df['MCS index'].max()
#     y_margin_mcs = (y_max_mcs - y_min_mcs) * margin

#     plt.figure(figsize=(10, 6))
#     plt.plot(df['Time Arrived'], df['MCS index'], marker='o', markersize=6, linestyle='-', color='#ff7f0e', label='MCS Index')
    
#     plt.ylim(y_min_mcs - y_margin_mcs, y_max_mcs + y_margin_mcs)
    
#     plt.xlabel('Time Arrived (s)', fontsize=12)
#     plt.ylabel('MCS Index', fontsize=12)
#     plt.title('MCS Index Over Time', fontsize=14, fontweight='bold')
#     plt.legend(loc='best', fontsize=10)
#     plt.grid(True, linestyle='--', alpha=0.6)
#     plt.tight_layout()
#     plt.savefig(os.path.join(DATA_OUT_DIR, "mcs_index_plot.png"), dpi=300)
#     plt.show()

#     # Data Rate
#     y_min_rate = df['Data Rate'].min()
#     y_max_rate = df['Data Rate'].max()
#     y_margin_rate = (y_max_rate - y_min_rate) * margin

#     plt.figure(figsize=(10, 6))
#     plt.plot(df['Time Arrived'], df['Data Rate'], marker='o',markersize=6, linestyle='-', color='#2ca02c', label='Data Rate (Mbps)')
    
#     plt.ylim(y_min_rate - y_margin_rate, y_max_rate + y_margin_rate)
    
#     plt.xlabel('Time Arrived (s)', fontsize=12)
#     plt.ylabel('Data Rate (Mbps)', fontsize=12)
#     plt.title('Data Rate Over Time', fontsize=14, fontweight='bold')
#     plt.legend(loc='best', fontsize=10)
#     plt.grid(True, linestyle='--', alpha=0.6)
#     plt.tight_layout()
#     plt.savefig(os.path.join(DATA_OUT_DIR, "data_rate_plot.png"), dpi=300)
#     plt.show()


# def time_series():
#     df = pd.read_csv(COLLECTED_DATA_FILE)

#     margin = 0.7
#     plt.style.use('bmh')    # bmh
    
#     # Signal Strength
#     df['Time Arrived'] = df['Time Arrived'].astype(float)
#     df = df.sort_values(by='Time Arrived')

#     # Interpolation for smooth curve
#     spl_signal = interpolate.make_interp_spline(df['Time Arrived'], df['Signal Strength'], k=3)
#     x_signal_new = np.linspace(df['Time Arrived'].min(), df['Time Arrived'].max(), 500)
#     y_signal_new = spl_signal(x_signal_new)

#     y_min_signal = y_signal_new.min()
#     y_max_signal = y_signal_new.max()
#     y_margin_signal = (y_max_signal - y_min_signal) * margin

#     plt.figure(figsize=(10, 6))
#     plt.plot(x_signal_new, y_signal_new, linestyle='-', color='#1f77b4', label='Signal Strength (dBm)', lw=2)
#     plt.ylim(y_min_signal - y_margin_signal, y_max_signal + y_margin_signal)
    
#     plt.xlabel('Time Arrived (s)', fontsize=12)
#     plt.ylabel('Signal Strength (dBm)', fontsize=12)
#     plt.title('Signal Strength Over Time', fontsize=14, fontweight='bold')
#     plt.legend(loc='best', fontsize=10)
#     plt.grid(True, linestyle='--', alpha=0.6)
#     plt.tight_layout()
#     plt.savefig(os.path.join(DATA_OUT_DIR, "signal_strength_plot.png"), dpi=300)
#     plt.show()

#     # MCS Index
#     spl_mcs = interpolate.make_interp_spline(df['Time Arrived'], df['MCS index'], k=3)
#     x_mcs_new = np.linspace(df['Time Arrived'].min(), df['Time Arrived'].max(), 500)
#     y_mcs_new = spl_mcs(x_mcs_new)

#     y_min_mcs = y_mcs_new.min()
#     y_max_mcs = y_mcs_new.max()
#     y_margin_mcs = (y_max_mcs - y_min_mcs) * margin

#     plt.figure(figsize=(10, 6))
#     plt.plot(x_mcs_new, y_mcs_new, linestyle='-', color='#ff7f0e', label='MCS Index', lw=2)
#     plt.ylim(y_min_mcs - y_margin_mcs, y_max_mcs + y_margin_mcs)
    
#     plt.xlabel('Time Arrived (s)', fontsize=12)
#     plt.ylabel('MCS Index', fontsize=12)
#     plt.title('MCS Index Over Time', fontsize=14, fontweight='bold')
#     plt.legend(loc='best', fontsize=10)
#     plt.grid(True, linestyle='--', alpha=0.6)
#     plt.tight_layout()
#     plt.savefig(os.path.join(DATA_OUT_DIR, "mcs_index_plot.png"), dpi=300)
#     plt.show()

#     # Data Rate
#     spl_rate = interpolate.make_interp_spline(df['Time Arrived'], df['Data Rate'], k=3)
#     x_rate_new = np.linspace(df['Time Arrived'].min(), df['Time Arrived'].max(), 500)
#     y_rate_new = spl_rate(x_rate_new)

#     y_min_rate = y_rate_new.min()
#     y_max_rate = y_rate_new.max()
#     y_margin_rate = (y_max_rate - y_min_rate) * margin

#     plt.figure(figsize=(10, 6))
#     plt.plot(x_rate_new, y_rate_new, linestyle='-', color='#2ca02c', label='Data Rate (Mbps)', lw=2)
#     plt.ylim(y_min_rate - y_margin_rate, y_max_rate + y_margin_rate)
    
#     plt.xlabel('Time Arrived (s)', fontsize=12)
#     plt.ylabel('Data Rate (Mbps)', fontsize=12)
#     plt.title('Data Rate Over Time', fontsize=14, fontweight='bold')
#     plt.legend(loc='best', fontsize=10)
#     plt.grid(True, linestyle='--', alpha=0.6)
#     plt.tight_layout()
#     plt.savefig(os.path.join(DATA_OUT_DIR, "data_rate_plot.png"), dpi=300)
#     plt.show()
