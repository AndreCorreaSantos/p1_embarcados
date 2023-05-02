import threading
from processing import get_data
import requests
import serial
import time
import numpy as np

# Define the first thread
def threadData():
    # do some work
    while(True):

        ser = serial.Serial('COM3', baudrate=115200, timeout=1)

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
                body = {'data':bpm} 
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