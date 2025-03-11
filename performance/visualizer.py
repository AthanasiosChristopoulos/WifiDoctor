
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

# throughput_data = [50, 100, 150, 200, 250, 300, 350]  # Example throughput values

# # Calculate percentiles using numpy
# percentile_75 = np.percentile(throughput_data, 75)  # 75th percentile
# percentile_95 = np.percentile(throughput_data, 95)  # 95th percentile

def signal_strength_time():
    
    df = pd.read_csv('collected_data.csv')

    df['Time Arrived'] = df['Time Arrived'].astype(float)
    
    df = df.sort_values(by='Time Arrived')

    plt.figure(figsize=(10, 5))
    
    plt.plot(df['Time Arrived'], df['Signal Strength'], marker='o', linestyle='-', color='b', label='Signal Strength (dBm)')

    plt.xlabel('Time Arrived (s)')
    plt.ylabel('Signal Strength (dBm)')
    plt.title('Wi-Fi Signal Strength Over Time')
    plt.legend()
    plt.grid(True)

    plt.savefig("signal_strength_plot.png")
    print("Plot saved as 'signal_strength_plot.png'")


# ======================================================================================================

if __name__ == "__main__":
    visualize_data()
    signal_strength_time()
