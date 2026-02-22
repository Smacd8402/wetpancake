param()

$backend = "http://127.0.0.1:8000/health"

try {
  $resp = Invoke-WebRequest -Uri $backend -UseBasicParsing -TimeoutSec 5
  if ($resp.StatusCode -ne 200) {
    Write-Error "Backend health check failed with status $($resp.StatusCode)"
    exit 1
  }
} catch {
  Write-Error "Backend health check failed: $($_.Exception.Message)"
  exit 1
}

Write-Output "check.ps1: all basic checks passed"
