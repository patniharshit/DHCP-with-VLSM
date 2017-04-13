import socket
from math import pow, ceil, log
import sys
import json


def min_pow2(x):
    z = log(x, 2)
    if int(z) != z:
        z = ceil(z)
    return int(z)


def getmask(cidr):
    arr = [0, 0, 0, 0]
    y = int(cidr / 8)
    z = -1
    for z in range(y):
        arr[z] = 255
    arr[z + 1] = int(256 - pow(2, 8 - (cidr - 8 * y)))
    return arr


def getnet(ipaddr, nmask):
    net = []
    net.append(int(ipaddr[0]) & int(nmask[0]))
    net.append(int(ipaddr[1]) & int(nmask[1]))
    net.append(int(ipaddr[2]) & int(nmask[2]))
    net.append(int(ipaddr[3]) & int(nmask[3]))
    return net


def getbcast(ipaddr, nmask):
    net = []
    net.append(int(ipaddr[0]) | 255 - int(nmask[0]))
    net.append(int(ipaddr[1]) | 255 - int(nmask[1]))
    net.append(int(ipaddr[2]) | 255 - int(nmask[2]))
    net.append(int(ipaddr[3]) | 255 - int(nmask[3]))
    return net


def getnextaddr(ipaddr, nmask):
    ipaddr = getbcast(ipaddr, nmask)
    for i in range(4):
        if ipaddr[3 - i] == 255:
            ipaddr[3 - i] = 0
            if ipaddr[3 - i - 1] != 255:
                ipaddr[3 - i - 1] += 1
                break
        else:
            ipaddr[3 - i] += 1
            break
    return ipaddr


def generate_next(tupple):
    """
    tupple format : tupple(1) : has the ip address for next machine to be assigned
                   tupple(2) : has the name of the Lab_name
                   tupple(3) : Has the number of machine allocated I address after allocation of recent IP addr
    """
    # Increase the number to be assigned by 1
    addr = tupple[0]
    addr[0] = int(addr[0])
    addr[1] = int(addr[1])
    addr[2] = int(addr[2])
    addr[3] = int(addr[3])
    if addr[3] == 255:
        if addr[2] == 255:
            if addr[1] == 255:
                addr[0] += 1
                addr[1] = 0
                addr[2] = 0
                addr[3] = 0
            else:
                addr[1] += 1
                addr[2] = 0
                addr[3] = 0
        else:
            addr[2] += 1
            addr[3] = 0
    else:
        addr[3] += 1

    new_tupple = (addr, tupple[1], tupple[2]+1)

    return new_tupple


def norm(ipaddr):
    addr = ipaddr[:]
    for i in range(len(addr)):
        addr[i] = str(addr[i])
    return ".".join(addr)

def getNetworkAddr(network_addr):
    network_addr = network_addr.split(".")
    for i in range(len(network_addr)):
        network_addr[i] = int(network_addr[i])
    return network_addr

def vlsm(ipaddr, lab_req):
    bits = 0

    for x in range(len(lab_req)):
        bits = min_pow2(lab_req[x][0] + 2)
        ipaddr = getnet(ipaddr, getmask(int(32 - bits)))

        state_arr.append((ipaddr, lab_req[x][1], 0))

        net_lab[lab_req[x][1]] = (norm(ipaddr), norm(getbcast(ipaddr, getmask(int(32 - bits)))), 32-bits)

        ipaddr = getnextaddr(ipaddr, getmask(int(32 - bits)))


def allote_ip(mac_address):

    flag = 0
    if(mac_address in dict_alloted):
        return dict_alloted[mac_address]

    lab_name = dict_mac.get(mac_address)

    for i in range(len(state_arr)):
        if(state_arr[i][1] == lab_name):
            if state_arr[i][2]==0:
                flag = 1

            next_state = generate_next(state_arr[i])
            if(next_state[2] <= dict_lab[lab_name]):
                state_arr[i] = next_state
            else:
                return "No more IPs can be alloted"
                exit(0)
            temp = next_state[0]
            return_ip = str(temp[0]) + '.' + str(temp[1]) + '.' + str(temp[2]) + '.' + str(temp[3]) + "/" + str(net_lab[state_arr[i][1]][2])
            dict_alloted[mac_address] = return_ip
            if flag==1:

                dns_arr[lab_name] = return_ip
            return return_ip


filename = 'subnets.conf'
f = open(filename, 'rb')

dict_lab = {}
dict_mac = {}
dict_alloted = {}
lab_req = []
state_arr = []
net_lab = {}
count = 0
num_hosts = 0
answer = ()
dns_arr={}

for line in f:
    if count == 0:
        line = line.split('\n')
        line = line[0].split("/")
        network_addr = line[0]      # Getting the network address
        cidr = int(line[1])              # Getting the cidr

    elif count == 1:
        num_labs = int(line[0])

    elif count > 1 and count <= num_labs+1:
        line = line.split('\n')
        line = line[0].split(" ")           # creating a dictionary for the labs in the form {'Lab_name':'No.of addresses required'}
        dict_lab[line[0]] = int(line[1])
        lab_req.append((int(line[1]), line[0]))
        num_hosts = num_hosts + int(line[1])  # add number of hosts in the lab to total

    elif count > num_labs+1:
        line = line.split('\n')
        line = line[0].split("-")           # creating a dictionary for the mac address in the form {'mac_addr':'Lab_name'}
        dict_mac[line[0]] = line[1]

    count = count + 1

# check if number of hosts are less than available ip addresses or not
if num_hosts > (pow(2, 32 - cidr) - 2):
    exit("ERROR: Too many hosts")

free_space = pow(2, 32 - cidr) - 2 - num_hosts
dict_lab["OPEN"] = free_space
lab_req.append((free_space, "OPEN"))

lab_req = sorted(lab_req, reverse=True)
mask = getmask(cidr)
network_addr = getNetworkAddr(network_addr)

ser_ip = getnet(network_addr, mask)
network_addr = ser_ip
server_ip = str(network_addr[0]) + "." + str(network_addr[1]) + "." + str(network_addr[2]) + "." + str(network_addr[3])
ser_tup = generate_next((network_addr, "server", 0))

vlsm(ser_tup[0], lab_req)

port = 45555
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = ""
s.bind((host, port))

dict_mac["SERVER"] = "OPEN"
answer1 = net_lab.get("OPEN")
SERVER = allote_ip("SERVER")

while True:
    # detect broadcast from client
    data, address = s.recvfrom(1024)
    print >>sys.stderr, 'Received %s from %s' % (data, address)

    # Get the lab name using the MAC address given by client
    result = dict_mac.get(data)

    if result is None:
        dict_mac[data] = "OPEN"
        answer = net_lab.get("OPEN")
        ans = allote_ip(data)
        result = "OPEN"
    else:
        answer = net_lab.get(result)
        ans = allote_ip(data)

    output = (ans, answer[0], answer[1], dns_arr.get(result), dns_arr.get(result), SERVER)
    output = json.dumps(output)
    s.sendto(output, address)
    print >>sys.stderr, 'Sent DHCP offer for %s back to %s' % (ans, address)

    # Recieve request
    data, address = s.recvfrom(1024)
    print 'Request recieved from client for %s' % (data)

    # Acknowlege request
    data = json.loads(data)
    if(data[0] == SERVER):
        s.sendto(output, address)
        print >>sys.stderr, 'Request acknowledged for %s back to %s' % (ans, address)
    else:
        print "Offer cancelled"

    print('Done sending\n\n')
