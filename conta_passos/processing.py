import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import serial
import numpy as np
from scipy.fft import fft, fftfreq

import numpy as np

# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
xs = []
ys = []

start_time = time.time()

def get_data():
    ser = serial.Serial('COM3', 115200)
    data = ser.readline().decode().strip()
    return float(data)

# This function is called periodically from FuncAnimation
# def animate(i, xs, ys):

#     # Read temperature (Celsius) from TMP102
#     try:
#         data = get_data()
#     except:
#         data = 1.00
#     print(data)

#     # Add x and y to lists
#     xs.append(round(time.time()-start_time,2))
#     ys.append(data)
    
#     if len(xs) > 25:
#         xs.pop(0)

#     if len(ys) > 25:
#         xs.pop(0)

#     # Limit x and y lists to 20 items
#     xs = xs[-20:]
#     ys = ys[-20:]

#     # Draw x and y lists
#     ax.clear()
#     ax.plot(xs, ys)

#     ax.set_ylim([0, 5])

#     # Format plot
#     plt.xticks(rotation=0, ha='right')
#     plt.subplots_adjust(bottom=0.30)
#     plt.title('Acceleration over time')
#     plt.ylabel('acceleration')

def animate(i, xs, ys):
    # Read temperature (Celsius) from TMP102
    try:
        data = get_data()
    except:
        data = 1.00
    print(data)

    # Add x and y to lists
    xs.append(round(time.time()-start_time,2))
    ys.append(data)

    if len(xs) > 25:
        xs.pop(0)

    if len(ys) > 25:
        ys.pop(0)

    # Perform FFT on y values
    n = len(ys)
    yf = fft(ys)
    xf = fftfreq(n, 1 / 25)[:n // 2]

    # Update amplitude vs frequency plot data
    line.set_data(xf, 2.0 / n * np.abs(yf[0:n//2]))

    # Format plot
    ax.set_ylim([0, 5])
    plt.xticks(rotation=0, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('Amplitude vs Frequency')
    plt.ylabel('Amplitude')
    plt.xlabel('Frequency (Hz)')

    return line,

# Set up plot to call animate() function periodically

ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=10)
plt.show()
