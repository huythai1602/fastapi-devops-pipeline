param(
    [string]$HealthUrl = "http://localhost:8002/health",
    [int]$Attempts = 10
)

$ErrorActionPreference = "Stop"

for ($i = 1; $i -le $Attempts; $i++) {
    $response = Invoke-RestMethod -Uri $HealthUrl -TimeoutSec 3
    if ($response.status -ne "healthy") {
        Write-Error "Canary health check failed at attempt $i."
        exit 1
    }
    Start-Sleep -Seconds 2
}

Write-Host "Canary health checks passed."
