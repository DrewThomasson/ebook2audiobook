param(
    [string]$HostName = "127.0.0.1",
    [int]$Port = 7860,
    [int]$Timeout = 60
)
for ($i = 1; $i -le $Timeout; $i++) {
    try {
        $tcp = [System.Net.Sockets.TcpClient]::new()
        $tcp.Connect($HostName, $Port)
        $tcp.Close()
        Start-Process "http://${HostName}:$Port/"
        break
    }
    catch {
        Start-Sleep -Seconds 1
    }
}