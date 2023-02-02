#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
import sys, struct, serial, time, datetime
from pylsl import StreamInfo, StreamOutlet, resolve_stream, StreamInlet
import os
import sys
import time
import serial
import serial.tools.list_ports
from datetime import datetime
import numpy as np
import csv
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import collections

global PPG_ar, GSR_ar

data_vis_l = 300
PPG_ar = collections.deque(np.zeros(data_vis_l))
GSR_ar = collections.deque(np.zeros(data_vis_l))

# participant_code = input("Enter participant code: ")
participant_code = sys.argv[1]

print('Port searching.....')
ports = serial.tools.list_ports.comports(include_links=False)
for port in ports :
    print('Find port '+ port.device)

port = port.device

print('port-',port)

# In[3]:


def wait_for_ack():
    ddata = ""
    ack = struct.pack('B', 0xff)
    while ddata != ack:
        ddata = ser.read(1)# print("0x{}02x".format(ord(ddata[0])))
        print('{}'.format(ddata[0]))
    return


# In[4]:


ser = serial.Serial(port, 115200) #here change only the COM port 
ser.flushInput()
print("port opening, done.")


# In[5]:


# send the set sensors command
ser.write(struct.pack('BBBB', 0x08 , 0x04, 0x01, 0x00))  #GSR and PPG
wait_for_ack()
print("sensor setting, done.")


# In[6]:


# Enable the internal expansion board power
ser.write(struct.pack('BB', 0x5E, 0x01))
wait_for_ack()
print("enable internal expansion board power, done.")


# In[7]:


sampling_freq = 50
clock_wait = int((2 << 14) / sampling_freq)

ser.write(struct.pack('<BH', 0x05, clock_wait))
wait_for_ack()

# send start streaming command
ser.write(struct.pack('B', 0x07))
wait_for_ack()
print("start command sending, done.")

# read incoming data
ddata = b''
numbytes = 0
framesize = 8 # 1byte packet type + 3byte timestamp + 2 byte GSR + 2 byte PPG(Int A13)


# In[8]:


# Configure the shimmer to collect the user defined time period.
seconds = int(10)
t_end = time.time() + seconds

task = 1.0 # dummy task

#  LSL
# Configure a streaminfo
info = StreamInfo(name='MyMarkerStream3', type='GSR_PPG', channel_count=3, channel_format='float32',  source_id='myuniquesourceid23443')
# next make an outlet
outlet = StreamOutlet(info)

def read_shimmer(writer):
    ddata = b''
    numbytes = 0
    framesize = 8 # 1byte packet type + 3byte timestamp + 2 byte GSR + 2 byte PPG(Int A13)

    while numbytes < framesize:
        ddata += ser.read(framesize)
        numbytes = len(ddata)
        
    data = ddata[0:framesize]
    ddata = ddata[framesize:]
    numbytes = len(ddata)

    # read packet payload
    (PPG_raw, GSR_raw) = struct.unpack('HH', data[4:framesize])

    # get current GSR range resistor value
    Range = ((GSR_raw >> 14) & 0xff)  # upper two bits
    if(Range == 0):
        Rf = 40.2   # kohm
    elif(Range == 1):
        Rf = 287.0  # kohm
    elif(Range == 2):
        Rf = 1000.0 # kohm
    elif(Range == 3):
        Rf = 3300.0 # kohm
    # convert GSR to kohm value
    gsr_to_volts = (GSR_raw & 0x3fff) * (3.0/4095.0)
    GSR_ohm = Rf/( (gsr_to_volts /0.5) - 1.0)

    # convert PPG to milliVolt value
    PPG_mv = PPG_raw * (3000.0/4095.0)
    ts = datetime.timestamp(datetime.now())
    mysample = [ts, GSR_raw, GSR_ohm, PPG_raw, PPG_mv]
    # mysample = [ts, GSR_ohm, PPG_mv]

    writer.writerow(mysample)

    return PPG_raw, GSR_raw
    # all_data.append(mysample)

    # Send data to LSL
    # outlet.push_sample(mysample)

with open('%s_shimmer.csv'%(participant_code), 'a', newline='') as file:
    writer = csv.writer(file)

    def animation_function(i):
        PPG_raw, GSR_raw = read_shimmer(writer)

        PPG_ar.popleft()
        GSR_ar.popleft()
        PPG_ar.append(PPG_raw)
        GSR_ar.append(GSR_raw)
        ax.cla()
        ax1.cla()
        ax.plot(GSR_ar)
        ax1.plot(PPG_ar)


    # Start animation plot
    fig = plt.figure(figsize=(12,6), facecolor='#DEDEDE')
    ax = plt.subplot(121)
    ax1 = plt.subplot(122)
    ax.set_facecolor('#DEDEDE')
    ax1.set_facecolor('#DEDEDE')
    ani = FuncAnimation(fig, animation_function, interval=50)

    # all_data = [] #saves the result data for the experiments


    # print("Packet Type\tTimestamp\tGSR\tPPG")
    print("Data reccording started...")

    plt.show()

    # while True:
    #     read_shimmer(writer)



