import socket
filename = 'subnets.conf'
f = open(filename,'rb')

dict_lab = {}
dict_mac = {}
count = 0

for line in f:
    if count==0:
        line = line.split('\n')
        line = line[0].split("/")
        network_addr = line[0]      #Getting the network address
        cidr = int(line[1])              #Getting the cidr

    elif count==1:
        num_labs = int(line[0])

    elif count>1 and count<=num_labs+1:
        line = line.split('\n')
        line = line[0].split(":")           #creating a dictionary for the labs in the form {'Lab_name':'No.of addresses required'}
        dict_lab[line[0]] = int(line[1])

    elif count > num_labs+1:
        line = line.split('\n')
        line = line[0].split("-")           #creating a dictionary for the mac address in the form {'mac_addr':'Lab_name'}
        dict_mac[line[0]] = line[1]

    count = count + 1

port = 45555
s = socket.socket()
host = ""
s.bind((host, port))
s.listen(5)

while True:
    conn, addr = s.accept()
    data = conn.recv(1024)
    print data
    result = dict_mac.get(data)             #Get Mac Address from Client
    if result is None:
        print "Error: Mac Address not found"
    else:
        print "Lab is : ",result
    print('Done sending')
    conn.send('Thank you for connecting')
    conn.close()
