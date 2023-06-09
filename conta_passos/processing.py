import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import serial
import numpy as np
from scipy.fft import fft, fftfreq
import platform
import numpy as np
import subprocess


# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
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
        output = subprocess.check_output(["./detect_ports.sh"])
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

    if abs(data-last_data) > 5 or abs(data-last_data) < 0.05: #estou tendo erros periodicos na leitura do serial. LEMBRAR DISSO
        data = last_data

    last_data = data
    return data

def get_raw_data():
    ser = serial.Serial('COM3', 115200)
    return ser.readline().decode().strip()

def animate(i, xs, ys):
    # Read temperature (Celsius) from TMP102
    # try:
    data = get_raw_data()
    print(data)
    # except:
    #     data = 1.00

    # Add x and y to lists
    global start_time

    time_now = round(time.time()-start_time,2)
    # if start_time > 20:
    #     start_time = time_now

    xs.append(time_now)
    # print(xs)
    ys.append(data)


    # Limit x and y lists to 20 item

    if len(xs)>75:
        xs.pop(0)


    if len(ys)>75:
        ys.pop(0)

    # print(len(xs))

    # Perform FFT on y values
    # n = len(ys)
    # yf = fft(ys)
    # xf = fftfreq(len(ys))

    # Draw amplitude vs frequency plot
    ax.clear()
    # ax.plot(xf, 2.0 / n * np.abs(yf[0:n//2]))
    ax.plot(xs,ys)

    ax.set_ylim([0, 2.5])
    ax.set_xlim([0, 20])

    # Format plot
    # if(len(xf)> 0):
    #     print(xf)
    plt.xticks(rotation=0, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('Amplitude vs Frequency')
    plt.ylabel('Amplitude')
    plt.xlabel('Frequency (Hz)')



# Set up plot to call animate() function periodically

ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=100)
plt.show()
