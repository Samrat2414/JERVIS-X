$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

Write-Host "Installing build dependencies..."
python -m pip install -r requirements-build.txt

Write-Host "Building JERVIS-X.exe..."
python -m PyInstaller `
    --clean `
    --noconfirm `
    --name JERVIS-X `
    --onefile `
    main.py

$zipPath = Join-Path $projectRoot "dist\JERVIS-X-Windows.zip"
$checksumPath = "$zipPath.sha256"

Write-Host "Creating Windows ZIP..."
Compress-Archive `
    -Path "dist\JERVIS-X.exe", "README.md", "LICENSE" `
    -DestinationPath $zipPath `
    -Force

$hash = (Get-FileHash $zipPath -Algorithm SHA256).Hash
"$hash  JERVIS-X-Windows.zip" |
    Set-Content $checksumPath -Encoding ASCII

Write-Host ""
Write-Host "Build complete:"
Write-Host $zipPath
Write-Host $checksumPath
Write-Host "SHA-256: $hash"