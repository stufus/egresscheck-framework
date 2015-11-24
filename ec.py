#!/usr/local/bin/python
import re
import cmd
import signal
import sys
import base64
import tempfile

# Global variable to store the various user-configurable options
ec_opts = { 'SOURCEIP': { 'value': '', 'default': '', 'validation':'^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$', 'required': 0, 'description':'This is the IP address of the client machine; from your point of view, it is the \'source address\' of the connections. It is used to filter out unwanted traffic.' },
            'TARGETIP': { 'value': '', 'default': '', 'validation':'^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$', 'required': 1, 'description':'This is the IP address that the client code will try to connect to.' },
            'PORTSTART': { 'value': '1', 'default': '1', 'validation':'^[0-9]+$', 'required': 1, 'description':'This is the starting port for the egress attempt.' },
            'PORTFINISH': { 'value': '65535', 'default': '65535', 'validation':'^[0-9]+$', 'required': 1, 'description':'This is the finishing port for the egress attempt.' },
            'PROTOCOL': { 'value': 'TCP', 'default': 'TCP', 'validation':'^(TCP|UDP|ALL)$', 'required': 1, 'description':'Chooses the protocol to use. Can be one of \'TCP\', \'UDP\' or \'ALL\' (attempts both TCP and UDP).' },
            'VERBOSITY': { 'value': '0', 'default': '0', 'validation':'^[012]$', 'required': 1, 'description':'Verbosity of the generated egress busting code. 0=none,1=errors,2=progress.' },
            'DELAY': { 'value': '0', 'default': '0', 'validation':'^[0-9]+(\.[0-9]{1,2})?$', 'required': 1, 'description':'Delay between generation of packets.' }
          }

ec_version = "v0.1-pre1"

def colourise(string,colour):
    return "\033["+colour+"m"+string+"\033[0m"

def banner():
    print ""
    print "       .mMMMMMm.           mMMm    M  WWW   W    W  RRRRR"
    print "      mMMMMMMMMMMM.           MM   MM    W   W   W    R   R"
    print "     /MMMM-    -MM.           MM   MM    W   W   W    R   R"
    print "    /MMM.    _  \/  ^         M M M M     W W W W     RRRR"
    print "    |M.    aRRr    /W|        M M M M     W W W W     R  R"
    print "    \/  .. ^^^   wWWW|        M  M  M      W   W      R   R"
    print "       /WW\.  .wWWWW/         M  M  M      W   W      R    R"
    print "       |WWWWWWWWWWW/"
    print "         .WWWWWW.        EgressChecker Mini-Framework "+ec_version+" / @ukstufus"
    print "                            stuart.morgan@mwrinfosecurity.com"
    print ""

def generate_oneliner(lang):
    pycmd = ''
    if (lang=='python' or lang=='python-cmd'):
        pycmd = 'import time;import thread;import socket;X=int;t=socket.socket;K=sys.exit;M=time.sleep;C=thread.start_new_thread;c=socket.AF_INET;'
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
                pycmd += "\n  r.write('[SockError('+str(E)+'):'+str(msg)+']');r.flush()"
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
                pycmd += "\n  r.write('[SockError('+str(E)+'):'+str(msg)+']');r.flush()"
            pycmd += "\n except:"
            if int(ec_opts['VERBOSITY']['value'])>0:
                pycmd += "\n  r.write('[Error:'+str(E)+']');r.flush()"
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
            pycmd += "\n  r.write('.');r.flush()"
        if ec_opts['DELAY']['value']:
            pycmd += "\n M("+ec_opts['DELAY']['value']+")"
        else:
            pycmd += "\n M(0.05)"
        pycmd += "\nK()"

    elif lang=='tcpdump':
        # Sort out the TCP capture filter
        tcpdump_cmd = ['dst host '+ec_opts['TARGETIP']['value']]
        tcpdump_cmd.append('dst portrange '+ec_opts['PORTSTART']['value']+'-'+ec_opts['PORTFINISH']['value'])
        if (ec_opts['SOURCEIP']['value']!=''):
            tcpdump_cmd.append('src host '+ec_opts['SOURCEIP']['value'])

        # Now deal with protocol specifics
        tcpdump_proto = []
        if (ec_opts['PROTOCOL']['value']=='TCP') or (ec_opts['PROTOCOL']['value']=='ALL'):
            tcpdump_proto.append('((tcp[tcpflags]&tcp-syn)>0 && (tcp[tcpflags]&tcp-ack)==0 && tcp)')
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
