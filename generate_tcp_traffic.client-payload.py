import socket
import sys
import time
import threading
import pprint

#Set IP addresses and parameters
ip_address = "127.0.0.1"
lowport = "1"
highport = "1024"
threads = "100"

# cycle through ranges
base_port = int(lowport)
end_port = int(highport)

# Function to actually send the traffic
def connect_tcp(ip,base_port):
    try:
        sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockobj.connect((ip, base_port))
        sockobj.close()
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
def portscan_tcp(ip,ports):
    for p in ports:
        connect_tcp(ip,p)
    
# Now go through and build the thread lists
threadports = build_threads(int(threads),int(lowport),int(highport))
for i in threadports:
    t = threading.Thread(target=portscan_tcp, args=(ip_address,i,))
    t.start()

# Now join the threads to the main one
main_thread = threading.currentThread()
for t in threading.enumerate():
    if t is not main_thread:
        t.join()

# Finally exit
sys.exit(0)
