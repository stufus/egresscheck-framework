#!/usr/bin/env python
import re
import os
import cmd
import signal
import sys
import base64
import zlib
import tempfile
import datetime

# Global variable to store the various user-configurable options
ec_opts = { 'SOURCEIP': { 'value': '', 'default': '', 'validation':'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', 'required': 0, 'description':'This is the IP address of the client machine; from your point of view, it is the \'source address\' of the connections. It is used to filter out unwanted traffic.' },
            'TARGETIP': { 'value': '', 'default': '', 'validation':'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', 'required': 1, 'description':'This is the IP address that the client code will try to connect to.' },
            'PORTS': { 'value': '22-25,53,80,443,445,3306,3389', 'default': '22-25,53,80,443,445,3306,3389', 'validation':'^[-0-9,]+$', 'required': 1, 'description':'This is the port range to egress check.' },
            'PROTOCOL': { 'value': 'TCP', 'default': 'TCP', 'validation':'^(TCP|UDP|ALL)$', 'required': 1, 'description':'Chooses the protocol to use. Can be one of \'TCP\', \'UDP\' or \'ALL\' (attempts both TCP and UDP).' },
            'VERBOSITY': { 'value': '0', 'default': '0', 'validation':'^[01]$', 'required': 1, 'description':'Verbosity of the generated egress busting code. 0=none,1=progress.' },
            'DELAY': { 'value': '0.1', 'default': '0.1', 'validation':'^[0-9]+(\.[0-9]{1,2})?$', 'required': 1, 'description':'Delay between generation of packets.' },
            'THREADS': { 'value': '25', 'default': '25', 'validation':'^[0-9]{1,8}$', 'required': 1, 'description':'Number of simultaneous packet-generation threads to spawn.' }
          }

