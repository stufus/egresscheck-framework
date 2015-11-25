#!/usr/local/bin/python
import re
import cmd
import signal
import sys
import base64
import tempfile

# Global variable to store the various user-configurable options
ec_opts = { 'SOURCEIP': { 'value': '', 'default': '', 'validation':'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', 'required': 0, 'description':'This is the IP address of the client machine; from your point of view, it is the \'source address\' of the connections. It is used to filter out unwanted traffic.' },
            'TARGETIP': { 'value': '', 'default': '', 'validation':'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', 'required': 1, 'description':'This is the IP address that the client code will try to connect to.' },
            'PORTS': { 'value': '22-25,53,80,443,445,3306,3389', 'default': '22-25,53,80,443,445,3306,3389', 'validation':'^[-0-9,]+$', 'required': 1, 'description':'This is the port range to egress check.' },
            'PROTOCOL': { 'value': 'TCP', 'default': 'TCP', 'validation':'^(TCP|UDP|ALL)$', 'required': 1, 'description':'Chooses the protocol to use. Can be one of \'TCP\', \'UDP\' or \'ALL\' (attempts both TCP and UDP).' },
            'VERBOSITY': { 'value': '0', 'default': '0', 'validation':'^[012]$', 'required': 1, 'description':'Verbosity of the generated egress busting code. 0=none,1=errors,2=progress.' },
            'DELAY': { 'value': '0', 'default': '0', 'validation':'^[0-9]+(\.[0-9]{1,2})?$', 'required': 1, 'description':'Delay between generation of packets.' },
            'THREADS': { 'value': '1', 'default': '1', 'validation':'^[0-9]{1,8}$', 'required': 1, 'description':'Number of simultaneous packet-generation threads to spawn.' }
          }

ec_version = "v0.1-pre1"

def colourise(string,colour):
    return "\n\033["+colour+"m"+string+"\033[0m"

def banner():
    print ""
    print "       .mMMMMMm.             MMm    M   WW   W   WW   RRRRR"
    print "      mMMMMMMMMMMM.           MM   MM    W   W   W    R   R"
    print "     /MMMM-    -MM.           MM   MM    W   W   W    R   R"
    print "    /MMM.    _  \/  ^         M M M M     W W W W     RRRR"
    print "    |M.    aRRr    /W|        M M M M     W W W W     R  R"
    print "    \/  .. ^^^   wWWW|        M  M  M      W   W      R   R"
    print "       /WW\.  .wWWWW/         M  M  M      W   W      R    R"
    print "       |WWWWWWWWWWW/"
    print "         .WWWWWW.        EgressChecker Mini-Framework "+ec_version
    print "                     stuart.morgan@mwrinfosecurity.com | @ukstufus"
    print ""

