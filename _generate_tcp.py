import socket
s=int
v=sys.exit
V=sys.stdout
import time
z=time.sleep
import thread
g=thread.start_new_thread
ip='127.0.0.1'
lp='1'
hp='2048'
f=s(lp)
D=s(hp)
def q(ip,f):
 try:
  o=socket(AF_INET,SOCK_STREAM)
  o.connect((ip,f))
  o.close()
  v()
 except:
  pass
 finally:
  pass
while f<D:
 f+=1
 g(q,(ip,f))
 if f%10==0:
  V.write(".")
  V.flush()
 z(0.008)
v()
