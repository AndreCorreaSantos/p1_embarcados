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
    ser = serial.Serial('COM3', 115200)
    data = float(ser.readline().decode().strip())
    return data

while(True):
    print(2)
    print(get_data())
