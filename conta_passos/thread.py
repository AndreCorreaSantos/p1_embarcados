import threading
import queue

# Define the first thread
def thread1(q):
    # do some work
    data = 1
    # put data in the queue
    q.put(data)
    # do some more work

# Define the second thread
def thread2(q):
    import oauth

# Create a queue
q = queue.Queue()

# Create two threads for the two programs
thread_1 = threading.Thread(target=thread1, args=(q,))
thread_2 = threading.Thread(target=thread2, args=(q,))

# Start the threads
thread_1.start()
thread_2.start()

# Wait for both threads to finish
thread_1.join()
thread_2.join()