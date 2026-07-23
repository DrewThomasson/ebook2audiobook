param(
    [switch]$Kill,
    [string]$FileName = "c10.dll"
)

$workspace = Get-Location
Write-Host "Workspace: $workspace"
Write-Host "Suchen nach '$FileName' (dies kann einige Sekunden dauern)..."

$paths = @()
# Suche im Projekt-venv und workspace
$paths += Get-ChildItem -Path . -Filter $FileName -Recurse -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName -ErrorAction SilentlyContinue
# Gängige Python-Installationspfade
$common = @(
    "$Env:LOCALAPPDATA\Programs\Python",
    "C:\\Program Files\\Python*",
    "C:\\Program Files (x86)\\Python*",
    "$Env:ProgramFiles\\Python*",
    "$Env:USERPROFILE\\AppData\\Local\\Programs\\Python"
)
foreach ($c in $common) {
    try {
        $found = Get-ChildItem -Path $c -Filter $FileName -Recurse -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName -ErrorAction SilentlyContinue
        if ($found) { $paths += $found }
    } catch { }
}

$paths = $paths | Sort-Object -Unique
if (-not $paths) {
    Write-Host "Keine Vorkommen von $FileName gefunden." -ForegroundColor Yellow
    Write-Host "Alternativ: führe Resource Monitor / Process Explorer aus oder gib mir Bescheid, ich helfe weiter."
    exit 0
}

Write-Host "Gefundene Dateien:"
$paths | ForEach-Object { Write-Host " - $_" }

# Prüfe auf handle.exe (kompatibel mit PowerShell 5.x)
$handleCmd = Get-Command handle.exe -ErrorAction SilentlyContinue
$handle = $null
if ($handleCmd) { $handle = $handleCmd.Source }
if (-not $handle) {
    Write-Host "\nSytemtool 'handle.exe' nicht gefunden." -ForegroundColor Yellow
    Write-Host "Lade 'handle.exe' von Microsoft Sysinternals herunter und entpacke es in einen Ordner, z.B. C:\tools\handle.exe" -ForegroundColor Gray
    Write-Host "Download: https://learn.microsoft.com/sysinternals/downloads/handle"
    Write-Host "Anschließend führe dieses Skript nochmals aus oder rufe: `handle.exe c10.dll` als Administrator auf." -ForegroundColor Gray
    exit 0
}

$allPids = @()
foreach ($p in $paths) {
    Write-Host "\nPrüfe Sperren für: $p"
    try {
        $out = & $handle -nobanner -a "$p" 2>&1
        if ($LASTEXITCODE -ne 0 -and -not $out) {
            Write-Host "handle.exe meldete keinen Eintrag oder fehlte die Berechtigung (Starte als Administrator)." -ForegroundColor Yellow
            continue
        }
        $out | ForEach-Object { Write-Host $_ }
        # extrahiere PIDs
        foreach ($line in $out) {
            if ($line -match "pid:\s*(\d+)") {
                $pid = [int]$matches[1]
                $allPids += $pid
            }
        }
    } catch {
        Write-Host "Fehler beim Aufruf von handle.exe: $_" -ForegroundColor Red
    }
}

$allPids = $allPids | Sort-Object -Unique
if (-not $allPids) {
    Write-Host "Keine sperrenden Prozesse gefunden (oder handle.exe konnte sie nicht auflösen)." -ForegroundColor Yellow
    Write-Host "Verwende Process Explorer (ProcExp) oder Resource Monitor, suche nach Handles für '$FileName'."
    exit 0
}

Write-Host "\nGefundene sperrende PIDs: " -NoNewline
Write-Host ($allPids -join ', ') -ForegroundColor Cyan

if ($Kill) {
    foreach ($pid in $allPids) {
        try {
            Write-Host "Beende Prozess PID=$pid ..."
            Stop-Process -Id $pid -Force -ErrorAction Stop
            Write-Host "PID $pid beendet." -ForegroundColor Green
        } catch {
            Write-Host "Konnte PID $pid nicht beenden: $_" -ForegroundColor Red
        }
    }
    Write-Host "Warte 2 Sekunden, dann versuche Neuinstallation oder Entfernen des Ordners." -ForegroundColor Gray
} else {
    Write-Host "Wenn du die Prozesse beenden möchtest, starte das Skript mit dem Parameter -Kill als Administrator." -ForegroundColor Yellow
}

Write-Host "Fertig."