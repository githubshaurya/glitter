param(
    [Parameter(Mandatory = $true)][string]$RunFile
)
$ErrorActionPreference = 'Stop'
Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class PaperRunAwake {
    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern uint SetThreadExecutionState(uint flags);
}
'@
try {
    while (Test-Path -LiteralPath $RunFile) {
        $plan = Get-Content -LiteralPath $RunFile -Raw | ConvertFrom-Json
        $cutoff = [DateTimeOffset]::Parse($plan.sessions[-1].close)
        if ($plan.phase -in @('COMPLETED', 'INSUFFICIENT_SESSIONS') -or [DateTimeOffset]::UtcNow -ge $cutoff) { break }
        # Keep the system awake for this run only; screen power and the global power plan are unchanged.
        $result = [PaperRunAwake]::SetThreadExecutionState([uint32]2147483649)
        if ($result -eq 0) { throw 'Windows refused the temporary execution-state request' }
        Start-Sleep -Seconds 30
    }
}
finally {
    [void][PaperRunAwake]::SetThreadExecutionState([uint32]2147483648)
    if (Test-Path -LiteralPath $RunFile) {
        $finalPlan = Get-Content -LiteralPath $RunFile -Raw | ConvertFrom-Json
        if ($finalPlan.phase -in @('COMPLETED', 'INSUFFICIENT_SESSIONS') -or
            [DateTimeOffset]::UtcNow -ge [DateTimeOffset]::Parse($finalPlan.sessions[-1].close)) {
            $runName = Split-Path -Leaf (Split-Path -Parent $RunFile)
            $shortcutPath = Join-Path ([Environment]::GetFolderPath('Startup')) ('Glitter ' + $runName.Replace('-', ' ') + '.lnk')
            if (Test-Path -LiteralPath $shortcutPath) {
                $shell = New-Object -ComObject WScript.Shell
                $shortcut = $shell.CreateShortcut($shortcutPath)
                $resumeScript = Join-Path $PSScriptRoot 'resume_paper_run.ps1'
                if ($shortcut.Arguments.Contains($resumeScript)) { Remove-Item -LiteralPath $shortcutPath }
            }
        }
    }
}
