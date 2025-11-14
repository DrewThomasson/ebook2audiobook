param(
    [string]$HostName = "127.0.0.1",
    [int]$Port = 7860,
    [int]$Timeout = 90
)

for ($i = 1; $i -le $Timeout; $i++) {
    try {
        $tcp = [System.Net.Sockets.TcpClient]::new()
        $tcp.Connect($HostName, $Port)
        $tcp.Close()
        Start-Process "http://${HostName}:$Port/"
        exit 0
    }
    catch {
        Start-Sleep -Seconds 1
    }
}
exit 0