ec_generators = ['python','python-cmd','powershell','powershell-cmd','tcpdump']
ec_version = "v0.1-pre2"

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
            pycmd += "def H(ip,bP):\n"
            pycmd += " try:\n"
            if int(ec_opts['VERBOSITY']['value'])>0:
                pycmd += "  Y.write('t');Y.flush()\n"
            pycmd += "  n=u(B,d)\n"
            pycmd += "  n.setblocking(0)\n"
            pycmd += "  n.connect((ip,bP))\n"
            pycmd += "  n.close()\n"
            pycmd += " except:\n"
            pycmd += "  pass\n"
        if (ec_opts['PROTOCOL']['value']=='UDP') or (ec_opts['PROTOCOL']['value']=='ALL'):
            pycmd += "def E(ip,bP):\n"
            pycmd += " try:\n"
            if int(ec_opts['VERBOSITY']['value'])>0:
                pycmd += "  Y.write('u');Y.flush()\n"
            pycmd += "  w=u(B,s)\n"
            pycmd += "  w.setblocking(0)\n"
            pycmd += "  w.sendto('.',(ip,bP))\n"
            pycmd += "  w.close()\n"
            pycmd += " except:\n"
            pycmd += "  pass\n"
        pycmd += "def b(ip,ports):\n"
        pycmd += " for p in ports:\n"
        if (ec_opts['PROTOCOL']['value']=='TCP') or (ec_opts['PROTOCOL']['value']=='ALL'):
            pycmd += "  H(ip,p)\n"
        if (ec_opts['PROTOCOL']['value']=='UDP') or (ec_opts['PROTOCOL']['value']=='ALL'):
            pycmd += "  E(ip,p)\n"
        if ec_opts['DELAY']['value']!='0':
            pycmd += "  z(V)\n"
            if int(ec_opts['VERBOSITY']['value'])>0:
                pycmd += "  Y.write('W');Y.flush()\n"
        if int(ec_opts['THREADS']['value'])>1:
            pycmd += "def Q(pa):\n"
            pycmd += " y=O(k,pa)\n"
            pycmd += " for i in y:\n"
            pycmd += "  L(target=b,args=(j,i)).start()\n"
            pycmd += " N=T()\n"
            pycmd += " for t in W():\n"
            pycmd += "  if t is not N:\n"
            pycmd += "   t.join()\n"
            pycmd += "def O(h,pa):\n"
            pycmd += " y=[]\n"
            pycmd += " U=F(pa)\n"
            pycmd += " if(U<h):\n"
            pycmd += "  h=U\n"
            pycmd += " for i in D(h):\n"
            pycmd += "  y.append([])\n"
            pycmd += " A=0\n"
            pycmd += " for i in pa:\n"
            pycmd += "  y[A].append(i)\n"
            pycmd += "  if A==(h-1):\n"
            pycmd += "   A=0\n"
            pycmd += "  else:\n"
            pycmd += "   A+=1\n"
            pycmd += " return y\n"
        pycmd += "def l(pS):\n"
        pycmd += " x=[]\n"
        pycmd += " r=pS.split(',')\n"
        pycmd += " for i in r:\n"
        pycmd += "  try:\n"
        pycmd += "   m=C(i)\n"
        pycmd += "   if m>0 and m<65536:\n"
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
        pycmd += "      x.append(c)\n"
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

    if (lang=='powershell' or lang=='powershell-cmd'):
        pycmd = "$ip = \""+ec_opts['TARGETIP']['value']+"\"\n"
        pycmd += "$pr = \""+ec_opts['PORTS']['value']+"\" -split ','\n"
        pycmd += "foreach ($p in $pr) {\n"
        pycmd += " if ($p -match '^[0-9]+-[0-9]+$') {\n"
        pycmd += "  $prange = $p -split '-'\n"
        pycmd += "  $high = $prange[1]\n"
        pycmd += "  $low = $prange[0]\n"
        pycmd += " } elseif ($p -match '^[0-9]+$') {\n"
        pycmd += "  $high = $p\n"
        pycmd += "  $low = $p\n"
        pycmd += " }\n"
        pycmd += " for ($c = [convert]::ToInt32($low);$c -le [convert]::ToInt32($high);$c++) {\n"
        if (ec_opts['PROTOCOL']['value']=='TCP') or (ec_opts['PROTOCOL']['value']=='ALL'):
            if int(ec_opts['VERBOSITY']['value'])>0:
                pycmd += "  Write-Host -NoNewLine \"t\"\n"
            pycmd += "  try {\n"
            pycmd += "   $t = New-Object System.Net.Sockets.TCPClient\n"
            pycmd += "   $t.BeginConnect($ip, $c, $null, $null) | Out-Null\n"
            pycmd += "   $t.Close()\n"
            pycmd += "  }\n"
            pycmd += "  catch { }\n"
        if (ec_opts['PROTOCOL']['value']=='UDP') or (ec_opts['PROTOCOL']['value']=='ALL'):
            if int(ec_opts['VERBOSITY']['value'])>0:
                pycmd += "  Write-Host -NoNewLine \"u\"\n"
            pycmd += "  $d = [system.Text.Encoding]::UTF8.GetBytes(\".\")\n"
            pycmd += "  try {\n"
            pycmd += "   $t = New-Object System.Net.Sockets.UDPClient\n"
            pycmd += "   $t.Send($d, $d.Length, $ip, $c) | Out-Null\n"
            pycmd += "   $t.Close()\n"
            pycmd += "  }\n"
            pycmd += "  catch { }\n"
        if ec_opts['DELAY']['value']!='0':
            if int(ec_opts['VERBOSITY']['value'])>0:
                pycmd += "  Write-Host -NoNewLine \"W\"\n"
            pycmd += "  Start-Sleep -m ("+ec_opts['DELAY']['value']+"*1000)\n"
        pycmd += " }\n"
        pycmd += "}\n"

    elif lang=='tcpdump':
        # Sort out the TCP capture filter
        tcpdump_cmd = ['dst host '+ec_opts['TARGETIP']['value']]
        if (ec_opts['SOURCEIP']['value']!=''):
            tcpdump_cmd.append('src host '+ec_opts['SOURCEIP']['value'])

        # Now deal with protocol specifics
        tcpdump_proto = []
        if (ec_opts['PROTOCOL']['value']=='TCP') or (ec_opts['PROTOCOL']['value']=='ALL'):
            tcpdump_proto.append('((tcp[tcpflags]&(tcp-syn|tcp-ack))==tcp-syn && tcp)')
        if (ec_opts['PROTOCOL']['value']=='UDP') or (ec_opts['PROTOCOL']['value']=='ALL'):
            tcpdump_proto.append('(udp)')
        
        # Now generate the tcpdump capture command line. Yes I know I'm using mktemp()...
        tmpname = 'egress_'+datetime.datetime.now().strftime('%Y%b%d_%H%M%S').lower()+'_'
        tf = tempfile.mktemp('.pcap',tmpname)
        tcpdump_run = 'tcpdump -n -U -w '+tf+' \''+(' && '.join(tcpdump_cmd))+' && ('+'||'.join(tcpdump_proto)+')\''
        tshark_tcp_run = 'tshark -r '+tf+' -Tfields -eip.proto -eip.src -etcp.dstport tcp | sort -u #For received TCP'
        tshark_udp_run = 'tshark -r '+tf+' -Tfields -eip.proto -eip.src -eudp.dstport udp | sort -u #For received UDP'
        pycmd = [tcpdump_run,tshark_tcp_run,tshark_udp_run]

    return pycmd

