# Define the path to the configuration file
$configFilePath = "./scripts/create_config.json"

# Read the configuration from the config.json file
$configData = Get-Content $configFilePath | ConvertFrom-Json

# Prompt the user to choose the type of template
$templateType = Read-Host "Enter the template type (note/report)"

# Ensure the user provides a valid template type
if ($templateType -ne "note" -and $templateType -ne "report") {
    Write-Host "Invalid template type. Please enter either 'note' or 'report'."
    exit 1
}

# Extract the configuration values for the chosen template type
$templateConfig = $configData."$templateType"

# Extract values from the template configuration
$directoryPrefix = $templateConfig.directoryPrefix
$rootDirectory = $templateConfig.rootDirectory
$templateDirectory = $templateConfig.templateDirectory
$templateFiles = $templateConfig.templateFiles
$mainTemplate = $templateFiles.mainTemplate
$classFile = $templateFiles.classFile

# Get the current date and construct directory and file names
$currentDate = Get-Date -Format "MM-dd"
$directoryName = "$directoryPrefix$currentDate"
$fileName = "$directoryName.tex"

# Define the full directory path and destination file path
$directoryPath = Join-Path -Path $rootDirectory -ChildPath $directoryName
$destinationFile = Join-Path -Path $directoryPath -ChildPath $fileName

# Check if the directory already exists
if (Test-Path $directoryPath -PathType Container) {
    Write-Host "Error: The target directory '$directoryPath' already exists. Please check or remove the existing directory."
    exit 1
} else {
    # Create the new directory
    New-Item -Path $directoryPath -ItemType Directory -Force | Out-Null
}

# Define the full template directory path based on rootDirectory and templateDirectory
$fullTemplateDirectory = Join-Path -Path $rootDirectory -ChildPath $templateDirectory

# Define full paths for the main template and class file
$mainTemplateFilePath = Join-Path -Path $fullTemplateDirectory -ChildPath $mainTemplate
$classFileFilePath = Join-Path -Path $fullTemplateDirectory -ChildPath $classFile

# Copy necessary files for the chosen template
Copy-Item -Path $mainTemplateFilePath -Destination $destinationFile
Copy-Item -Path $classFileFilePath -Destination $directoryPath

# Output success messages
Write-Host "Directory created: $directoryPath"
Write-Host "File copied: $fileName"
