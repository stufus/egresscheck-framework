import sys;import socket;import time;import threading
O=socket.socket;L=socket.AF_INET;m=socket.SOCK_STREAM;p=socket.SOCK_DGRAM
B=threading.currentThread;r=threading.Thread;h=threading.enumerate
x=sys.stdout
s=range
N=time.sleep
P="127.0.0.1"
M=1
t=20
q=5
o=0.1
def u(ip,bp):
 try:
  x.write('t');x.flush()
  F=O(L,m)
  F.connect((ip,bp))
  F.close()
 except:
  pass
def J(ip,bp):
 try:
  x.write('u');x.flush()
  v=O(L,p)
  v.sendto('.',(ip,bp))
  v.close()
 except:
  pass
def E(l,M,t):
 V=[]
 if(1+t-M)<l:
  l=(1+t-M)
 for i in s(l):
  V.append([])
 n=0
 for i in s(M,t+1):
  V[n].append(i)
  if n==(l-1):
   n=0
  else:
   n+=1
 return V
def e(ip,Z):
 for p in Z:
  u(ip,p)
  J(ip,p)
  N(o);x.write('W');x.flush()
V=E(q,M,t)
for i in V:
 r(target=e,args=(P,i)).start()
c=B()
for t in h():
 if t is not c:
  t.join()
sys.exit(0)
