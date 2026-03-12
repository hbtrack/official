$ErrorActionPreference = "Stop"

# Canonical PATH bootstrap for Contract Gates tooling (CI/local).
# Goal: make Node-based CLIs in `node_modules/.bin` available as plain commands:
#   redocly, spectral, ajv

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\\..")).Path
$nodeBin = Join-Path $repoRoot "node_modules\\.bin"

if (-not ($env:Path -like "*$nodeBin*")) {
  $env:Path = "$nodeBin;$env:Path"
}

# Add Go runtime to PATH if installed in default location (Windows)
$defaultGoRuntimeBin = "C:\\Program Files\\Go\\bin"
if ((Test-Path $defaultGoRuntimeBin) -and (-not ($env:Path -like "*$defaultGoRuntimeBin*"))) {
  $env:Path = "$defaultGoRuntimeBin;$env:Path"
}

# Go-installed CLIs (ex.: oasdiff) typically land in:
# - %USERPROFILE%\go\bin (default GOPATH on Windows)
# - $(go env GOPATH)\bin (if Go is installed/configured)
$defaultGoBin = Join-Path $env:USERPROFILE "go\\bin"
if (Test-Path $defaultGoBin) {
  if (-not ($env:Path -like "*$defaultGoBin*")) {
    $env:Path = "$defaultGoBin;$env:Path"
  }
}

try {
  $goPath = & go env GOPATH 2>$null
  if ($LASTEXITCODE -eq 0 -and $goPath) {
    $goBin = Join-Path $goPath "bin"
    if (Test-Path $goBin) {
      if (-not ($env:Path -like "*$goBin*")) {
        $env:Path = "$goBin;$env:Path"
      }
    }
  }
} catch {
  # Go not installed; ignore.
}
