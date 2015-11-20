import socket
X=int
t=socket.socket
c=socket.AF_INET
a=socket.SOCK_STREAM
import sys
K=sys.exit
r=sys.stdout
import time
M=time.sleep
import thread
C=thread.start_new_thread
ip="127.0.0.1"
lp="1"
hp="2048"
E=X(lp)
V=X(hp)
def H(ip,E):
 try:
  B=t(c,a)
  B.connect(ip,E)
  B.close()
  K()
 except:
  pass
 finally:
  pass
while E<V:
 E+=1
 C(H,(ip,E))
 if E%10==0:
  r.write(".")
  r.flush()
 M(0.008)
K()
