

function egresscheck {
    [CmdletBinding()]                                                                                                                                                                           
    param([string]$ip, [string]$pr) 

    $pr_split = $portrange -split ','
    $ports = @()
    foreach ($p in $pr_split) {
        if ($p -match '^[0-9]+-[0-9]+$') {
            $prange = $p -split '-'
            for ($c = [convert]::ToInt32($prange[0]);$c -le [convert]::ToInt32($prange[1]);$c++) {
                $ports += $c
            }
        } elseif ($p -match '^[0-9]+$') {
            $ports += $p
        } else {
            #Error in port definition
            return
        }
    }

    $ports

    foreach ($eachport in $ports) {
		Write-Output "_tcp -ip $ip -port $eachport"
		Write-Output "_udp -ip $ip -port $eachport"
    }

    #Write-Output "Finished"     
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

$ip = "127.0.0.1"
$portrange = "20-30,40,50"
egresscheck -ip $ip -pr $portrange