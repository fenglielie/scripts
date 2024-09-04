# Define the path to the configuration file
$configFilePath = "./scripts/backup_config.json"

# Read the configuration from the config.json file
$configData = Get-Content $configFilePath | ConvertFrom-Json

# Extract the configuration values
$webDavUrl = $configData.webDavUrl
$username = $configData.username
$password = $configData.password
$fileExtension = $configData.fileExtension
$localBackupDir = $configData.localBackupDir

######################################################################

# Create a secure password object
$securePassword = ConvertTo-SecureString $password -AsPlainText -Force

# Create a credentials object
$credentials = New-Object System.Management.Automation.PSCredential ($username, $securePassword)

# Function to upload a file to the WebDAV server using curl
function UploadFileToWebDav($filePath, $webDavUrl, [PSCredential] $credentials) {
    $fileName = [System.IO.Path]::GetFileName($filePath)
    $destinationUrl = $webDavUrl + $fileName

    # Construct the curl command string
    $curlCommand = "curl -u $($credentials.UserName):$($password) `"$destinationUrl`" -T `"$filePath`""

    # Execute the curl command and capture the output and exit code
    Invoke-Expression $curlCommand 2>&1

    # Check the exit code of the curl command
    $lastExitCode = $LASTEXITCODE

    if ($lastExitCode -eq 0) {
        return
    }
    else {
        Write-Host "Error: Failed to upload"
    }
}

# Function to copy a file to the local backup directory
function CopyFileToLocalBackup($filePath, $localBackupDir) {
    $fileName = [System.IO.Path]::GetFileName($filePath)
    $localFilePath = Join-Path $localBackupDir $fileName

    # Copy the file to the local backup directory
    Copy-Item $filePath -Destination $localFilePath
}

# Define a function to ask user if they want to backup to WebDAV
function AskUserForWebDavBackup() {
    # Ask user if they want to backup to WebDAV
    $response = Read-Host "Do you want to backup to WebDAV? (y/n)"
    if ($response.ToLower() -eq "y") {
        return $true
    }
    return $false
}

# Define a function to ask user if they want to backup to local directory
function AskUserForLocalBackup() {
    # Ask user if they want to backup to local directory
    $response = Read-Host "Do you want to backup to local directory? (y/n)"
    if ($response.ToLower() -eq "y") {
        return $true
    }
    return $false
}

# Recursively find all files with the specified extension in the current directory
$filesToBackup = Get-ChildItem -Path "." -Recurse -Filter "*$fileExtension"

$localBackup = AskUserForLocalBackup
if ($localBackup) {
    # Backup to local directory
    foreach ($file in $filesToBackup) {
        Write-Host "Uploading $file to local directory..."
        CopyFileToLocalBackup $file.FullName $localBackupDir
    }
}

$webDavBackup = AskUserForWebDavBackup
if ($webDavBackup) {
    # Backup to WebDAV
    foreach ($file in $filesToBackup) {
        Write-Host "Uploading $file to WebDAV..."
        UploadFileToWebDav $file.FullName $webDavUrl $credentials
    }
}

Write-Host "Backup completed."
