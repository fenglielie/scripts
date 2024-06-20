python ./blogcheck.py

if ($LastExitCode -ne 0) {
    Write-Host "blog check: fail."
    exit 1
}

python ./headcheck.py

if ($LastExitCode -ne 0) {
    Write-Host "head check: fail."
    exit 1
}

$env:Path += "$((Get-Item -Path ../node_modules/.bin -Force).FullName);"

hexo clean

if ($LastExitCode -ne 0) {
    Write-Host "hexo clean: fail."
    exit 1
}

hexo g

if ($LastExitCode -ne 0) {
    Write-Host "hexo g: fail."
    exit 1
}

hexo d

if ($LastExitCode -ne 0) {
    Write-Host "hexo d: fail."
    exit 1
}
