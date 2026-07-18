# Install / launch Voicebox for Tony (Windows)
# Usage: powershell -ExecutionPolicy Bypass -File scripts/install_voicebox.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Dir = Join-Path $Root "tools\voicebox"
$Msi = Join-Path $Dir "Voicebox_x64_en-US.msi"
$Url = "https://github.com/jamiepine/voicebox/releases/download/v0.5.0/Voicebox_0.5.0_x64_en-US.msi"

New-Item -ItemType Directory -Force -Path $Dir | Out-Null

if (-not (Test-Path $Msi) -or (Get-Item $Msi).Length -lt 1MB) {
  Write-Host "Downloading Voicebox (~530MB)..."
  Invoke-WebRequest -Uri $Url -OutFile $Msi -UseBasicParsing
}

Write-Host "Installing Voicebox (may prompt for admin)..."
$p = Start-Process msiexec.exe -ArgumentList "/i `"$Msi`" /passive /norestart" -Wait -PassThru
Write-Host "msiexec exit code: $($p.ExitCode)"

$candidates = @(
  "$env:LOCALAPPDATA\Programs\Voicebox\Voicebox.exe",
  "$env:ProgramFiles\Voicebox\Voicebox.exe",
  "${env:ProgramFiles(x86)}\Voicebox\Voicebox.exe"
)
$exe = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $exe) {
  $exe = Get-ChildItem -Path "$env:LOCALAPPDATA","$env:ProgramFiles" -Filter "Voicebox.exe" -Recurse -ErrorAction SilentlyContinue |
    Select-Object -First 1 -ExpandProperty FullName
}

if ($exe) {
  Write-Host "Launching $exe"
  Start-Process $exe
  Write-Host "Next: create/clone a voice profile in Voicebox, then set VOICEBOX_PROFILE in .env"
} else {
  Write-Host "Install finished but Voicebox.exe not found yet. Open Start Menu and launch Voicebox."
}
