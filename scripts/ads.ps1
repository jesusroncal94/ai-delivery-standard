# Windows PowerShell entry point; forwards to scripts/ads.sh through Git Bash.
# Example: .\scripts\ads.ps1 check ..\my-project
$bash = Get-Command bash -ErrorAction SilentlyContinue
if ($null -eq $bash) {
    Write-Error 'Git Bash is required (bash.exe on PATH).'
    exit 1
}
& $bash.Source (Join-Path $PSScriptRoot 'ads.sh') @args
exit $LASTEXITCODE
