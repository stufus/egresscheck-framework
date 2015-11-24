import pprint
import socket
import sys
import time
import threading

#Set IP addresses and parameters
ip_address = "127.0.0.1"
lowport = "1"
highport = "1024"
threads = "500"

# Function to actually send the traffic (TCP)
def connect_tcp(ip,base_port):
    try:
        sys.stdout.write('t');sys.stdout.flush()
        tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpsock.connect((ip, base_port))
        tcpsock.close()
    except:
        pass 

# Function to actually send the traffic (UDP)
def connect_udp(ip,base_port):
    try:
        sys.stdout.write('u');sys.stdout.flush()
        udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpsock.sendto('.',(ip, base_port))
        udpsock.close()
    except: 
        pass

# Divvy up the ports into arrays to be scanned by each thread
def build_threads(num_threads,lowport,highport):
    # If there are too many threads, reduce down to the number needed
    threadports = []
    if (1+highport-lowport)<num_threads:
        num_threads = (1+highport-lowport)
    for i in range(num_threads):
        threadports.append([])
    groupcount=0
    for i in range(lowport,highport+1):
        threadports[groupcount].append(i)
        if groupcount==(num_threads-1):
            groupcount=0
        else:
            groupcount+=1
    return threadports

# Perform a TCP portscan
def portscan(ip,ports):
    for p in ports:
        connect_tcp(ip,p)
        connect_udp(ip,p)
        time.sleep(0.1)
    
# Now go through and build the thread lists
threadports = build_threads(int(threads),int(lowport),int(highport))
pprint.pprint(threadports)
for i in threadports:
    t = threading.Thread(target=portscan, args=(ip_address,i,))
    t.start()

# Now join the threads to the main one
main_thread = threading.currentThread()
for t in threading.enumerate():
    if t is not main_thread:
        t.join()

# Finally exit
sys.exit(0)
