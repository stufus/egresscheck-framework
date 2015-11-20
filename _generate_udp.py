import socket
j=int
E=socket.socket
S=socket.AF_INET
Q=socket.SOCK_DGRAM
import sys
v=sys.exit
u=sys.stdout
import time
A=time.sleep
import thread
V=thread.start_new_thread
ip="127.0.0.1"
lp="1"
hp="2048"
m=j(lp)
y=j(hp)
def B(ip,m):
 try:
  b=E(S,Q)
  b.sendto(".",(ip,m))
  b.close()
  v()
 except:
  pass
 finally:
  pass
while m<y:
 m+=1
 V(B,(ip,m))
 if m%10==0:
  u.write(".")
  u.flush()
 A(0.008)
v()
