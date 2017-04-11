import socket
import re
import os
import sys
from sys import argv

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', 0))
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
server_address = ('<broadcast>', 45555)

if len(argv) >= 2:
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

# use regex for validating mac address
#validInput = re.match("([0-9a-fA-F]:?){12}", " ".join(inputCommand))

#if validInput is None:
#    exit("ERROR: Validate the input")

sent = s.sendto(inputCommand, server_address)
data, server = s.recvfrom(1024)
print >>sys.stderr, 'received "%s"' % data

s.close()

print('connection closed')
