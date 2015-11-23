#!/usr/local/bin/python
import pprint
import re
import cmd
import signal
import sys

# Global variable to store the various user-configurable options
ec_opts = { 'REMOTEIP': { 'value': '', 'validation':'^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$', 'required': 0, 'description':'This is the IP address of the target machine. It is used to filter out unwanted traffic.' },
            'TARGETIP': { 'value': '', 'validation':'^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$', 'required': 1, 'description':'This is the IP address that the client code will try to connect to.' },
            'PORTSTART': { 'value': '1', 'validation':'^[0-9]+$', 'required': 1, 'description':'This is the starting port for the egress attempt.' },
            'PORTFINISH': { 'value': '65535', 'validation':'^[0-9]+$', 'required': 1, 'description':'This is the finishing port for the egress attempt.' },
            'PROTOCOL': { 'value': 'TCP', 'validation':'^(TCP|UDP|all)$', 'required': 1, 'description':'Chooses the protocol to use. Can be one of \'TCP\', \'UDP\' or \'all\' (attempts both TCP and UDP).' }
                 }

class ec(cmd.Cmd):

    prompt = "egresschecker> "

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
