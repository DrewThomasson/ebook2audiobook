# Function to check if the script is running as Administrator
function Test-IsAdmin {
	$currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
	return $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# If the script is not running as Administrator, restart it with elevated privileges
if (-not (Test-IsAdmin)) {
	Write-Host "This script requires administrative privileges. Restarting as Administrator..." -ForegroundColor Yellow
	Start-Process powershell.exe -ArgumentList "-NoProfile", "-ExecutionPolicy RemoteSigned", "-File", "`"$PSCommandPath`" $Params" -Verb RunAs
	exit
}

################# Main script starts here with admin privileges #################

# Function to check if Conda is installed
function Check-CondaInstalled {
	Write-Host "Checking if Conda is installed..."
	$condaPath = (Get-Command conda -ErrorAction SilentlyContinue).Source
	if ($condaPath) {
		Write-Host "Conda is already installed at: $condaPath"
		return $true
	} else {
		Write-Host "Conda is not installed."
		return $false
	}
}

function Check-ProgramsInstalled {
	param (
		[string[]]$Programs
	)

	$programsMissing = @()

	if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
		Write-Host "Chocolatey is not installed. Installing Chocolatey..."
		Set-ExecutionPolicy Bypass -Scope Process -Force
		[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
		iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

		if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
			return $true
		} else {
			Write-Host "Chocolatey installed successfully."
		}
	}

	foreach ($program in $Programs) {
		if (Get-Command $program -ErrorAction SilentlyContinue) {
			Write-Host "$program is installed."
		} else {
			$programsMissing += $program
		}
	}

	$missingCount = $programsMissing.Count

	if ($missingCount -eq 0) {
		return $true
	} else {
		$installedCount = 0
		foreach ($program in $programsMissing) {
			if ($program -eq "ffmpeg") {
				Write-Host "Installing ffmpeg..."
				choco install ffmpeg -y

				if (Get-Command ffmpeg -ErrorAction SilentlyContinue) {
					Write-Host "ffmpeg installed successfully!"
					$installedCount += 1
				}
			} elseif ($program -eq "calibre") {
				# Avoid conflict with calibre built-in lxml
				pip uninstall lxml -y

				# Install Calibre using Chocolatey
				Write-Host "Installing Calibre..."
				choco install calibre -y

				# Verify Calibre installation
				if (Get-Command calibre -ErrorAction SilentlyContinue) {
						Write-Host "Calibre installed successfully!"
					$installedCount += 1
				}
			}
		}
	}
	if ($installedCount -eq $countMissing) {
		return $false
	}
	return $true
}

# Function to check if Docker is installed and running
function Check-Docker {
	Write-Host "Checking if Docker is installed..."
	$dockerPath = (Get-Command docker -ErrorAction SilentlyContinue).Source
	if ($dockerPath) {
		Write-Host "Docker is installed at: $dockerPath"
		# Check if Docker service is running
		$dockerStatus = (Get-Service -Name com.docker.service -ErrorAction SilentlyContinue).Status
		if ($dockerStatus -eq 'Running') {
			Write-Host "Docker service is running."
			return $true
		} else {
			Write-Host "Docker service is installed but not running. Attempting to start Docker service..."
			Start-Service -Name "com.docker.service" -ErrorAction SilentlyContinue

			# Wait for Docker service to start
			while ((Get-Service -Name "com.docker.service").Status -ne 'Running') {
				Write-Host "Waiting for Docker service to start..."
				Start-Sleep -Seconds 5
			}
			Write-Host "Docker service is now running."
			return $true
		}
	} else {
		Write-Host "Docker is not installed."
		return $false
	}
}

######### Miniconda installation

$minicondaUrl = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
$installerPath = "$env:TEMP\Miniconda3-latest-Windows-x86_64.exe"

if (-not (Check-CondaInstalled)) {
	# Check if the Miniconda installer already exists
	if (-not (Test-Path $installerPath)) {
		Write-Host "Downloading Miniconda installer..."
		Invoke-WebRequest -Uri $minicondaUrl -OutFile $installerPath
	} else {
		Write-Host "Miniconda installer already exists at $installerPath. Skipping download."
	}

	# Set the installation path for Miniconda
	$installPath = "C:\Miniconda3"

	Write-Host "Installing Miniconda..."
	Start-Process -FilePath $installerPath -ArgumentList "/InstallationType=JustMe", "/RegisterPython=0", "/AddToPath=1", "/S", "/D=$installPath" -NoNewWindow -Wait

	Write-Host "Verifying Miniconda installation..."
	& "$installPath\Scripts\conda.exe" --version
	Write-Host "Miniconda installation complete."
} else {
	Write-Host "Skipping Miniconda installation."
}

######### Docker installation

$dockerMsiUrl = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
$dockerInstallerPath = "$env:TEMP\DockerInstaller.exe"

$dockerUtilsNeeded = Check-ProgramsInstalled -Programs @("ffmpeg", "calibre")

if ($dockerUtilsNeeded) {
	if (-not (Check-Docker)) {
		# Verify the installer file or re-download if corrupted or missing
		if (-not (Test-Path $dockerInstallerPath)) {
			Write-Host "Downloading Docker installer for Windows..."
			Invoke-WebRequest -Uri $dockerMsiUrl -OutFile $dockerInstallerPath
		}

		# Launch the Docker installer
		Write-Host "Launching Docker installer..."
		Start-Process -FilePath $dockerInstallerPath
		Write-Host "Please complete the Docker installation manually."
		pause

		# Ensure Docker service is running after installation
		Write-Host "Ensuring Docker service is running..."
		Start-Service -Name "com.docker.service" -ErrorAction SilentlyContinue

		# Wait for Docker service to start
		while ((Get-Service -Name "com.docker.service").Status -ne 'Running') {
			Write-Host "Waiting for Docker service to start..."
			Start-Sleep -Seconds 5
		}

		Write-Host "Docker service is now running."
	}
}

######### Install ebook2audiobook

if (Check-CondaInstalled) {

	Write-Host "Installing ebook2audiobook..." -ForegroundColor Yellow

	# Set the working directory to the script's directory
	$scriptDir = $PSScriptRoot
	Set-Location -Path $scriptDir

	# Create new Conda environment with Python 3.11 in the script directory, showing progress
	Write-Host "Creating Conda environment with Python 3.11 in $scriptDir..."
	& conda create --prefix "$scriptDir\python_env" python=3.11 -y -v

	# Ensure the correct Python environment is active
	Write-Host "Checking Python version in Conda environment..."

	# Get python.exe version from python_env
	$pythonEnvVersion = & "$scriptDir\python_env\python.exe" --version

	# Get the Conda-managed Python version using conda run
	$pythonVersion = & conda run --prefix "$scriptDir\python_env" python --version
	
	if ($pythonVersion.Trim() -eq $pythonEnvVersion.Trim()) {
		Write-Host "Python versions match, proceeding with installation..."

		if ($dockerUtilsNeeded) {
			# Build Docker image for utils
			Write-Host "Building Docker image for utils..."
			& conda run --prefix "$scriptDir\python_env" docker build -f DockerfileUtils -t utils .
		}

		# Install required Python packages with pip, showing progress
		Write-Host "Installing required Python packages..."
		& conda run --prefix "$scriptDir\python_env" python.exe -m pip install --upgrade pip --progress-bar on -v
		& conda run --prefix "$scriptDir\python_env" pip install pydub nltk beautifulsoup4 ebooklib translate coqui-tts tqdm mecab mecab-python3 unidic gradio>=4.44.0 docker --progress-bar on -v

		# Download unidic language model for MeCab with progress
		Write-Host "Downloading unidic language model for MeCab..."
		& conda run --prefix "$scriptDir\python_env" python.exe -m unidic download

		# Download spacy NLP model with progress
		Write-Host "Downloading spaCy language model..."
		& conda run --prefix "$scriptDir\python_env" python.exe -m spacy download en_core_web_sm

		# Install ebook2audiobook
		Write-Host "Installing ebook2audiobook..."
		& conda run --prefix "$scriptDir\python_env" pip install -e .

		# Delete Docker and Miniconda installers if both are installed and running
		if ((Check-CondaInstalled) -and (Check-Docker)) {
			Write-Host "Both Conda and Docker are installed and running. Deleting installer files..."
			Remove-Item -Path $installerPath -Force -ErrorAction SilentlyContinue
			Remove-Item -Path $dockerInstallerPath -Force -ErrorAction SilentlyContinue
			Write-Host "Installer files deleted."
		}

		Write-Host "******************* ebook2audiobook installation successful! *******************" -ForegroundColor Green
		Write-Host "To launch ebook2audiobook:" -ForegroundColor Yellow
		Write-Host "- in command line mode: ./ebook2audiobook.cmd --headless [other options]"
		Write-Host "- in graphic web mode: ./ebook2audiobook.cmd [--share]"
	} else {
		Write-Host "The python terminal is still using the OS python version $pythonVersion, but it should be $pythonEnvVersion from the python_env virtual environment"
	}
	
	# Deactivate Conda environment
	Write-Host "Deactivating Conda environment..."
	& conda deactivate
} else {
	Write-Host "Installation cannot proceed. Either Conda is not installed or Docker is not running." -ForegroundColor Red
}
