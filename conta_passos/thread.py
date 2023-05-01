import threading
from processing import get_data
import requests

# Define the first thread
def threadData():
    # do some work
    while(True):
        data = get_data() #mandar data para endpoint do servidor
        body = {'data':data} 
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