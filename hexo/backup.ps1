# backup.ps1

# 切换工作目录到脚本所在目录的上一级目录
Set-Location -Path (Join-Path -Path $PSScriptRoot -ChildPath "..")

$InfoColor = "Green"
$ErrorColor = "Red"

git pull

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Git pull failed. Aborting script." -ForegroundColor $ErrorColor
    exit 1
}

git add source/

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Git add failed. Aborting script." -ForegroundColor $ErrorColor
    exit 1
}

git commit -m "Auto backup of blog from pwsh script."

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Git commit failed. Aborting script." -ForegroundColor $ErrorColor
    exit 1
}

git push

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Git push failed. Aborting script." -ForegroundColor $ErrorColor
    exit 1
}

Write-Host "[INFO] Auto backup successfully." -ForegroundColor $InfoColor
