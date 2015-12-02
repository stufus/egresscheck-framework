

function egresscheck {
    [CmdletBinding()]                                                                                                                                                                           
    param([string]$ip, [int]$startPort = 1, [int]$endPort = 65535)

    for ($i = $startPort; $i -le $endPort; $i++)                                                                                                                                                
    {
		_tcp -ip "$ip" -port $i
		_udp -ip "$ip" -port $i
    }

    Write-Output "Finished"     
}

function _tcp {
    [CmdletBinding()]                                                                                                                                                                           
    param([string]$ip, [int]$port)

	try {                                                                                                                                                                                       
		$t = New-Object System.Net.Sockets.TCPClient                                                                                                                              
		$t.BeginConnect($ip, $port, $null, $null) | Out-Null
        $t.Close()
        
	}
	catch { }  
}

function _udp {
    [CmdletBinding()]                                                                                                                                                                           
    param([string]$ip, [int]$port)

	try {                                                                                                                                                                                       
		$t = New-Object System.Net.Sockets.UDPClient       
        $t.BeginSend(".", 1, $ip, $port, $null, $null) | Out-Null
        $t.Close()
        
	}
	catch { }  
}

egresscheck -ip "127.0.0.1" -startPort 1 -endPort 65535