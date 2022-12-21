# Description

Code was translated from the original Replay Gain implementation by David Robinson in MATLAB

Taken from https://www.mars.org/mailman/public/mad-dev/2004-February/000993.html

The proposed standard describes a method for computing Replay Gain 
adjustments, which in any case are just decibel scale factors. 
Essentially the energy of the encoded signal is calibrated against a 
reference level, and the difference is stored as the Replay Gain 
adjustment value. The reference level set forth in the proposed 
standard is the SMPTE-sanctioned 83 dB SPL, representing a comfortable 
average listening level.

# Dependencies

This code uses the following python libraries:

- numpy
- scipy
- yulewalker