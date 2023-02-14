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

from paho.mqtt import client as mqtt_client



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


sampling_freq = 50.33
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
# seconds = int(10)
# t_end = time.time() + seconds

# task = 1.0 # dummy task

start_time = datetime.fromtimestamp(datetime.timestamp(datetime.now()))
current_time = 0

#  LSL
# Configure a streaminfo
# info = StreamInfo(name='Shimmer', type='GSR_PPG', channel_count=2, channel_format='float32',  source_id='myuid34234')
# next make an outlet
# outlet = StreamOutlet(info)


# broker = 'broker.emqx.io'

broker = 'localhost'

port = 1883
topic = ["GSC_uS",'PPG_mv']
client_id = 'client1'
# username = 'emqx'
# password = 'public'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


try:
    client = connect_mqtt()
    client.loop_start()

    print("Data reccording started...")
    with open('%s_shimmer.csv'%(participant_code), 'a', newline='') as file:
        writer = csv.writer(file)

        while True:
            while numbytes < framesize:
                ddata += ser.read(framesize)
                numbytes = len(ddata)

            data = ddata[0:framesize]
            ddata = ddata[framesize:]
            numbytes = len(ddata)


            (packettype) = struct.unpack('B', data[0:1])
            (timestamp0, timestamp1, timestamp2) = struct.unpack('BBB',data[1:4])

            # read packet payload
            (PPG_raw, GSR_raw) = struct.unpack('HH', data[4:framesize])



            # get current GSR range resistor value
            Range = ((GSR_raw >> 14) & 0xff)  # upper two bits
            if(Range == 0):
                Rf = 40200   # ohm
            elif(Range == 1):
                Rf = 287000  # ohm
            elif(Range == 2):
                Rf = 1000000 # ohm
            elif(Range == 3):
                Rf = 3300000  # ohm

            # convert GSR to ohm value
            gsr_to_volts = (GSR_raw & 0x3fff) * (3.0/4095.0)
            GSR_ohm = Rf/( (gsr_to_volts /0.5) - 1.0)
            GSC_uS = (1/GSR_ohm)*1000000 #uS
            

            # convert PPG to milliVolt value
            PPG_mv = PPG_raw * (3000.0/4095.0)
    
            current_time = datetime.fromtimestamp(datetime.timestamp(datetime.now()))


            ts = datetime.timestamp(datetime.now())
            
            delta = current_time - start_time
            diff = delta.total_seconds()
            
            mysampleCSV = [ts, GSR_ohm, GSC_uS, PPG_mv, diff]            

            # Send data to local MQTT
            result1 =  client.publish(topic[0], payload =str(GSC_uS) )
            result2 =  client.publish(topic[1], payload =str(PPG_mv) )

            # result: [0, 1]
            status1 = result1[0]
            status2 = result2[0]
            if status1 == 0 and status2 ==0:
                pass
                #print("MSG Send to topic: {} and {}".format(topic[0], topic[1]))
            else:
                print("Failed to send message to topics")

            writer.writerow(mysampleCSV)

            # print('Time diff {} sec'.format(diff))
            
            # if diff >=60.0:
            #     break
            # else:
            #     continue
            

                
        # all_data.append(mysample) 

        # Send data to LSL
        # outlet.push_sample(mysample)
        
except KeyboardInterrupt:
#send stop streaming command
    ser.write(struct.pack('B', 0x20))
    print()
    print("stop command sent, waiting for ACK_COMMAND")
    wait_for_ack()
    print("ACK_COMMAND received.")
    #close serial port
    ser.close()
    print("All done")