def generate_oneliner(lang):
    pycmd = ''
    if (lang=='python' or lang=='python-cmd'):
		pycmd += "import socket\n"
		pycmd += "import sys\n"
		pycmd += "K=sys.exit\n"
		pycmd += "F=len\n"
		pycmd += "D=range\n"
		pycmd += "C=int\n"
		pycmd += "u=socket.socket\n"
		pycmd += "B=socket.AF_INET\n"
        if (ec_opts['PROTOCOL']['value']=='TCP') or (ec_opts['PROTOCOL']['value']=='ALL'):
		    pycmd += "d=socket.SOCK_STREAM\n"
        if (ec_opts['PROTOCOL']['value']=='UDP') or (ec_opts['PROTOCOL']['value']=='ALL'):
		    pycmd += "s=socket.SOCK_DGRAM\n"
        if int(ec_opts['VERBOSITY']['value'])>0:
		    pycmd += "Y=sys.stdout\n"
        if ec_opts['DELAY']['value']!='0':
		    pycmd += "import time\n"
		    pycmd += "z=time.sleep\n"
		    pycmd += "V="+ec_opts['DELAY']['value']+"\n"
        if int(ec_opts['THREADS']['value'])>1:
		    pycmd += "import threading\n"
		    pycmd += "T=threading.currentThread\n"
		    pycmd += "L=threading.Thread\n"
		    pycmd += "W=threading.enumerate\n"
		    pycmd += "k="+ec_opts['THREADS']['value']+"\n"
		pycmd += "j=\""+ec_opts['TARGETIP']['value']+"\"\n"
		pycmd += "p=\""+ec_opts['PORTS']['value']+"\"\n"
        if (ec_opts['PROTOCOL']['value']=='TCP') or (ec_opts['PROTOCOL']['value']=='ALL'):
			pycmd += "def H(ip,base_port):\n"
			pycmd += " try:\n"
	        if int(ec_opts['VERBOSITY']['value'])>0:
			    pycmd += "  Y.write('t');Y.flush()\n"
			pycmd += "  n=u(B,d)\n"
			pycmd += "  n.connect((ip,base_port))\n"
			pycmd += "  n.close()\n"
			pycmd += " except:\n"
			pycmd += "  pass\n"
        if (ec_opts['PROTOCOL']['value']=='UDP') or (ec_opts['PROTOCOL']['value']=='ALL'):
			pycmd += "def E(ip,base_port):\n"
			pycmd += " try:\n"
	        if int(ec_opts['VERBOSITY']['value'])>0:
			    pycmd += "  Y.write('u');Y.flush()\n"
			pycmd += "  w=u(B,s)\n"
			pycmd += "  w.sendto('.',(ip,base_port))\n"
			pycmd += "  w.close()\n"
			pycmd += " except:\n"
			pycmd += "  pass\n"
		pycmd += "def b(ip,ports):\n"
		pycmd += " for p in ports:\n"
        if (ec_opts['PROTOCOL']['value']=='TCP') or (ec_opts['PROTOCOL']['value']=='ALL'):
		    pycmd += "  H(ip,p)\n"
        if (ec_opts['PROTOCOL']['value']=='UDP') or (ec_opts['PROTOCOL']['value']=='ALL'):
		    pycmd += "  E(ip,p)\n"
		pycmd += "  z(V)\n"
        if int(ec_opts['VERBOSITY']['value'])>0:
		    pycmd += "  Y.write('W');Y.flush()\n"
        if int(ec_opts['THREADS']['value'])>1:
			pycmd += "def Q(portarray):\n"
			pycmd += " y=O(k,portarray)\n"
			pycmd += " for i in y:\n"
			pycmd += "  L(target=b,args=(j,i)).start()\n"
			pycmd += " N=T()\n"
			pycmd += " for t in W():\n"
			pycmd += "  if t is not N:\n"
			pycmd += "   t.join()\n"
			pycmd += "def O(h,portarray):\n"
			pycmd += " y=[]\n"
			pycmd += " U=F(portarray)\n"
			pycmd += " if(U<h):\n"
			pycmd += "  h=U\n"
			pycmd += " for i in D(h):\n"
			pycmd += "  y.append([])\n"
			pycmd += " A=0\n"
			pycmd += " for i in portarray:\n"
			pycmd += "  y[A].append(i)\n"
			pycmd += "  if A==(h-1):\n"
			pycmd += "   A=0\n"
			pycmd += "  else:\n"
			pycmd += "   A+=1\n"
			pycmd += " return y\n"
		pycmd += "def l(portstring):\n"
		pycmd += " x=[]\n"
		pycmd += " r=portstring.split(',')\n"
		pycmd += " for i in r:\n"
		pycmd += "  try:\n"
		pycmd += "   m=C(i)\n"
		pycmd += "   if m>0 and m<65536 and m not in x:\n"
		pycmd += "    x.append(m)\n"
		pycmd += "  except:\n"
		pycmd += "   e=i.split('-')\n"
		pycmd += "   if F(e)==2:\n"
		pycmd += "    try:\n"
		pycmd += "     M=C(e[0])\n"
		pycmd += "     c=C(e[1])\n"
		pycmd += "    except:\n"
		pycmd += "     return 0\n"
		pycmd += "    if M>0 and c<65536 and M<=c:\n"
		pycmd += "     for c in D(M,c+1):\n"
		pycmd += "      if c not in x:\n"
		pycmd += "       x.append(c)\n"
		pycmd += "    else:\n"
		pycmd += "     return 0\n"
		pycmd += "   else:\n"
		pycmd += "    return 0\n"
		pycmd += " return x\n"
		pycmd += "def R():\n"
		pycmd += " a=l(p)\n"
		pycmd += " if a==0:\n"
		pycmd += "  K(2)\n"
		pycmd += " elif F(a)>0:\n"
        if int(ec_opts['THREADS']['value'])>1:
		    pycmd += "  Q(a)\n"
        else:
            pycmd += "  b(j,a)\n"
		pycmd += " K(0)\n"
		pycmd += "R()\n"
		pycmd += "K(0)\n"

    elif lang=='tcpdump':
        # Sort out the TCP capture filter
        tcpdump_cmd = ['dst host '+ec_opts['TARGETIP']['value']]
        if (ec_opts['SOURCEIP']['value']!=''):
            tcpdump_cmd.append('src host '+ec_opts['SOURCEIP']['value'])

        # Now deal with protocol specifics
        tcpdump_proto = []
        if (ec_opts['PROTOCOL']['value']=='TCP') or (ec_opts['PROTOCOL']['value']=='ALL'):
            tcpdump_proto.append('((tcp[tcpflags]&(tcp-syn|tck-ack))==tcp-syn && tcp)')
        if (ec_opts['PROTOCOL']['value']=='UDP') or (ec_opts['PROTOCOL']['value']=='ALL'):
            tcpdump_proto.append('(udp)')
        
        # Now generate the tcpdump capture command line. Yes I know I'm using mktemp()...
        tf = tempfile.mktemp('.pcap','egress_')
        tcpdump_run = 'tcpdump -n -U -w '+tf+' \''+(' && '.join(tcpdump_cmd))+' && ('+'||'.join(tcpdump_proto)+')\''
        tshark_run = 'tshark -r '+tf+' -Tfields -eip.proto -eip.src -etcp.dstport | sort -u'
        pycmd = [tcpdump_run,tshark_run]

    return pycmd

