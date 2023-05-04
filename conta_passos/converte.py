# get serial info from com4
import serial
import time
from scipy.signal import find_peaks
from scipy.signal import butter, filtfilt
import numpy as np
import bib
import matplotlib.pyplot as plt
import max30105
buf = [0 for x in range(32)]
fir_coeffs = [172, 321, 579, 927, 1360,
              1858, 2390, 2916, 3391, 3768, 4012, 4096]
offset = 0
ir_signal_max = 0
ir_signal_min = 0
ir_current = 0
pos_edge = 0
neg_edge = 0
beat_detected = False
ir_avg = 0


def low_pass_fir(sample, offset):
    """Filter a sample using a low-pass FIR filter with a 32 sample buffer."""
    buf[offset] = sample
    z = fir_coeffs[11] * buf[(offset - 11) & 0x1f]

    for i in range(11):
        z += fir_coeffs[i] * (buf[(offset - i) & 0x1f] +
                              buf[(offset - 22 + i) & 0x1f])

    offset += 1
    offset %= 32
    return z >> 15, offset


def average_dc_estimator(sample, ir_avg):
    """Estimate the average DC."""
    ir_avg = ir_avg + (((sample << 15) - ir_avg) >> 4)
    return ir_avg >> 15


def dcRemoval(x, prev_w, alpha):
    w = x + alpha * prev_w
    result = w - prev_w
    return w, result


MEAN_FILTER_SIZE = 5


def meanDiff(M, filterValues, index, sum, count):
    avg = 0
    sum -= filterValues[index]
    filterValues[index] = M
    sum += filterValues[index]

    index += 1
    index = index % MEAN_FILTER_SIZE

    if count < MEAN_FILTER_SIZE:
        count += 1

    avg = sum / count
    return (avg - M), filterValues, index, sum, count

def butter_lowpass(sample, filterResultv):
    filterResultv[0] = filterResultv[1]

    filterResultv[1] = (2.452372752527856026e-1 * sample) + (0.50952544949442879485 * filterResultv[0])



    filterResultresult = filterResultv[0] + filterResultv[1]
    return filterResultresult, filterResultv



filterValues = [0 for x in range(MEAN_FILTER_SIZE)]
index_mean = 0
sum_mean = 0
count_mean = 0
PULSE_MIN_THRESHOLD   =           20      
PULSE_MAX_THRESHOLD     =          800     
PULSE_STEP_RESILIENCY   =          30   
PULSE_SIZE = 20   
ser = serial.Serial('COM8', 115200)
samples = []
inicio = True
comeco = True
index = 0
new_samples = []
ultimo_bat = 1000000000000000000
ultimo_rate = 0
teste = []
antiga = 0
current_state = 0
lastBeat = 0
aoba = bib.MAX30100()
filterResultv = [0, 0]
pulse_list = [30 for x in range(PULSE_SIZE)]
index_pulse = 0
values_down = 0
aguarde = True
while True:
    # read serial data
    data = ser.readline()
    data = data.decode().strip()
    if (data[0]=='h')  :
       

        
        
        
            




    # if len(samples) >= size and comeco:
    #     acabou = time.time()
    #     delta_t = (acabou - iniciou)
    #     for sample in samples:
    #         ir_avg = average_dc_estimator(sample, ir_avg)
    #         nova, offset = low_pass_fir(sample - ir_avg, offset)
    #         new_samples.append(nova)
    #     peaks, _ = find_peaks(new_samples, height=5000, distance=60)
    #     heart_rate = len(peaks) / delta_t * 60
    #     inicio = True
    #     print(f"Rate: {heart_rate}")
    #     new_samples = []
    #     samples = []

    # if not comeco:
    #     a = beat.check_for_beat(ir)
    #     if a:
    #         rate = beat.get_beat_rate()
    #         print(f"Rate: {rate}")

print(teste)
plt.plot(teste[:])

plt.show()
