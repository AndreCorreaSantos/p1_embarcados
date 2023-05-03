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
        step_list = []
        heart_list = []
        start_time = time.time()
        last_step_t = start_time
        steps_pm = 0
        bpm = 0
        choice = 0

        while True:
            data = ser.read().decode()
            if data:
                time_now = time.time() - start_time
                if data == '1':
                    time_step = time_now - last_step_t
                    step_list.append(time_step) #appendando periodos dos passos
                    if len(step_list) > 30:
                        step_list.pop(0)
                    steps_pm = (1/np.average(step_list))*60 #pegando frequencia media dos ultimos 10 passos
                    last_step_t = time_now

                    body = {
                        'choice':choice,
                        'steps':round(steps_pm/10)*10,
                        'heart':round(bpm/10)*10
                        } 
                    response = requests.put("http://127.0.0.1:8000/main",json=body)

                if data == '2':
                    time_heart = time_now - last_heart_t
                    heart_list.append(time_heart) #appendando periodos dos passos
                    if len(heart_list) > 30:
                        heart_list.pop(0)
                    bpm = (1/np.average(heart_list))*60 #pegando frequencia media dos ultimos 10 passos
                    last_heart_t = time_now

                    body = {
                        'choice':choice,
                        'steps':round(steps_pm/10)*10,
                        'heart':round(bpm/10)*10
                        }  
                    response = requests.put("http://127.0.0.1:8000/main",json=body)

                if data == '3':
                    choice != choice
                    body = {
                        'choice':choice,
                        'steps':round(steps_pm/10)*10,
                        'heart':round(bpm/10)*10
                        } 
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