def print_supported_languages():
    print "   python     "+"| Generates a python egress buster script."
    print "   python-cmd "+"| Generates a python one-liner designed to be copied and pasted."
    print "   tcpdump    "+"| Generates the tcpdump capture command to be run on the target machine."

class ec(cmd.Cmd):

    prompt = colourise('egresschecker>','0;36')+" "

    def do_generate(self, param):
        if ec_opts['TARGETIP']['value'].strip()=='':
            print colourise('Error:','31;1')+" Must specify a target IP. Use 'set TARGETIP x.x.x.x'."
        elif param == '':
            print colourise('Error:','31;1')+" Must specify a language."
            print_supported_languages()
        else:
            cmdLang = param.split()[0].lower()
            if (cmdLang == 'python' or cmdLang=='python-cmd'):
                code = generate_oneliner(cmdLang)
                if (cmdLang=='python'):
                    print colourise('Run the code below on the client machine:','0;32')
                    print 'import sys'
                    print code
                elif (cmdLang=='python-cmd'):
                    print colourise('Run the command below on the client machine:','0;32')
                    print 'python -c \'import base64,sys;exec(base64.b64decode("'+base64.b64encode(code)+'"))\''
            elif cmdLang == 'tcpdump':
                code = generate_oneliner(cmdLang)
                print colourise('Run the command below on the target machine (probably yours) to save connection attempts:','0;32')
                print code[0]
                print colourise('The command below will parse the saved capture file and display the ports on which connections were received:','0;32')
                print code[1]
                pass
            else:
                print colourise('Error:','31;1')+" Invalid language specified."
                print_supported_languages()

    def complete_set(self, text, line, begidx, endidx):
        param = line.partition(' ')[2].upper()
        offset = len(param) - len(text)
        return [s[offset:] for s in ec_opts.keys() if s.startswith(param)]

    def complete_get(self, text, line, begidx, endidx):
        param = line.partition(' ')[2].upper()
        offset = len(param) - len(text)
        return [s[offset:] for s in ec_opts.keys() if s.startswith(param)]

    def do_set(self, param):
        if param != '' and len(param.split())==2:
            cmdVariable = param.split()[0].upper()
            if cmdVariable in ec_opts.keys():
                cmdParam = param.split()[1]
                if re.match(ec_opts[cmdVariable]['validation'],cmdParam):
                    ec_opts[cmdVariable]['value'] = cmdParam
                    print cmdVariable+' => '+cmdParam
                else:
                    print colourise('Error:','31;1')+" Invalid "+cmdVariable+" setting provided"
            else:
                print colourise('Error:','31;1')+" "+cmdVariable+" is not recognised"
        else:
            print colourise('Error:','31;1')+" Variable name and value required. Use \'get\' to see all variables."
     
    def do_get(self, param):
        if param != '':
            cmdVariable = param.split()[0].upper()
            if cmdVariable in ec_opts.keys():
                print cmdVariable+' = '+ec_opts[cmdVariable]['value']
            else:
                print colourise('Error:','31;1')+" "+cmdVariable+" not found"
        else:  
            print "+"+'-'*14+"+"+'-'*19+"+"
            print "| %-12s | %-17s |" % ('Option','Value')
            print "+"+'-'*14+"+"+'-'*19+"+"
            for k,v in ec_opts.iteritems():
                print "| %-12s | %-17s |" % (k,v['value'])
            print "+"+'-'*14+"+"+'-'*19+"+"

    def do_quit(self, param):
        print ""
        return True

    def do_exit(self, param):
        print ""
        return True

    do_EOF=do_exit

def signal_handler(signum, frame):
    print ""
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    banner()
    ec().cmdloop()
