import socket
from math import pow, ceil, log

def min_pow2(x):  # how many bits do we need to borrow
    z = log(x, 2)  # to cover number of hosts
    if int(z) != z:  # in math language:
        z = ceil(z)  # to which integer power do
    return int(z)  # we need to raise 2 to get the number that is ge "x"


def getmask(cidr):  # ex. 24 -> 255.255.255.0
    arr = [0 for i in range(4)]  # creating list of four 0s
    y = int(cidr / 8)  # how many octets of 255
    if y > 0:  # if mask < 8
        for z in range(y):
            arr[z] = 255
        arr[z + 1] = int(256 - pow(2, 8 - (cidr - 8 * y)))
    else:
        arr[0] = 256 - pow(2, 8 - cidr)
    return arr


def getnet(ipaddr, nmask):  # Get network address from ip and mask
    net = [0 for i in range(4)]
    for i in range(4):
        net[i] = int(ipaddr[i]) & int(nmask[i])  # octet and mask
    return net


def getfirst(ipaddr):  # Get first usable address from ip and mask
    addr = ipaddr[:]  # list is mutable, not to change the global value
    return addr


def getlast(ipaddr, nmask):  # Get last usable address from ip and mask
    addr = getbcast(ipaddr, nmask)
    return addr


def getbcast(ipaddr, nmask):  # Get broadcast address from ip and mask
    net = [0 for i in range(4)]
    for i in range(4):
        net[i] = int(ipaddr[i]) | 255 - int(nmask[i])  # octet or wildcard mask
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
    tuppe format : tupple(1) : has the ip address for next machine to be assigned
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
        print " SUBNET: %d NEEDED: %3d (%3d %% of) ALLOCATED %4d ADDRESS: %15s :: %15s - %-15s :: %15s MASK: %d (%15s)" % \
              (x + 1,
               lab_req[x][0],
               (lab_req[x][0] * 100) / (int(pow(2, bits)) - 2),
               int(pow(2, bits)) - 2,
               norm(ipaddr),
               norm(getfirst(ipaddr)),
               norm(getlast(ipaddr, getmask(int(32 - bits)))),
               norm(getbcast(ipaddr, getmask(int(32 - bits)))),
               32 - bits,
               norm(getmask(int(32 - bits))))

        ipaddr = getnextaddr(ipaddr, getmask(int(32 - bits)))


def allote_ip(mac_address):
    lab_name = dict_mac.get(mac_address)

    for i in range(len(state_arr)):
        if(state_arr[i][1] == lab_name):
            next_state = generate_next(state_arr[i])
            if(next_state[2] <= dict_lab[lab_name]):
                state_arr[i] = next_state
            else:
                return "No more IPs can be alloted"
                exit(0)
            temp = next_state[0]
            return_ip = str(temp[0]) + '.' + str(temp[1]) + '.' + str(temp[2]) + '.' + str(temp[3])
            return return_ip


filename = 'subnets.conf'
f = open(filename, 'rb')

dict_lab = {}
dict_mac = {}
lab_req = []
state_arr = []
count = 0
num_hosts = 0

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
        line = line[0].split(":")           # creating a dictionary for the labs in the form {'Lab_name':'No.of addresses required'}
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

lab_req = sorted(lab_req, reverse=True)
mask = getmask(cidr)
network_addr = getNetworkAddr(network_addr)

vlsm(getnet(network_addr, mask), lab_req)

port = 45555
s = socket.socket()
host = ""
s.bind((host, port))
s.listen(5)

while True:
    conn, addr = s.accept()
    data = conn.recv(1024)
    print data

    result = dict_mac.get(data)             # Get the lab name using the MAC address given by client
    if result is None:
        print "Error: Mac Address not found"

    conn.send(allote_ip(data))

    print('Done sending')

    conn.close()
