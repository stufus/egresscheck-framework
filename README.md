# EgressCheck Framework

This is a mini-framework which can be used to help check for egress filtering between your host and a client system on which you have the ability to execute commands and scripts.

## Summary
Most penetration testers have, at one time or another, had the need to measure or circumvent data egress security controls; red team exercises, targeted attack simulations and some internal penetration tests are good examples. For the purposes of simplicity, assume that there is an opportunity to execute code on either a Windows or a UNIX machine; the next stage would be to effectively 'portscan' your machine's IP address from the compromised machine in order to find out which ports can be used to egress data. 

This is not a new problem; there are a large number of scripts and tools designed to meet this need and the majority do this very well. This tool aims to improve on the principles on which the other tools have been built, offering a few additional features in a slightly more user-friendly way. 

I wanted a tool that could offer something for both windows and UNIX systems, that would present the commands and tools to run as one-liners, could offer both TCP and UDP, that could take advantage of native tools on the client, that could format the results and does not require me to immediately kill all my existing listeners.  
 
## Components

This tool comprises two main components:
* Generating packets on all ports in a given range, which would be run on the compromised host (the client). For example, assume that the client's address is 10.0.0.1.
* Measuring which connections were made to your machine (the attacker). For example, assume that your IP address is 192.168.0.1.

## Quick Start Example

* The compromised machine is 10.0.0.1 which runs Linux.
* Your machine is 192.168.0.1.
* You want to identify egress opportunities from 10.0.0.1 to 192.168.0.1 across all 65535 TCP and UDP ports.

On your machine:

```
stufus@me$ git clone https://github.com/stufus/egresscheck-framework.git
stufus@me$ ./ecf.py 

       .mMMMMMm.             MMm    M   WW   W   WW   RRRRR
      mMMMMMMMMMMM.           MM   MM    W   W   W    R   R
     /MMMM-    -MM.           MM   MM    W   W   W    R   R
    /MMM.    _  \/  ^         M M M M     W W W W     RRRR
    |M.    aRRr    /W|        M M M M     W W W W     R  R
    \/  .. ^^^   wWWW|        M  M  M      W   W      R   R
       /WW\.  .wWWWW/         M  M  M      W   W      R    R
       |WWWWWWWWWWW/
         .WWWWWW.        EgressChecker Mini-Framework v0.1-pre1
                     stuart.morgan@mwrinfosecurity.com | @ukstufus


egresschecker> set SOURCEIP 10.0.0.1
SOURCEIP => 10.0.0.1

egresschecker> set TARGETIP 192.168.0.1
TARGETIP => 192.168.0.1

egresschecker> set PORTS 1-65535
PORTS => 1-65535 (65535 ports)

egresschecker> set PROTOCOL all
PROTOCOL => ALL

egresschecker> get
+--------------+-----------------------------+
| Option       | Value                       |
+--------------+-----------------------------+
| PROTOCOL     | ALL                         |
| VERBOSITY    | 0                           |
| DELAY        | 0.1                         |
| THREADS      | 25                          |
| TARGETIP     | 192.168.0.1                 |
| SOURCEIP     | 10.0.0.1                    |
| PORTS        | 1-65535                     |
+--------------+-----------------------------+

egresschecker> generate tcpdump

Run the command below on the target machine (probably yours) to save connection attempts:                                                                                                                      
tcpdump -n -U -w /tmp/egress_2015nov26_130154_650H57.pcap 'dst host 192.168.0.1 && src host 10.0.0.1 && (((tcp[tcpflags]&(tcp-syn|tcp-ack))==tcp-syn && tcp)||(udp))'                                          

The commands below will parse the saved capture file and display the ports on which connections were received:                                                                                                 
tshark -r /tmp/egress_2015nov26_130154_650H57.pcap -Tfields -eip.proto -eip.src -etcp.dstport tcp | sort -u #For received TCP                                                                                  
tshark -r /tmp/egress_2015nov26_130154_650H57.pcap -Tfields -eip.proto -eip.src -eudp.dstport udp | sort -u #For received UDP                                                                                  

Also written to: /tmp/capture_2015nov26_130154_OiH0mn.sh

egresschecker> generate python-cmd

Run the command below on the client machine:
python -c 'import base64,sys,zlib;exec(zlib.decompress(base64.b64decode("eJx9U8FO4zAQvfsrLC51RIjSrop2VwxSgXZ3VQoLLXCoKpSmLjUkjhW7ouXr12M7EIS0l2TmZd57M2NHlKqqDdVV/sINESHbazIG+0z4ThgygoJLcgF1Jp84OQchDdmCpySBedbkg9Hjn6vhjKwaYHp9Pn6czm6HgwnRn8CLX7cWC55GlJy8Ab4SXXCuyD2kSff986bm2UrIJzKD9zjJt3XNpZk5gFy2vgTooQVxuS15nRlOXqDXJ89w0P3RS7rH3xPrc0CUzY+O+/1v/QOy4mv6mwkVL/9GPwk19d4+qYQtO4tXEYaJ5mZZ2GGsMks9lFdS8tywQAxgUWnObMx3OVcGdVSmtbMYfrF4dRYaqa9fLRCSK1OxTtKJWy6v/3VZYiUuUaPRuqqpokJSh2ChG1ShzvA9emP3kSPfMJUhbQ/X7CW2sVcQqOA6vmQmq5+4gWVs3xrYcyyiKNEWNdjQFcxYIBkkPTCUo2KNqaayMvQKAWqS50pI5m2v2SZujOcLQu9gxJy5WLO7k42T2MBdq5kL5tF9killt8TmC1s+gLRVozJXMR8smiIR+V4GAGxz1HUKnkR5oblPD6FLaM3NtrYzu/YKpqZYu3PN1aCmiVaFMKwTd9obqlEgHC0t4dz7oWF5mtJMrmh5glfu2BXQXdNWiWUfR0k5iMbgqNNIjBiPAHqe2phQOrE2fJ4uIp/mLu2GtKVJm5FSl1nBSegp9z25eHICeSjHqXK/6kmcH4ZltdvOg0mzuc8WH/AHGqKd2+qtuxoZ2O26k7YhpMgYsx5e7cINnUWnDrxheB/G+GdYInHBP/7yVuw=")))'

Also written to: /tmp/egress_2015nov26_130157_EXxfhI.sh

egresschecker>
```

