param(
    [string]$Image = "fastapi-devops-pipeline:latest",
    [ValidateSet("blue", "green")]
    [string]$Target = "green"
)

$ErrorActionPreference = "Stop"

$service = "app-$Target"
$port = if ($Target -eq "green") { "8002" } else { "8001" }
$env:APP_IMAGE = $Image

Write-Host "Deploying $Image to $Target environment..."
docker compose --profile $Target up -d $service

Write-Host "Waiting for $Target health check on port $port..."
for ($i = 1; $i -le 30; $i++) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:$port/health" -TimeoutSec 3
        if ($response.status -eq "healthy") {
            Write-Host "$Target environment is healthy."
            Write-Host "Switch traffic to http://localhost:$port after this check passes."
            exit 0
        }
    }
    catch {
        Start-Sleep -Seconds 2
    }
}

Write-Error "$Target deployment failed health checks. Keep current environment running and roll back traffic."
exit 1
