import socket
import re
from sys import argv

s = socket.socket()
HOST = ""
PORT = 45555

if argv[1] == "-h" or argv[1] == "--help":
    print
    print "Usage: client.py -m <mac_address>"
    print
    exit(0)

# use regex for validating mac address
validInput = re.match("([0-9a-fA-F]:?){12}", " ".join(argv[2:]))

if validInput is None:
    exit("ERROR: Validate the input")

inputCommand = argv[2]

s.connect((HOST, PORT))
s.send(inputCommand)
s.close()

print('connection closed')