On your system, run the tcpdump command provided by the 'generate tcpdump' directive:

```
stufus@me$ tcpdump -n -U -w /tmp/egress_2015nov26_130154_650H57.pcap 'dst host 192.168.0.1 && src host 10.0.0.1 && (((tcp[tcpflags]&(tcp-syn|tcp-ack))==tcp-syn && tcp)||(udp))'
tcpdump: listening on em0, link-type EN10MB (Ethernet), capture size 65535 bytes
```

On the compromised system, run the python one-liner:

```
user@client$ python -c 'import base64,sys,zlib;exec(zlib.decompress(base64.b64decode("eJx9U8FO4zAQvfsrLC51RIjSrop2VwxSgXZ3VQoLLXCoKpSmLjUkjhW7ouXr12M7EIS0l2TmZd57M2NHlKqqDdVV/sINESHbazIG+0z4ThgygoJLcgF1Jp84OQchDdmCpySBedbkg9Hjn6vhjKwaYHp9Pn6czm6HgwnRn8CLX7cWC55GlJy8Ab4SXXCuyD2kSff986bm2UrIJzKD9zjJt3XNpZk5gFy2vgTooQVxuS15nRlOXqDXJ89w0P3RS7rH3xPrc0CUzY+O+/1v/QOy4mv6mwkVL/9GPwk19d4+qYQtO4tXEYaJ5mZZ2GGsMks9lFdS8tywQAxgUWnObMx3OVcGdVSmtbMYfrF4dRYaqa9fLRCSK1OxTtKJWy6v/3VZYiUuUaPRuqqpokJSh2ChG1ShzvA9emP3kSPfMJUhbQ/X7CW2sVcQqOA6vmQmq5+4gWVs3xrYcyyiKNEWNdjQFcxYIBkkPTCUo2KNqaayMvQKAWqS50pI5m2v2SZujOcLQu9gxJy5WLO7k42T2MBdq5kL5tF9killt8TmC1s+gLRVozJXMR8smiIR+V4GAGxz1HUKnkR5oblPD6FLaM3NtrYzu/YKpqZYu3PN1aCmiVaFMKwTd9obqlEgHC0t4dz7oWF5mtJMrmh5glfu2BXQXdNWiWUfR0k5iMbgqNNIjBiPAHqe2phQOrE2fJ4uIp/mLu2GtKVJm5FSl1nBSegp9z25eHICeSjHqXK/6kmcH4ZltdvOg0mzuc8WH/AHGqKd2+qtuxoZ2O26k7YhpMgYsx5e7cINnUWnDrxheB/G+GdYInHBP/7yVuw=")))'
```

