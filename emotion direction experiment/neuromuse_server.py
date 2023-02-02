from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from pylsl import StreamInfo, StreamOutlet
import numpy as np
import scipy.io.wavfile as wf
import sounddevice as sd
import random
import glob
from datetime import datetime
import csv
import os
import sys
import math
import time

# parameters
channels = 4 # hardcode the number of audio channels here!
# corrective_gains = np.array([1., 1., 1.239, 1.239]) # at listening position for -20dBFS pink noise (front, back, left, right)
corrective_gains = np.array([0.83, 0.8, 1., 1.]) # at listening position for -20dBFS pink noise (front, back, left, right)

# select sound card
sd.default.device = 'Focusrite USB ASIO, ASIO'


# ========================
# User info

if(len(sys.argv) > 1):
    code = sys.argv[1]
else:
    code = input("Enter participant code: ")

if(len(sys.argv) > 5):
    age = sys.argv[2]
    gender = sys.argv[3]
    handed = sys.argv[4]
    experiment_type = sys.argv[5]
else:
    age = input("Enter participant age: ")
    gender = input("Enter participant gender (m/f/n): ")
    handed = input("Enter participant handedness (l/r): ")
    experiment_type = input("\nWhat kind of experiment are you doing? ([a]rousal, or [v]alence): ")

print("\nParticipant %s: %s, %s, %s\n"%(code, age, gender, handed))

# ========================
# musical excerpts

if(experiment_type[0] == 'a'):
    print("Loading arousal files...")
    high = [i.replace('\\', '/') for i in glob.glob('wav/ha/*.wav')]
    low = [i.replace('\\', '/') for i in glob.glob('wav/la/*.wav')]
elif(experiment_type[0] == 'v'):
    print("Loading valence files...")
    high = [i.replace('\\', '/') for i in glob.glob('wav/hv/*.wav')]
    low = [i.replace('\\', '/') for i in glob.glob('wav/lv/*.wav')]
else:
    print("No appropriate choice taken (a or v)! Exiting...")
    exit(0)

# shuffle the samples
random.shuffle(high)
random.shuffle(low)

def group_list(l, block_size):
    return [l[n:n+block_size] for n in range(0, len(l), block_size)]

# group the randomised samples into groups of n
block_size = 3
high_grouped = group_list(high, block_size)
low_grouped = group_list(low, block_size)

def generate_position_array(positions, iterations):
    r = list(range(positions)) * math.ceil(iterations)
    random.shuffle(r)
    return r[:int(positions*iterations)]

# generate a randomised position array and zip it together with our grouped samples
high_positioned = list(zip(generate_position_array(channels, len(high_grouped)/channels), high_grouped))
low_positioned = list(zip(generate_position_array(channels, len(low_grouped)/channels), low_grouped))

# join both lists and shuffle them once more to randomise between high and low
blocks = high_positioned + low_positioned
random.shuffle(blocks)

print(' ================== ')
for i in blocks:
    print(i)
print(' ================== ')


# ========================
# CSV file

def writeCSVLine(line):
    ts = [datetime.timestamp(datetime.now())]
    ts.extend(line)
    with open('%s_events.csv'%(code), 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(ts)

print('\n === Preparing events CSV file...')
writeCSVLine(['Experiment', experiment_type])
writeCSVLine(['Paritcipant', code, age, gender, handed])


# ========================
# Lab Streaming Layer

print('\n === Connecting to LSL stream...')
info = StreamInfo('MyMarkerStream3','Markers',1,0,'int32','myuniquesourceid23443')
outlet = StreamOutlet(info)


# ========================
# Websocket class

class SimpleEcho(WebSocket):
    block_index = 0
    sample_index = 0

    def handleConnected(self):
        self.block_index = 0
        self.sample_index = 0

        writeCSVLine(['connected'])
        self.sendMessage('type ' + experiment_type[0])
        print(self.address, 'connected')

    def handleClose(self):
        writeCSVLine(['closed'])
        print(self.address, 'closed')

    def handleMessage(self):
        print(" - received: " + self.data)
        writeCSVLine([self.data])
        if(self.data == 'play'):
            self.play_next()
        elif(self.data[:8] == 'baseline'):
            outlet.push_sample([12])
        elif(self.data == 'rest 5000'):
            outlet.push_sample([10])

    def play_next(self):
        b = blocks[self.block_index]
        ch = b[0]
        s = b[1][self.sample_index]

        r, w = wf.read(s)
        l = 48000*21#21#len(w)
        o = np.zeros((l, channels), dtype=w.dtype)
        o[:l, ch] = w[:l] * corrective_gains[ch]

        sl = s.split('/')
        line = ['play', ch, sl[1], sl[2].split('.')[0]]
        writeCSVLine(line)

        marker = 0
        if(sl[1][0] == 'l'):
            marker = ch*2 + 1
        elif(sl[1][0] == 'h'):
            marker = (ch+1) * 2
        outlet.push_sample([marker])

        print('play: %s (%s) at channel %i (marker %i)'%(sl[2], sl[1][0], ch, marker))

        sd.play(o, r)
        sd.wait()

        writeCSVLine(['stop'])

        self.sample_index += 1
        if(self.sample_index == block_size):
            self.sample_index = 0
            self.block_index += 1
            if(self.block_index == len(blocks)):
                print(' sent: end')
                self.sendMessage('end')
            else:
                print(' sent: block ' + str(self.block_index/len(blocks)))
                self.sendMessage('block ' + str(self.block_index/len(blocks)))
        else:
            print(' sent: sample')
            self.sendMessage('sample')

server = SimpleWebSocketServer('', 8001, SimpleEcho)

print("\n === Starting Neuromuse websocket server...")
server.serveforever()