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

inputCommand = argv[2:]

socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket1.connect((HOST, PORT))
socket1.send(inputCommand)
socket1.close()

print('connection closed')
