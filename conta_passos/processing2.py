import time
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import serial
import numpy as np
from scipy.fft import fft, fftfreq
import platform
import numpy as np
import subprocess


# Create figure and axis for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

# Create empty line object to be updated later
line, = ax.plot([], [])

# Initialize x and y data arrays
xs = []
ys = []

start_time = time.time()
last_data = 0


def get_port():
    system = platform.system()
    if system == 'Windows':
        port = 'COM3'
         #no windows tem que estar ligado na com3
    else: #linux


        output = subprocess.check_output(['./detect_ports.sh'])
        # subprocess.Popen(['spotify']) #abrindo spotify
        
        for line in output.decode().splitlines():
            if "Atmel" in line:
                port = line.split(" ")[0]

    return port


def get_data():
    
    port = get_port()

    ser = serial.Serial(port, 115200)
    global last_data
    try:
        data = float(ser.readline().decode().strip())
    except:
        data = last_data

    if data > 10 or data < 0.00000001: #estou tendo erros periodicos na leitura do serial. LEMBRAR DISSO
        data = last_data

    last_data = data
    return data


def animate(i):
    global xs, ys

    # Read data from sensor
    data = get_data()

    # Add data to x and y arrays
    xs.append(time.time()-start_time)
    ys.append(data)

    # Limit x and y arrays to a fixed length
    xs = xs[-75:]
    ys = ys[-75:]

    # Compute FFT of y data
    fft_vals = np.fft.fft(ys)
    freqs = np.fft.fftfreq(len(ys), d=1.0/5.0) # replace 5.0 with your actual sampling frequency

    # Cutoff frequencies from 0 to 0.05
    cutoff_mask = np.logical_and(freqs >= 0, freqs <= 0.05)
    fft_vals[cutoff_mask] = 0

    # Update line data with FFT output
    line.set_data(freqs, np.abs(fft_vals)/2)

    # Set plot limits
    ax.set_xlim([0, 5])
    ax.set_ylim([0, 10])

    maxIndex = np.argmax(np.abs(fft_vals))

    maxFreq = freqs[maxIndex]
    maxAmplitude = np.abs(fft_vals[maxIndex])/2

    steps_pm = maxFreq * 60
    print("steps per minute: ", abs(steps_pm))


    # Format plot
    plt.xticks(rotation=0, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('Amplitude vs Frequency')
    plt.ylabel('Amplitude')
    plt.xlabel('Frequency (Hz)')



# Set up plot with initial empty line object
line, = ax.plot([], [])

# Set up animation loop
ani = animation.FuncAnimation(fig, animate, interval=100)

# Show plot
plt.show()
