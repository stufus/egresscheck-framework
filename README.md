# EgressChecker

EgressChecker is a mini-framework which can be used to help check for egress filtering between your host and a client system on which you have the ability to execute commands and scripts.

## Summary
Most penetration testers have, at one time or another, had the need to measure or circumvent data egress security controls; red team exercises, targeted attack simulations and some internal penetration tests are good examples. For the purposes of simplicity, assume that there is an opportunity to execute code on either a Windows or a UNIX machine; the next stage would be to effectively 'portscan' your machine's IP address from the compromised machine in order to find out which ports can be used to egress data. 

This is not a new problem; there are a large number of scripts and tools designed to meet this need and the majority do this very well. This tool aims to improve on the principles on which the other tools have been built, offering a few additional features in a slightly more user-friendly way. 

I wanted a tool that could offer something for both windows and UNIX systems, that would present the commands and tools to run as one-liners, could offer both TCP and UDP, that could take advantage of native tools on the client, that could format the results and does not require me to immediately kill all my existing listeners.  
 
## Components

This tool comprises two main components:
* Generating packets on all ports in a given range, which would be run on the compromised host (the client). For example, assume that the client's address is 10.0.0.1.
* Measuring which connections were made to your machine (the attacker). For example, assume that your IP address is 192.168.0.1.

## Mechanism

On the basis of the example above, this tool will allow you to connect to 192.168.0.1 on each port from 10.0.0.1, and let you see which connections were successful, which effectively will identify gaps or breaches in firewalls.

The basic approach is to:

* Generate a 'one-liner' that can be run on the client. Currently, EgressChecker can generate one-liners in python and ruby, but there is no reason why you could not use any other tool for this purpose.
* Use tcpdump to monitor connections to your machine. EgressChecker will print the command that you need to run to perform the necessary capturing and filtering. If used in TCP mode, it just looks for SYN packets. Tcpdump will be configured to save the filtered capture file.
* Parse the tcpdump file, from which the results can be displayed in a number of formats, useful for other tools or simply for reporting.

## FAQs
### Why tcpdump?

There are a number of different approaches that others have implemented and that I've tried. However, I have had mixed results from them. 

One tool used scapy sniff packets; despite being a very elegant approach, I found that it did not seem to capture all packets and it was difficult to understand why. 

Another tool worked by opening up listening sockets on a large number of ports on your machine, and monitoring connections to them. Nothing wrong with it, but you can't do too many at once, and I wanted a solution that would sniff the packets (meaning that you may not have to drop your software firewall, nor would you need to kill any existing listeners that you have).

A different tool worked by using iptables to redirect all traffic to a single port, and monitored that port. I couldn't use it because FreeBSD doesn't have iptables, so it did not work for me.

### Is it stealthy?

Not really. You can configure a delay between packets being generated if you want to. I've tried to keep the client code (one liners) as small as possible; they really are very simple scripts.
