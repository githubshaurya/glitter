param([string]$RunRelativePath = 'proof/paper-run-20261117')
$ErrorActionPreference = 'Stop'
$repoPath = Split-Path -Parent $PSScriptRoot
$runDirectory = [IO.Path]::GetFullPath((Join-Path $repoPath $RunRelativePath))
if (-not $runDirectory.StartsWith((Join-Path $repoPath 'proof') + [IO.Path]::DirectorySeparatorChar)) { throw 'Run directory must be within project proof' }
$runFile = Join-Path $runDirectory 'run.json'
if (-not (Test-Path -LiteralPath $runFile)) { exit }
$plan = Get-Content -LiteralPath $runFile -Raw | ConvertFrom-Json
if ($plan.phase -in @('COMPLETED', 'INSUFFICIENT_SESSIONS') -or
    [DateTimeOffset]::UtcNow -ge [DateTimeOffset]::Parse($plan.sessions[-1].close)) { exit }
Set-Location -LiteralPath $repoPath
$dockerPath = Join-Path $env:LOCALAPPDATA 'Programs/DockerDesktop/resources/bin/docker.exe'
& $dockerPath desktop start --detach
$ready = $false
for ($attempt = 0; $attempt -lt 60; $attempt++) {
    & $dockerPath info --format '{{.ServerVersion}}' 2>$null
    if ($LASTEXITCODE -eq 0) { $ready = $true; break }
    Start-Sleep -Seconds 5
}
if (-not $ready) { throw 'Docker did not start within five minutes' }
$deploymentFile = Join-Path $runDirectory 'deployment.env'
$composeArgs = @('compose', '-f', 'compose.services.yml')
if (Test-Path -LiteralPath $deploymentFile) {
    $composeArgs += @('--env-file', (Join-Path $repoPath '.env'), '--env-file', $deploymentFile)
}
& $dockerPath @composeArgs -p glitter_paper_20261117 --profile shadow up -d --no-build
if ($LASTEXITCODE -ne 0) { throw 'Paper stack failed to resume' }
$pythonPath = Join-Path $repoPath '.venv/Scripts/python.exe'
if (Test-Path -LiteralPath $deploymentFile) {
    $pythonPath = (& py -3.12 -c 'import sys; print(sys.executable)').Trim()
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $pythonPath)) {
        throw 'The host Python 3.12 used by the paper log collector is unavailable'
    }
}
$captureScript = Join-Path $PSScriptRoot 'capture_runtime.py'
$captureProcess = Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'python*' -and $_.CommandLine -like "*$captureScript*" -and $_.CommandLine -like "*$runFile*" }
if (-not $captureProcess) {
    Start-Process -FilePath $pythonPath -ArgumentList @(('"'+$captureScript+'"'),'--run-file',('"'+$runFile+'"')) -WorkingDirectory $repoPath -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runDirectory 'runtime-helper.stdout.log') -RedirectStandardError (Join-Path $runDirectory 'runtime-helper.stderr.log')
}
$awakeScript = Join-Path $PSScriptRoot 'keep_awake.ps1'
& $awakeScript -RunFile $runFile