Once the script has finished, go back to your machine and close tcpdump. You can then parse the pcap file to extract the TCP and UDP connections that were received. This was tested on a test network that permitted egress on TCP ports 21,80,443,8080 and UDP ports 161,53447 and blocked all others:

```
^C190 packets captured
16450 packets received by filter
0 packets dropped by kernel
stufus@me$ tshark -r /tmp/egress_2015nov26_130154_650H57.pcap -Tfields -eip.proto -eip.src -etcp.dstport tcp
6       10.0.0.1     21
6       10.0.0.1     80
6       10.0.0.1     443
6       10.0.0.1     8080
stufus@me$ tshark -r /tmp/egress_2015nov26_130154_650H57.pcap -Tfields -eip.proto -eip.src -eudp.dstport udp
17      10.0.0.1     161
17      10.0.0.1     53447
```

This can then be formatted using basic UNIX tools either for injection into other tools or for reporting. For example:

```
stufus@me$ tshark -r /tmp/egress_2015nov26_130154_650H57.pcap -Tfields -eip.proto -eip.src -etcp.dstport tcp > /tmp/egress.tcp
stufus@me$ cat /tmp/egress.tcp | awk '{ print $3 }' | xargs echo | sed 's/ /,/g'
21,80,443,8080
stufus@me$ cat /tmp/egress.tcp | awk '{ print $2,":",$3 }' | sed 's/ //g'
10.0.0.1:21
10.0.0.1:80
10.0.0.1:443
10.0.0.1:8080
```

## Mechanism

On the basis of the example above, this tool will allow you to connect to 192.168.0.1 on each port from 10.0.0.1, and let you see which connections were successful, which effectively will identify gaps or breaches in firewalls.

The basic approach is to:

* Generate a 'one-liner' that can be run on the client. Currently, ECF can only generate one-liners in python, but I'll add other scripts in the fullness of time.
* Use tcpdump to monitor connections to your machine. ECF will print the command that you need to run to perform the necessary capturing and filtering. If used in TCP mode, it just looks for SYN packets. Tcpdump will be configured to save the filtered capture file.
* Parse the tcpdump file, from which the results can be displayed in a number of formats, useful for other tools or simply for reporting. Currently, *tshark* is used as a pcap parser; ECF provides the parameters to pass to tshark.

### Client script

Regardless of the scripting language used, code that is generated by this framework will generate packets according to the following routine:

* The metadata (target IP address, port range, number of threads etc to use) will be 'hardcoded' into the script. The script is semi-dynamically generated based on the parameters provided.
* If THREADS is set to 1, this effectively means that threading will be disabled and the code that manages threads will not be included. 
* If THREADS is greater than 1, the script will import a threading library if necessary, divide up the ports to be scanned between the threads and launch all of them.
 * For example, if all ports between 10 and 20 were included and 4 threads were configured, the script would assign the 4 threads to scan the following ports:
   * Thread 1: 10, 14, 18
    * Thread 2: 11, 15, 19
    * Thread 3: 12, 16, 20
    * Thread 4: 13, 17
 * Each thread will loop through the requested ports and, depending on the configuration, will attempt to connect() (for TCP) and sendto() (for UDP). If both protocols are requested, the script will attempt the TCP connection first, followed by the UDP scan. 
   * In the example above, Thread 1 will connect to TCP/10, UDP/10, TCP/14, UDP/14, TCP/18, UDP/18 and then exit.
  * The main script will exit once all threads have completed and will block until then. However, sockets are created in non-blocking mode, meaning that it runs very quickly.

## Usage

EgressCheck is interactive; you will be presented with a prompt at which you can type commands. Each command is listed below, along with notes about it for additional information.

### get
> Syntax: get [option]

This command will list the various options that can be set. Typing 'get' on its own will list all values. 

```
egresschecker> get                                                                                                                    

+--------------+-----------------------------+                                                                  
| Option       | Value                       |
+--------------+-----------------------------+
| PROTOCOL     | ALL                         |
| VERBOSITY    | 0                           |
| DELAY        | 0.1                         |
| THREADS      | 25                          |
| TARGETIP     | 192.168.0.1                 |
| SOURCEIP     | 10.0.0.1                    |
| PORTS        | 1-65535                     |
+--------------+-----------------------------+
```

