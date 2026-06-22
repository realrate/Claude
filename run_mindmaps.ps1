# Run from any directory — script always executes from its own folder
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$COMPANIES = @("trilinc", "strata", "hp", "angi", "nvidia", "tesla", "apple")

if ($args.Count -eq 0) {
    Write-Host "Usage: .\run_mindmaps.ps1 <company> [company2 ...] | .\run_mindmaps.ps1 all"
    Write-Host "Companies: $($COMPANIES -join ', ')"
    exit 0
}

$targets = if ($args[0] -eq "all") { $COMPANIES } else { $args }

foreach ($company in $targets) {
    if ($COMPANIES -notcontains $company) {
        Write-Warning "Unknown company: $company — skipping"
        continue
    }
    Write-Host "Generating mind map for $company..."
    python gen_mindmap.py $company
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Failed: $company (exit $LASTEXITCODE)"
    }
}
