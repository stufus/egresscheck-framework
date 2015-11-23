#!/usr/local/bin/python
import pprint

# Global variable to store the various user-configurable options
ec_opts =   { 'REMOTEIP': { 'value': '', 'validation':'/^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/', 'required': 0, 'description':'This is the IP address of the target machine. It is used to filter out unwanted traffic.' },
              'TARGETIP': { 'value': '', 'validation':'/^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/', 'required': 1, 'description':'This is the IP address that the client code will try to connect to.' },
              'PORTSTART': { 'value': '1', 'validation':'/^[0-9]+$/', 'required': 1, 'description':'This is the starting port for the egress attempt.' },
              'PORTFINISH': { 'value': '65535', 'validation':'/^[0-9]+$/', 'required': 1, 'description':'This is the finishing port for the egress attempt.' },
              'PROTOCOL': { 'value': 'TCP', 'validation':'/^(TCP|UDP|all)$/', 'required': 1, 'description':'Chooses the protocol to use. Can be one of \'TCP\', \'UDP\' or \'all\' (attempts both TCP and UDP).' }
            }

def process_user_input(uinput):
    strippedInput = uinput.strip()
    cmdVerb = strippedInput.split()[0].lower()

    if cmdVerb == 'set':
        cmdVariable = strippedInput.split()[1].upper()
        if cmdVariable in ec_opts.keys():
            cmdParam = strippedInput.split()[2]
            ec_opts[cmdVariable]['value'] = cmdParam
        else:
            print "Invalid option: " + cmdVariable

    elif cmdVerb == 'get':
        pprint.pprint(ec_opts)

    elif cmdVerb == 'import':
        cmdFile = strippedInput.split()[1]
        pass

    else:
        pass

cmd = raw_input('egresschecker> ')
process_user_input(cmd)