def print_supported_languages():
    print "   python         "+"| Generates a python egress buster script."
    print "   python-cmd     "+"| Generates a python one-liner designed to be copied and pasted."
    print "   powershell     "+"| Generates a powershell egress buster script."
    print "   powershell-cmd "+"| Generates a powershell one-liner designed to be copied and pasted."
    print "   tcpdump        "+"| Generates the tcpdump capture command to be run on the target machine."

def write_file_data(prefix,suffix,data):
    date_time = datetime.datetime.now().strftime('%Y%b%d_%H%M%S').lower()
    handle,filename = tempfile.mkstemp(suffix,prefix+date_time+'_')
    os.write(handle,data)
    os.close(handle)
    print colourise("Also written to: \033[4;35m"+filename,'0;35')

def build_port_list(portstring):
    temp_list = []
    chunks = portstring.split(',')
    for i in chunks:
        try:
            single_val = int(i)
            if single_val>0 and single_val<65536: # May be a single number
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
                        temp_list.append(c)
                else:
                    return 0
            else:
                return 0
    return temp_list

class ec(cmd.Cmd):

    prompt = colourise('egresschecker>','0;36')+" "
    undoc_header = None

    def do_generate(self, param):
        "Generate client code to perform the egress check. Specify a target language.\nExample: generate python-cmd"
        if ec_opts['TARGETIP']['value'].strip()=='':
            print colourise('Error:','1;31')+" Must specify a target IP. Use 'set TARGETIP x.x.x.x'."
        elif param == '':
            print colourise('Error:','1;31')+" Must specify a language."
            print_supported_languages()
        else:
            cmdLang = param.split()[0].lower()
            if (cmdLang == 'python' or cmdLang=='python-cmd'):
                code = generate_oneliner(cmdLang)
                if (cmdLang=='python'):
                    print colourise('Run the code below on the client machine:','0;32')
                    print code
                    write_file_data('egress_','.py',code)
                elif (cmdLang=='python-cmd'):
                    print colourise('Run the command below on the client machine:','0;32')
                    cmdline = 'python -c \'import base64,sys,zlib;exec(zlib.decompress(base64.b64decode("'+base64.b64encode(zlib.compress(code))+'")))\''
                    print cmdline
                    write_file_data('egress_','.sh',cmdline)
            elif (cmdLang == 'powershell' or cmdLang=='powershell-cmd'):
                code = generate_oneliner(cmdLang)
                if (cmdLang=='powershell'):
                    print colourise('Run the code below on the client machine:','0;32')
                    print code
                    write_file_data('egress_','.ps1',code)
                elif (cmdLang=='powershell-cmd'):
                    print colourise('Run the command below on the client machine:','0;32')
                    # In powershell, data must be in unicode format (i.e. chr(0) in between each one)
                    unicode_code = ""
                    for c in code.strip():
                        unicode_code += c+"\x00"
                    cmdline = 'powershell.exe -nop -w hidden -e '+base64.b64encode(unicode_code)
                    print cmdline
                    write_file_data('egress_','.bat',cmdline)
            elif cmdLang == 'tcpdump':
                code = generate_oneliner(cmdLang)
                print colourise('Run the command below on the target machine (probably yours) to save connection attempts:','0;32')
                print code[0]
                print colourise('The commands below will parse the saved capture file and display the ports on which connections were received:','0;32')
                print code[1]
                print code[2]
                write_file_data('capture_','.sh',code[0]+"\n"+code[1]+"\n"+code[2])
            else:
                print colourise('Error:','1;31')+" Invalid language specified."
                print_supported_languages()

    def complete_generate(self, text, line, begidx, endidx):
        param = line.partition(' ')[2].lower()
        offset = len(param) - len(text)
        return [s[offset:] for s in ec_generators if s.startswith(param)]

    def complete_set(self, text, line, begidx, endidx):
        param = line.partition(' ')[2].upper()
        offset = len(param) - len(text)
        return [s[offset:] for s in ec_opts.keys() if s.startswith(param)]

    def complete_get(self, text, line, begidx, endidx):
        param = line.partition(' ')[2].upper()
        offset = len(param) - len(text)
        return [s[offset:] for s in ec_opts.keys() if s.startswith(param)]

    def do_set(self, param):
        "Changes one of the stored options. Use 'get' without any parameters to see all options.\nExample: set PORTS 22,23,25-30"
        if param != '' and len(param.split())==2:
            cmdVariable = param.split()[0].upper()
            if cmdVariable in ec_opts.keys():
                cmdParam = param.split()[1].upper()
                if re.match(ec_opts[cmdVariable]['validation'],cmdParam):
                    # Specific PORTS check
                    if cmdVariable=='PORTS':
                        finalports = build_port_list(cmdParam)
                        if finalports==0:
                            print colourise('Error:','1;31')+" Invalid "+cmdVariable+" specification"
                        else:
                            ec_opts[cmdVariable]['value'] = cmdParam
                            finalword = 'port'
                            finalcount = len(finalports)
                            if (finalcount>1):
                                finalword += 's'
                            print cmdVariable+' => '+cmdParam+" ("+str(finalcount)+" "+finalword+")"
                    else:
                        ec_opts[cmdVariable]['value'] = cmdParam
                        print cmdVariable+' => '+cmdParam
                else:
                    print colourise('Error:','1;31')+" Invalid "+cmdVariable+" setting provided"
            else:
                print colourise('Error:','1;31')+" "+cmdVariable+" is not recognised"
        else:
            print colourise('Error:','1;31')+" Variable name and value required. Use \'get\' to see all variables."
     
    def do_get(self, param):
        "Retrieves the value of the given option. When used without any parameters, this will show all options.\nExample: get PORTS"
        if param != '':
            cmdVariable = param.split()[0].upper()
            if cmdVariable in ec_opts.keys():
                print cmdVariable+' = '+ec_opts[cmdVariable]['value']
            else:
                print colourise('Error:','1;31')+" "+cmdVariable+" not found"
        else:  
            padding = "+"+'-'*14+"+"+'-'*29+"+"
            print padding
            print "| %-12s | %-27s |" % ('Option','Value')
            print padding
            for k,v in ec_opts.iteritems():
                print "| %-12s | %-27s |" % (k,v['value'])
            print padding

    def do_quit(self, param):
        "Exits the framework"
        print ""
        return True

    def do_exit(self, param):
        "Exits the framework"
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