Typing an option name will display the value of that option only.

```
egresschecker> get PORTS   
PORTS = 1-65535
```

The options are summarised below.

Option  | Description
------------- | -------------
PROTOCOL  | Determins the IP protocol to use; this can be one of 'TCP','UDP' or 'ALL'. This affects the way that the connect-back scripts are generated and is also used to construct the tcpdump filter. Selecting 'TCP' will have the effect of making the script connect to each port in the 'PORTS' list over TCP. Selecting UDP will send a UDP packet to each port instead. Selecting 'ALL' will attempt a TCP and UDP connection to each port.
VERBOSITY | This can be '0' or '1' and affects the output of the connect-back scripts. If '0' is set, the scripts will be as silent as they can be. If '1' is set, the script will output status information to stdout. This is in the form of letter codes; it will write a 't' to stdout if it is sending a TCP packet, 'u' if it is sending a UDP packet or 'W' if it is waiting (see the DELAY option).
DELAY | The number of seconds to pause after sending the required packets to each port. If this is set to '0', the code which introduces the artificial delay will be omitted completely. Note that this is per-thread; if there are 10 threads, the per-thread routine is 'send TCP,send UDP,wait'.
THREADS | The number of simultaneous threads to generate when performing the egress test. If this is set to '1', the multi-threading libraries and code will not be imported or used. If it set to more than 1, the required number of threads will be generated and the connections will be divided up between the ports.
TARGETIP | This is the IP address that the connections should be targeted to. It is a required field and must be an IPv4 IP address. It will be hardcoded into the dynamically generated connect-back scripts and is also used to generate the tcpdump filter.
SOURCEIP | This is optional and is only used to make the tcpdump filter more specific. It should be set to the IPv4 IP address that the connections will appear to come from (if known).
PORTS | The port numbers to try. This accepts a mix of individual IPs and ranges, separated by commas (in a similar style to basic nmap). For example: 22,23,24,25,30,80,81,82 and 22-25,30,80-82 would both be acceptable forms of notation.

Where it makes sense, the parameters are tab-completable. 

### set

> Syntax: set [option] [value]

The 'set' command is used to change one of the options above. When setting an option, ECF will display the option name, a '=>' symbol and then the option value below it, for confirmation.

Examples:

```
egresschecker> set PORTS 22,23,25-30,80
PORTS => 22,23,25-30,80 (9 ports)

egresschecker> set TARGETIP 192.168.0.1
TARGETIP => 192.168.0.1

egresschecker> set SOURCEIP 10.0.0.1
SOURCEIP => 10.0.0.1

egresschecker> set PORTS 1-65535
PORTS => 1-65535 (65535 ports)

egresschecker> set PROTOCOL all
PROTOCOL => ALL
```

If you attempt to set an invalid option, you will see an error message. For example:

```
egresschecker> set TARGET 10.81.60.152

Error: TARGET is not recognised

egresschecker> 
```

Where it makes sense, the parameters are tab-completable. 

### generate

> Syntax: generate [format]

The generate command is used to produce the connect-back scripts to run on the compromised hosts, and to produce example tcpdump and tshark commands in order to capture and filter the connections on your machine.

The available formats are tab-completable and currently comprise:

Option  | Description
------------- | -------------
python | A raw python script which, when executed, will perform the egress test.
python-cmd | A python one-liner which can be executed from the command line which has the same effect as above.
tcpdump | The commands needed to record the connection attempts on your machine, and two example tshark commands to filter the packet captures in order to identify TCP and UDP incoming connections.

Whenever the generate command is run, the relevant output will also be written to a temporary file to make it easier to transfer, execute or audit the scripts. For example, running 'generate python-cmd' will generate the one-liner and include a statement to the effect of:

```
Also written to: /tmp/egress_2015nov26_154558_6aWX1P.sh
```

The format of this name is:
> [type-of-file]_[year][month][day]_[hh][mm][ss]_[random].[extension]

I have deliberately specified the month as a short name instead of a number to avoid the confusion over whether the date is in US format or UK format.

The temporary files are not cleaned up after ECF exits; this is deliberate because it gives you the opportunity to hash or audit the files if needed as evidence during a simulated attack or other penetration test.

## Speed

The egress code will use non-blocking sockets and, when configured without delays and multiple threads, covered the full range of ports (1-65535) in both TCP and UDP in just over 11 seconds.

