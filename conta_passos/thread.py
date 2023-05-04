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
        port = 'COM8'
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
    

    PULSE_SIZE = 20   


    ultimo_bat = 1000000000000000000

    pulse_list = [30 for x in range(PULSE_SIZE)]
    index = 0
    aguarde = True
    media = 0
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

            data = ser.readline()
            data = data.decode().strip()

            if  data != '':
                time_now = time.time() - start_time
                if data[0] == '1':
                    time_step = time_now - last_step_t
                    step_list.append(time_step) #appendando periodos dos passos
                    if len(step_list) > 30:
                        step_list.pop(0)
                    steps_pm = (1/np.average(step_list))*60 #pegando frequencia media dos ultimos 10 passos
                    last_step_t = time_now

                    body = {
                        'choice':choice,
                        'steps':round(steps_pm/10)*10,
                        'heart':round(media)
                        } 
                    response = requests.put("http://127.0.0.1:8000/main",json=body)

                if data[0] == 'h':
                    ir = data[1:]
                    # Convert to float
                    ir = float(ir)
                    ir = int(ir)
                
                    ir = abs(ir)

                    if ir>100:
                        ultimo_bat = time.time()
                        aguarde = False

                    if time.time() - ultimo_bat > 8:
                        ultimo_bat = time.time()
                        aguarde = True

                    

                    if ir > 80 and time.time() - ultimo_bat > 0.3 and not aguarde:
                        bpm = 60/(time.time() - ultimo_bat)
                        ultimo_bat = time.time()
                    
                        if bpm < 180 and bpm > 40 :
                            pulse_list[index] = bpm
                            index += 1

                        media = np.mean(pulse_list)
                        body = {
                        'choice':choice,
                        'steps':round(steps_pm/10)*10,
                        'heart':round(media)
                        }  
                        print(media)
                        response = requests.put("http://127.0.0.1:8000/main",json=body)
                        aguarde = True
                    index = index % PULSE_SIZE
            
                    

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