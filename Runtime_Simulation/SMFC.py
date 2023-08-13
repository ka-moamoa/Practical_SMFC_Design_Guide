import csv
from collections import defaultdict
from scipy.signal import butter, lfilter
import matplotlib.pyplot as plt
from datetime import datetime

def butter_lowpass(cutoff, fs, order=5):
        return butter(order, cutoff, fs=fs, btype='low', analog=False)

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def getMFC_data(path):

    #STEP 1: Import raw voltage values from v3_Data.csv and get average of v3 and v0 cells

    columns = defaultdict(list) # each value in each column is appended to a list

    with open(path) as f:
        reader = csv.DictReader(f) # read rows into a dictionary format
        for row in reader: # read a row as {column1: value1, column2: value2,...}
            for (k,v) in row.items(): # go over each column name and value 
                if v != '':
                    columns[k].append(v) # append the value into the appropriate list
                                    # based on column name k

    x2 = columns['unix_time']

    unix_time = []
    for t in x2:
        unix_time.append(int(float(t)))

    d0 = datetime.fromtimestamp(unix_time[0])
    days = []
    for d in unix_time:
        day = datetime.fromtimestamp(d)
        day_from_start = day-d0
        decimal_day = day_from_start.total_seconds()/(24 * 3600)
        days.append(decimal_day)

    soil = columns['soil_moisture']
    vwc = []
    for i in range(0, len(soil)):
        vwc.append(float(soil[i]))

    v1 = columns['v0']
    v2 = columns['v1']
    v3 = columns['v2']
    p1 = columns['v3']
    p2 = columns['v4']
    p3 = columns['v5']

    v1_volt = []
    v2_volt = []
    v3_volt = []
    p1_volt = []
    p2_volt = []
    p3_volt = []
    for i in range(0, len(v3)):
        v1_volt.append(float(v1[i]))
        v2_volt.append(float(v2[i]))
        v3_volt.append(float(v3[i]))
        p1_volt.append(float(p1[i]))
        p2_volt.append(float(p2[i]))
        p3_volt.append(float(p3[i]))


    vertical_ave = []
    planar_ave = []

    end = 188750
    for i in range(0, len(v3_volt)):
        vertical_ave.append((v1_volt[i] + v2_volt[i] + v3_volt[i])/3)
        if i<end:
            planar_ave.append((p1_volt[i] + p2_volt[i] + p3_volt[i])/3)
        else:
            planar_ave.append((p2_volt[i] + p3_volt[i])/2) #skip Cell 1 due to data loss

    #STEP 2: Filter them same as what we did in v3_power_plot to get 2 voltage traces

    # Filter requirements.
    order = 6
    fs = 1/60      # sample rate, Hz
    cutoff = 1/(12*3600)  # desired cutoff frequency of the filter, Hz

    # Get the filter coefficients so we can check its frequency response.
    b, a = butter_lowpass(cutoff, fs, order)

    # Filter the data, and plot both the original and filtered signals.
    v3_avg_v = butter_lowpass_filter(vertical_ave, cutoff, fs, order)
    v0_avg_v = butter_lowpass_filter(planar_ave, cutoff, fs, order)

    return days, v0_avg_v, v3_avg_v