```
egresschecker> set TARGETIP 192.168.0.1
TARGETIP => 192.168.0.1

egresschecker> set DELAY 0
DELAY => 0

egresschecker> set PORTS 1-65535
PORTS => 1-65535 (65535 ports)

egresschecker> set PROTOCOL all
PROTOCOL => ALL

egresschecker> get
+--------------+-----------------------------+
| Option       | Value                       |
+--------------+-----------------------------+
| PROTOCOL     | ALL                         |
| VERBOSITY    | 0                           |
| DELAY        | 0                           |
| THREADS      | 25                          |
| TARGETIP     | 192.168.0.1                 |
| SOURCEIP     |                             |
| PORTS        | 1-65535                     |
+--------------+-----------------------------+

egresschecker> generate python-cmd

Run the command below on the client machine:
python -c 'import base64,sys,zlib;exec(zlib.decompress(base64.b64decode("eJx9U9Fu....
```

When this code was run on the target machine, the execution completed in 11.255 seconds. The packet capture on the source machine was analysed which showed the connections being received.

```
user@clientlinux:~$ time python -c 'import base64,sys,zlib;exec(zlib.decompress(base64.b64decode("eJx9U9Fu....

real    0m11.255s
user    0m10.539s
sys     0m10.521s
```

An artificial delay of 100ms was configured and a new python one-liner was generated and tested. I have left this as a default simply to be a bit kinder to the target machine. However, I have tested this (without a delay) on a number of different systems and networks and have not noticed any problems.

```
egresschecker> get
+--------------+-----------------------------+
| Option       | Value                       |
+--------------+-----------------------------+
| PROTOCOL     | ALL                         |
| VERBOSITY    | 0                           |
| DELAY        | 0.1                         |
| THREADS      | 25                          |
| TARGETIP     | 192.168.0.1                 |
| SOURCEIP     |                             |
| PORTS        | 1-65535                     |
+--------------+-----------------------------+

egresschecker> generate python-cmd

Run the command below on the client machine:
python -c 'import base64,sys,zlib;exec(zlib.decompress(base64.b64decode("eJx9U8F...
```

With this delay, the script completed in just under 4 and a half minutes. 

```
user@clientlinux:~$ time python -c 'import base64,sys,zlib;exec(zlib.decompress(base64.b64decode("eJx9U8F...

real    4m23.189s
user    0m7.228s
sys     0m5.254s
```

## FAQs
### Why tcpdump?

There are a number of different approaches that others have implemented and that I've tried. However, I have had mixed results from them. 

One tool used scapy to sniff packets; despite being a very elegant approach, I found that it did not seem to capture all packets. 

Another tool worked by opening up listening sockets on a large number of ports on your machine, and monitoring connections to them. Nothing wrong with it, but you can't do too many at once, and I wanted a solution that would sniff the packets (meaning that you may not have to drop your software firewall, nor would you need to kill any existing listeners that you have).

A different tool worked by using iptables to redirect all traffic to a single port, and monitored that port. I couldn't use it because FreeBSD doesn't have iptables, so it did not work for me.

Using tcpdump has a few other benefits too; for example, it does not require listeners to be set up. In addition, this technique could easily be used on machines several layers deep on a target network. If access to a machine has been compromised through a pivot with sufficient privileges to dump traffic, internal egress could be assessed too.

### Is it stealthy?

Not really. You can configure a delay between packets being generated if you want to. I've tried to keep the client code (one liners) as small as possible; they really are very simple scripts.

### Is it accurate?

It is as accurate as it reasonably can be; remember that your host is simply capturing incoming SYN packets (for TCP) and incoming UDP packets and, if they match the source and destination IPs, displaying them. It can't tell for sure whether the packets were generated by the helper script or not but, if the packets arrive at your host, perhaps it is not important how they were generated. This will be inaccurate if there are intercepting proxies or traffic manging such as NAT in place; there may be egress channels which will not be immediately obvious from the results of this script.

### Is it compatible with other scripts?

Yes in that it is, at heart, very basic. There are two parts; a client (which generates traffic) and the listener (on which you can run tcpdump). If you run the tcpdump code on your own host and run something else which generates traffic to you, tcpdump will faithfully record the traffic which is received regardless of the tool used to generate it.

### Who is the intended audience?

Penetration testers looking to identify egress channels during engagements, and system administrators who wish to audit their systems to test the basic effectiveness of their firewall configuration.
