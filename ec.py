#!/usr/local/bin/python
import pprint
import re
import cmd
import signal
import sys
import base64

# Global variable to store the various user-configurable options
ec_opts = { 'REMOTEIP': { 'value': '', 'validation':'^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$', 'required': 0, 'description':'This is the IP address of the target machine. It is used to filter out unwanted traffic.' },
            'TARGETIP': { 'value': '', 'validation':'^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$', 'required': 1, 'description':'This is the IP address that the client code will try to connect to.' },
            'PORTSTART': { 'value': '1', 'validation':'^[0-9]+$', 'required': 1, 'description':'This is the starting port for the egress attempt.' },
            'PORTFINISH': { 'value': '65535', 'validation':'^[0-9]+$', 'required': 1, 'description':'This is the finishing port for the egress attempt.' },
            'PROTOCOL': { 'value': 'TCP', 'validation':'^(TCP|UDP|ALL)$', 'required': 1, 'description':'Chooses the protocol to use. Can be one of \'TCP\', \'UDP\' or \'ALL\' (attempts both TCP and UDP).' },
            'VERBOSITY': { 'value': '0', 'validation':'^[012]$', 'required': 1, 'description':'Verbosity of the generated egress busting code. 0=none,1=errors,2=progress.' },
            'DELAY': { 'value': '0', 'validation':'^[0-9]+$', 'required': 1, 'description':'Delay been generation of packets.' }
           }

def generate_oneliner(lang):
    if lang=='python':
        pycmd = 'import time;import thread;import sys;import socket;X=int;t=socket.socket;K=sys.exit;M=time.sleep;C=thread.start_new_thread;c=socket.AF_INET;'
        if int(ec_opts['VERBOSITY']['value'])>0:
            pycmd += 'r=sys.stdout;'
        pycmd += 'ip="'+ec_opts['TARGETIP']['value']+'";'
        pycmd += 'lp="'+ec_opts['PORTSTART']['value']+'";'
        pycmd += 'hp="'+ec_opts['PORTFINISH']['value']+'";'
        pycmd += 'E=X(lp);V=X(hp)'
        if (ec_opts['PROTOCOL']['value']=='TCP') or (ec_opts['PROTOCOL']['value']=='ALL'):
            pycmd += "\ndef H(ip,E):"
            pycmd += "\n try:"
            pycmd += "\n  B=t(c,socket.SOCK_STREAM)"
            pycmd += "\n  B.connect((ip,E))"
            pycmd += "\n  B.close()"
            pycmd += "\n  K()"
            if int(ec_opts['VERBOSITY']['value'])>0:
                pycmd += "\n except socket.error, msg:"
                pycmd += "\n  r.write('[SockError('+str(E)+'):'+str(msg)+']')"
            pycmd += "\n except:"
            if int(ec_opts['VERBOSITY']['value'])>0:
                pycmd += "\n  r.write('[Error:'+str(E)+']');r.flush()"
            else:
                pycmd += "\n  pass"

        if (ec_opts['PROTOCOL']['value']=='UDP') or (ec_opts['PROTOCOL']['value']=='ALL'):
            pycmd += "\ndef J(ip,E):"
            pycmd += "\n try:"
            pycmd += "\n  B=t(c,socket.SOCK_DGRAM)"
            pycmd += "\n  B.sendto('.',(ip,E))"
            pycmd += "\n  B.close()"
            pycmd += "\n  K()"
            if int(ec_opts['VERBOSITY']['value'])>0:
                pycmd += "\n except socket.error, msg:"
                pycmd += "\n  r.write('[SockError('+str(E)+'):'+str(msg)+']')"
            pycmd += "\n except:"
            if int(ec_opts['VERBOSITY']['value'])>0:
                pycmd += "\n  r.write('[Error:'+str(E)+']')"
            else:
                pycmd += "\n  pass"
        pycmd += "\nwhile E<V:"
        pycmd += "\n E+=1"
        if (ec_opts['PROTOCOL']['value']=='TCP') or (ec_opts['PROTOCOL']['value']=='ALL'):
            pycmd += "\n C(H,(ip,E))"
        if (ec_opts['PROTOCOL']['value']=='UDP') or (ec_opts['PROTOCOL']['value']=='ALL'):
            pycmd += "\n C(J,(ip,E))"
        if int(ec_opts['VERBOSITY']['value'])>1:
            pycmd += "\n if E%10==0:"
            pycmd += "\n  r.write('.')"
        if int(ec_opts['DELAY']['value'])>0:
            pycmd += "\n M("+str(int(ec_opts['DELAY']['value']))+")"
        else:
            pycmd += "\n M(0.01)"
        pycmd += "\nK()"
        return pycmd

class ec(cmd.Cmd):

    prompt = "egresschecker> "

    def do_generate(self, param):
        if param != '':
            cmdLang = param.split()[0].lower()
            if cmdLang == 'python':
                code = generate_oneliner(cmdLang)
                print code+"\n\n"
                print 'python -c \'import base64,sys;exec(base64.b64decode("'+base64.b64encode(code)+'"))\''
            elif cmdLang == 'tcpdump':
                pass
            else:
                print "Error: Invalid language specified."
        else:
            print "Error: Must specify a language. Currently, 'python' and 'tcpdump' are the only supported options." 

    def do_set(self, param):
        if param != '':
            cmdVariable = param.split()[0].upper()
            if cmdVariable in ec_opts.keys():
                cmdParam = param.split()[1]
                if re.match(ec_opts[cmdVariable]['validation'],cmdParam):
                    ec_opts[cmdVariable]['value'] = cmdParam
                    print cmdVariable+' => '+cmdParam
                else:
                    print "Error: Invalid "+cmdVariable+" setting provided"
            else:
                print "Error: "+cmdVariable+" is not recognised"
        else:
            print "Error: Variable name required. Use \'get\' to see all variables"
     
    def do_get(self, param):
        if param != '':
            cmdVariable = param.split()[0].upper()
            if cmdVariable in ec_opts.keys():
                print cmdVariable+' = '+ec_opts[cmdVariable]['value']
            else:
                print "Error: "+cmdVariable+" not found"
        else:  
            print "Showing all variables:"

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
    ec().cmdloop()
