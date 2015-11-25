# This is part of the egresscheck-framework => https://github.com/stufus/egresscheck-framework
# Stuart Morgan <stuart.morgan@mwrinfosecurity.com>
#
# This is the 'template' python script which is minified and included into the framework.

import socket
import sys
import time
import threading

# Set IP addresses and parameters
ip_address = "127.0.0.1"
port_string = "22-25,53,80,389,443,445,993,3306,3389"
threads = 2
sleeptime = 0.1

######################## THESE FUNCTIONS DO THE PORTSCAN ###########################

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

# Perform a TCP portscan
def portscan(ip,ports):
    for p in ports:
        connect_tcp(ip,p)
        connect_udp(ip,p)
        time.sleep(sleeptime)
        sys.stdout.write('W');sys.stdout.flush()
    
######################## THESE FUNCTIONS HANDLE MULTITHREADED SCANS ###########################

def run_multithreaded(portarray):
    # Now go through and build the thread lists
    threadports = build_threads(threads,portarray)
    for i in threadports:
        threading.Thread(target=portscan, args=(ip_address,i,)).start()
    
    # Now join the threads to the main one
    main_thread = threading.currentThread()
    for t in threading.enumerate():
        if t is not main_thread:
            t.join()

# Divvy up the ports into arrays to be scanned by each thread
def build_threads(num_threads,portarray):
    # If there are too many threads, reduce down to the number needed
    threadports = []
    portsize = len(portarray)
    if (portsize<num_threads):
        num_threads = portsize
    for i in range(num_threads):
        threadports.append([])
    groupcount=0
    for i in portarray:
        threadports[groupcount].append(i)
        if groupcount==(num_threads-1):
            groupcount=0
        else:
            groupcount+=1
    return threadports

def build_port_list(portstring):
    temp_list = []
    chunks = portstring.split(',')
    for i in chunks:
        try:
            single_val = int(i)
            if single_val>0 and single_val<65536 and single_val not in temp_list: # May be a single number
                temp_list.append(single_val)
        except:
            chunk_range = i.split('-')
            if len(chunk_range)==2:
                try:
                    lownum = int(chunk_range[0])
                    highnum = int(chunk_range[1])
                except:
                    return 0
                if lownum>0 and highnum<65536 and lownum<=highnum:
                    for c in range(lownum,highnum+1):
                        if c not in temp_list:
                            temp_list.append(c)
                else:
                    return 0
            else:
                return 0
    return temp_list

# Entry point
def start():
    temp_port_list = build_port_list(port_string)
    if temp_port_list==0:
        sys.exit(2)
    elif len(temp_port_list)>0:
        run_multithreaded(temp_port_list)
#        run_singlethreaded(temp_port_list)
    sys.exit(0)

start()

# Finally exit
sys.exit(0)
