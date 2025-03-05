# .ps1
# Script to run ebook2audiobook.cmd with administrator privileges

# Paste contents into https://ps2exe.azurewebsites.net to create exe


# Get the directory of the current script
$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Full path to the ebook2audiobook.cmd
$cmdPath = Join-Path $scriptDirectory "ebook2audiobook.cmd"

# Check if the command file exists
if (Test-Path $cmdPath) {
    # Create a process start info
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "cmd.exe"
    $psi.Arguments = "/c `"$cmdPath`""
    $psi.Verb = "runas"  # This triggers running as administrator
    $psi.WorkingDirectory = $scriptDirectory
    $psi.UseShellExecute = $true

    # Start the process
    try {
        [System.Diagnostics.Process]::Start($psi)
    }
    catch {
        Write-Host "Failed to run the command as administrator: $_"
        pause
    }
}
else {
    Write-Host "ebook2audiobook.cmd not found in the script directory."
    pause
}
