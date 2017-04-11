import socket
import re
import os
from sys import argv

s = socket.socket()
HOST = ""
PORT = 45555
if len(argv)==2:
    if argv[1] == "-m":
        inputCommand = argv[2]
    elif argv[1] == "-h" or argv[1] == "--help":
        print
        print "Usage: client.py -m <mac_address>"
        print
        exit(0)
else:
    f = os.popen("ifconfig -a")
    for line in f:
        firstline = line.split()
        break
    inputCommand = firstline[len(firstline)-1]

inputCommand = inputCommand.upper()
print inputCommand

# use regex for validating mac address
#validInput = re.match("([0-9a-fA-F]:?){12}", " ".join(inputCommand))

#if validInput is None:
#    exit("ERROR: Validate the input")

s.connect((HOST, PORT))
s.send(inputCommand)
data = s.recv(1024)
print data
s.close()

print('connection closed')
