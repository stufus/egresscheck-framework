import socket
import sys
import time
import thread
import pprint

#Set IP addresses and parameters
ip_address = "127.0.0.1"
lowport = "1"
highport = "100"
threads = "50"

# cycle through ranges
base_port = int(lowport)
end_port = int(highport)

# Function to actually send the traffic
def connect_tcp(ip_address,base_port):
    try:
        sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockobj.connect((ip_address, base_port))
        sockobj.close()
    except:
        pass

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

#while base_port<end_port:
#    base_port+=1 
#    thread.start_new_thread(start_socket, (ip_address,base_port))
#    if base_port % 10 == 0:
#        sys.stdout.write(".") 
#        sys.stdout.flush()
#    time.sleep(0.008)
threads = build_threads(int(threads),int(lowport),int(highport))

sys.exit()
