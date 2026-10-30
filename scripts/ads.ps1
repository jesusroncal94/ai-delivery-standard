# Windows PowerShell entry point; forwards to scripts/ads.sh through Git Bash.
# Example: .\scripts\ads.ps1 check ..\my-project
# Example: .\scripts\ads.ps1 portfolio ..\projects-registry\portfolio.yaml --output /portfolio/PORTFOLIO.md
# Git Bash is found next to Git for Windows: the bash.exe first on PATH is often WSL's, which cannot run Windows paths.
$bash = $null
if (Get-Command git -ErrorAction SilentlyContinue) {
    $bash = Join-Path (Split-Path (Split-Path (Split-Path (git --exec-path)))) 'bin\bash.exe'
}
if ($null -eq $bash -or -not (Test-Path $bash)) {
    Write-Error 'Git Bash is required (Git for Windows).'
    exit 1
}
& $bash (Join-Path $PSScriptRoot 'ads.sh') @args
exit $LASTEXITCODE
