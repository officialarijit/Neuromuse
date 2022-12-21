# Description

The NeuroMUSE direction listening experiment.

# Dependencies

This code uses the following python libraries:

- numpy
- scipy
- sounddevice
- SimpleWebSocketServer
- pylsl

# Usage

Execute neuromuse_server.py and load the html page emotion.html in a browser. Using a Socket, the two should communicate with each other. The server records all user input and meta data into a CSV file. Also, it launches Lab Streaming Layer events to synchronise with other equipment that supports the protocol.

Additionally, if you wish to record data using the Shimmer sensors, you may use the ShimmerLSL.py file