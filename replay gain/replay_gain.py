import os, sys
import numpy as np
from yulewalker import yulewalk
from scipy.signal import butter, lfilter
from scipy.io import wavfile
import glob

# Code was translated from the original Replay Gain implementation by David Robinson in MATLAB

# Taken rom https://www.mars.org/mailman/public/mad-dev/2004-February/000993.html
# The proposed standard describes a method for computing Replay Gain 
# adjustments, which in any case are just decibel scalefactors. 
# Essentially the energy of the encoded signal is calibrated against a 
# reference level, and the difference is stored as the Replay Gain 
# adjustment value. The reference level set forth in the proposed 
# standard is the SMPTE-sanctioned 83 dB SPL, representing a comfortable 
# average listening level.

def equalloudfilt(fs=48000):
    if fs==44100 or fs==48000:
        EL80 = np.array([[float(j) for j in i.split(',')] for i in ("0,120;20,113;30,103;40,97;50,93;60,91;70,89;80,87;90,86;100,85;200,78;300,76;400,76;500,76;600,76;700,77;800,78;900,79.5;1000,80;1500,79;2000,77;2500,74;3000,71.5;3700,70;4000,70.5;5000,74;6000,79;7000,84;8000,86;9000,86;10000,85;12000,95;15000,110;20000,125;%f,140"%(fs/2)).split(';')])
    elif fs==32000:
        EL80 = np.array([[float(j) for j in i.split(',')] for i in ("0,120;20,113;30,103;40,97;50,93;60,91;70,89;80,87;90,86;100,85;200,78;300,76;400,76;500,76;600,76;700,77;800,78;900,79.5;1000,80;1500,79;2000,77;2500,74;3000,71.5;3700,70;4000,70.5;5000,74;6000,79;7000,84;8000,86;9000,86;10000,85;12000,95;15000,110;%f,115"%(fs/2)).split(';')])
    else:
        raise ValueError("Error: sampling rate %i not supported! Currently, only 32000, 44100 & 48000 allowed."%fs)
    
    f = EL80[:,0]/(fs/2)
    m = 10**((70-EL80[:,1])/20)
    a1, b1 = yulewalk(10, f, m) # NOTE: python yulewalk returns coefficients in opposite order, i.e. first a, then b
    b2, a2 = butter(2, 150/(fs/2), 'highpass')

    return a1, b1, a2, b2

def replaygain(filename):
    fs, y = wavfile.read(filename)
    y_dtype_original = y.dtype
    if y.dtype.kind == 'i': # input bit type is integer, thus convert to float range [-1, +1]
        y = y/np.iinfo(y.dtype).max
    samples = len(y)
    try:
        channels = y.shape[1]
    except:
        channels = 1

    a1, b1, a2, b2 = equalloudfilt(fs);

    # Set the vrms window to 50ms
    rms_window_length = int(np.round(50*(fs/1000)))
    # Which rms value to take as typical of whole file
    percentage = 95
    # Set amount of data (in seconds) to cope at once. Ex.: chunk data in from wave file in 2 second blocks
    block_length = 2
    rms_per_block = int(np.fix((fs*block_length)/rms_window_length))

    if samples < fs*block_length:
        raise Exception('Error: length of audio file not long enough. Min %i samples needed!'%(fs*block_length))

    vrms_all = np.zeros(int((np.fix(samples/(fs*block_length))-1)*rms_per_block)-1)
    for audio_block in range(int(np.fix(samples/(fs*block_length))-1)):
        inaudio = y[(fs*block_length*audio_block)+1 : fs*block_length*(audio_block+1)] # Grab a section of audio

        inaudio = lfilter(b1, a1, inaudio, axis=0)
        inaudio = lfilter(b2, a2, inaudio, axis=0)

        for rms_block in range(rms_per_block-1):
            if channels == 1:
                vrms_all[(audio_block*rms_per_block)+rms_block] = np.mean(inaudio[(rms_block*rms_window_length)+1 : (rms_block+1)*rms_window_length]**2)
            elif channels == 2:
                vrms_left = np.mean(inaudio[(rms_block*rms_window_length)+1 : (rms_block+1)*rms_window_length, 0]**2)
                vrms_right = np.mean(inaudio[(rms_block*rms_window_length)+1 : (rms_block+1)*rms_window_length, 1]**2)
                vrms_all[(audio_block*rms_per_block)+rms_block] = (vrms_left+vrms_right)/2

    vrms_all = 10*np.log10(vrms_all+10**-10);
    vrms_all = np.sort(vrms_all)
    return vrms_all[int(np.round(len(vrms_all)*percentage/100.))]

if __name__ == "__main__":
    ref_vrms = replaygain('ref_pink.wav')
    # print(ref_vrms)

    files = []
    print("Replay Gain\nTaken from the original Replay Gain implementation by David Robinson.\n\nPlease provide one or several paths to analyse.\nEnter them one by one.\nWhen done, press enter without entering anything else.\n")
    pathname = input("Enter a directory or file name: ")
    while(len(pathname) > 0):
        print("Processing... ", end="")
        if os.path.isdir(pathname):
            for folder in os.walk(pathname):
                found = glob.glob(os.path.join(folder[0], "*.wav"))
                if(len(found) > 0):
                    print("\nfound %i files in '%s'... "%(len(found), os.path.split(folder[0])[-1]), end="")
                    files.extend(found)
            print("done.")
            pathname = input("Enter another directory or file name: ")
        elif os.path.exists(pathname):
            files.extend(pathname)
        else:
            print("not found.")
            pathname = input("Enter another directory or file name: ")

    if len(files) == 0:
        sys.exit("\nExit: no files given.")

    confirmation = input("\nGoing to compute %i files. Continue? (y/[n]): ")
    if confirmation != 'y':
        sys.exit("\nExiting...")

    print("\nResults:")
    for file in files:
        vrms = ref_vrms - replaygain(file)
        print("%s: %f"%(os.path.split(file)[-1], vrms))

    print("\nDone.")





