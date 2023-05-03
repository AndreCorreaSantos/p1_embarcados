import threading
import requests
import serial
import time
import numpy as np
import platform
import subprocess


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

# Define the first thread
def threadData():
    # do some work
    port = get_port()
    ser = serial.Serial(port, baudrate=115200, timeout=1)
    while(True):

        # read data from the serial port
        time_list = []
        start_time = time.time()
        last_time = start_time

        while True:
            data = ser.read().decode()
            if data:
                time_now = time.time() - start_time
                time_step = time_now - last_time
                time_list.append(time_step) #appendando periodos dos passos
                if len(time_list) > 30:
                    time_list.pop(0)
                bpm = (1/np.average(time_list))*60 #pegando frequencia media dos ultimos 10 passos
                last_time = time_now
                body = {'data':round(bpm/10)*10} 
                response = requests.put("http://127.0.0.1:8000/main",json=body)


# Define the second thread
def threadServer():
    import oauth #iniciando servidor


# Create two threads for the two programs
thread_data = threading.Thread(target=threadData)
thread_server = threading.Thread(target=threadServer)

# Start the threads
thread_data.start()
thread_server.start()

# Wait for both threads to finish
thread_data.join()
thread_server.join()