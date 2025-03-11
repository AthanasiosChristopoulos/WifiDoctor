import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ======================================================================================================

def visualize_data():
    df = pd.read_csv('reduced_data.csv')
    print("\n========= Wi-Fi Reduced Data =========")
    print(df.to_string(index=False))
    print("=====================================")

# ======================================================================================================

def channel_to_frequency_range(channel):
    if 1 <= channel <= 14:  
        center_freq = 2412 + (channel - 1) * 5  
    elif 36 <= channel <= 64 or 100 <= channel <= 165:  
        center_freq = 5000 + channel * 5  
    else:
        return None  

    low = center_freq - 10
    high = center_freq + 10
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
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6), sharey=True, gridspec_kw={'width_ratios': [2, 2]})

    sorted_bssids = sorted(bssid_data.items(), key=lambda x: x[1][1])

    for bssid, (freq_range, strength) in sorted_bssids:
        x_values = [freq_range[0], freq_range[0], freq_range[-1], freq_range[-1]]
        y_values = [0, strength, strength, 0]

        if freq_range[0] < 2500:  
            ax1.fill_between(x_values, y_values, step="mid", alpha=0.7, label=bssid)
        else:
            ax2.fill_between(x_values, y_values, step="mid", alpha=0.7, label=bssid)

    ax1.set_xlim([2377, 2500])
    ax2.set_xlim([5100, 5900])

    ax1.set_xticks(np.arange(2377, 2500, 5))
    ax2.set_xticks(np.arange(5100, 5900, 100))

    ax1.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)

    ax1.set_xlabel('Frequency (MHz)')
    ax2.set_xlabel('Frequency (MHz)')
    ax1.set_ylabel('Signal Strength (+100 dBm)')

    ax1.legend(loc='best', fontsize=8)
    ax1.grid(True)
    ax2.grid(True)

    fig.subplots_adjust(wspace=0.1)
    plt.suptitle('BSSID Frequency Occupancy with Broken Axis')

    plt.show()

# ======================================================================================================

if __name__ == "__main__":
    visualize_data()
    bssid_data = read_csv('reduced_data.csv')
    plot_bssid_channels(bssid_data)
