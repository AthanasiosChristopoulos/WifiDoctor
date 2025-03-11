import numpy as np
import matplotlib.pyplot as plt

def test_signal_strength_time():
    # Generate dummy time values (simulating time in seconds)
    time_arrived = np.linspace(1594650021, 1594650021 + 10, 50)  # 50 timestamps over 10 seconds

    # Generate dummy signal strength values (simulating dBm readings)
    signal_strength = np.random.randint(-50, -30, size=50) + np.sin(np.linspace(0, 10, 50)) * 5

    # Plot the dummy data
    plt.figure(figsize=(10, 5))
    plt.plot(time_arrived, signal_strength, marker='o', linestyle='-', color='b', label='Signal Strength (dBm)')

    plt.xlabel('Time Arrived (s)')
    plt.ylabel('Signal Strength (dBm)')
    plt.title('Dummy Wi-Fi Signal Strength Over Time')
    plt.legend()
    plt.grid(True)

    plt.show()

# Run the test function
test_signal_strength_time()
