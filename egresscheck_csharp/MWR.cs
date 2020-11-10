using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using System.Net;
using System.Net.Sockets;

namespace egresscheck_csharp
{
    class MWR
    {
        static void Main(string[] args)
        {
            ec("127.0.0.1", "1000-1100");
        }

        static IAsyncResult tcp(string ip, int port)
        {
            try
            {
                IAsyncResult r;
                Socket s = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
                r = s.BeginConnect(ip, port, null, null);
                return r;
            } catch { return null; }
        }

        static void udp(string ip, int port)
        {
            try
            {
                UdpClient s = new UdpClient(ip, port);
                s.Send(new byte['.'], 1);
                s.Close();
            } catch { return; }
        }

        static void ec(string ip, string ports)
        {
            List<int> allports = new List<int>();
            List<IAsyncResult> sockets = new List<IAsyncResult>();
            string[] pr_split = ports.Split(',');
            foreach (string p in pr_split)
            {
                if (Regex.IsMatch(p, "^[0-9]+-[0-9]+$")) {
                    string[] prange = p.Split('-');
                    for (int c = Convert.ToInt32(prange[0]); c <= Convert.ToInt32(prange[1]); c++)
                        allports.Add(c);
                } else if (Regex.IsMatch(p, "^[0-9]+$"))
                {
                    allports.Add(Convert.ToInt32(p));
                } else
                {
                    throw new Exception("Invalid port specification");
                }
            }

            foreach (int i in allports)
            {
                udp(ip, i);
                IAsyncResult r = tcp(ip, i);
                if (r != null)
                    sockets.Add(r);
            }

            // Wait for the async operations to be complete
            foreach (IAsyncResult a in sockets)
                a.AsyncWaitHandle.WaitOne();


        }


        /*
$pr_split = $portrange -split ','
$ports = @()
foreach ($p in $pr_split) {
    if ($p -match '^[0-9]+-[0-9]+$') {
        $prange = $p -split '-'
        for ($c = [convert]::ToInt32($prange[0]);$c -le[convert]::ToInt32($prange[1]);$c++) {
            $ports += $c
}
}
elseif($p - match '^[0-9]+$') {
        $ports += $p
    } else
{
# Error in port definition
return
    }
}

foreach ($eachport in $ports) {
Write - Output "Sending TCP/$eachport to $ip"
            _tcp - ip $ip - port $eachport
    Write - Output "Sending UDP/$eachport to $ip"
            _udp - ip $ip - port $eachport
    Start - Sleep - m(0.2 * 1000)
}

}
        */

    }
            
}
