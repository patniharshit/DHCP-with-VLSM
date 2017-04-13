import socket
import re
import os
import sys
import json
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
validInput = re.match("([0-9a-fA-F]:?){12}", " ".join([inputCommand]))

if validInput is None:
    exit("ERROR: Validate the input")

# send DHCP discovery request
sent = s.sendto(inputCommand, server_address)
print >>sys.stderr, 'Broadcast request for IP for mac address ' + str(inputCommand)

# recieve DHCP offer
data, server = s.recvfrom(1024)
data = json.loads(data)

print >>sys.stderr, '\nDHCP offer for IP from server: "%s"\n' % data[0]

# send request
req = ("server_ip", data[0])
req = json.dumps(req)
sent = s.sendto(req, server_address)
print >>sys.stderr, 'Request send to %s for %s' % ('server', data[0])

# recieve ack
data, server = s.recvfrom(1024)
data = json.loads(data)
print >>sys.stderr, '\nACK: "%s"' % data
gate = data[3].split("/")
gate = gate[0]
dns = data[4].split("/")
dns = dns[0]
print '\nIP address: %s\nNetwork Address : %s\nBroadcast Address: %s\nGateway: %s\nDNS: %s\n' % (data[0], data[1], data[2], gate, dns)
s.close()
