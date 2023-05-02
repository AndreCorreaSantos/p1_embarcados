import serial


def get_data():
    
    port = 'COM3'
    ser = serial.Serial(port, 115200)
    data = float(ser.readline().decode().strip())
    return data

while True:
    print(1)
    print(get_data())