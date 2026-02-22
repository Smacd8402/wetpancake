param()

$backend = "http://127.0.0.1:8000/health"
$runtime = "http://127.0.0.1:8000/runtime/health"

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

try {
  $runtimeResp = Invoke-RestMethod -Uri $runtime -Method Get -TimeoutSec 5
  if (-not $runtimeResp.ok) {
    Write-Error "Runtime dependency check failed"
    $runtimeResp.checks.PSObject.Properties | ForEach-Object {
      $name = $_.Name
      $ok = $_.Value.ok
      $detail = $_.Value.detail
      Write-Output " - $name : ok=$ok detail=$detail"
    }
    exit 1
  }
} catch {
  Write-Error "Runtime health endpoint failed: $($_.Exception.Message)"
  exit 1
}

Write-Output "check.ps1: all dependency checks passed"
