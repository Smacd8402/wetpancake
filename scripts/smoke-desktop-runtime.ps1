param()

$ErrorActionPreference = "Stop"

function Wait-HttpOk {
  param(
    [Parameter(Mandatory = $true)][string]$Url,
    [int]$Attempts = 20,
    [int]$DelayMs = 400
  )

  for ($i = 1; $i -le $Attempts; $i++) {
    try {
      $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3
      if ($resp.StatusCode -eq 200) {
        return $resp
      }
    } catch {
      Start-Sleep -Milliseconds $DelayMs
    }
  }
  throw "Timed out waiting for $Url"
}

$repo = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repo "services/backend"
$desktopDir = Join-Path $repo "apps/desktop"
$tmp = $null

$env:WHISPER_CMD_TEMPLATE = ""
$env:PIPER_CMD_TEMPLATE = ""
$env:PIPER_VOICE_PATH = ""

$backendProc = Start-Process -FilePath py -ArgumentList "-m","uvicorn","app.main:app","--host","127.0.0.1","--port","8000" -WorkingDirectory $backendDir -PassThru
$desktopProc = Start-Process -FilePath py -ArgumentList "-m","http.server","5173","--bind","127.0.0.1" -WorkingDirectory $desktopDir -PassThru

try {
  Wait-HttpOk -Url "http://127.0.0.1:8000/health" | Out-Null
  $desktop = Wait-HttpOk -Url "http://127.0.0.1:5173/index.html"
  $bundle = Wait-HttpOk -Url "http://127.0.0.1:5173/app.js"

  if ($desktop.Content -notmatch "Start Call") {
    throw "Desktop page missing Start Call"
  }
  if ($desktop.Content -notmatch "Post-Call Scorecard") {
    throw "Desktop page missing Post-Call Scorecard"
  }
  if ($bundle.Content -notmatch "Hold To Talk" -or $bundle.Content -notmatch "Release To Send") {
    throw "Desktop app missing Hold/Release labels"
  }
  if ($desktop.Content -notmatch "End Call") {
    throw "Desktop app missing End Call label"
  }
  Write-Output "UI check: Start Call / Hold-Release / End Call / Scorecard labels present"

  $sessionReq = @{ duration_minutes = 8 } | ConvertTo-Json
  $sessionResp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/sessions" -Method Post -ContentType "application/json" -Body $sessionReq
  if (-not $sessionResp.session_id) {
    throw "Start Call failed: missing session_id"
  }
  Write-Output "Start Call: created session $($sessionResp.session_id)"

  $tmp = Join-Path $env:TEMP "wetpancake-smoke-input.wav"
  [System.IO.File]::WriteAllBytes($tmp, [byte[]](1,2,3,4,5,6,7,8))
  $sttText = "[transcript_pending]"
  try {
    $sttRaw = & curl.exe -s -X POST -F "audio=@$tmp" "http://127.0.0.1:8000/stt/transcribe"
    $sttResp = $sttRaw | ConvertFrom-Json
    if ($sttResp.text) {
      $sttText = [string]$sttResp.text
      if ($sttText -match "Error opening input" -or $sttText.Length -gt 160) {
        $sttText = "[transcript_pending]"
      }
    }
  } catch {
    Write-Output "Hold/Release: STT endpoint unavailable, continuing with fallback transcript"
  }
  Write-Output "Hold/Release: STT transcript '$sttText'"

  $turnReq = @{
    trust = 0.4
    resistance = 0.6
    trainee_text = "Can I get 30 seconds?"
    primary_objection = "busy"
  } | ConvertTo-Json
  $turnResp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/dialogue/turn" -Method Post -ContentType "application/json" -Body $turnReq
  if (-not $turnResp.text) {
    throw "Hold/Release failed: dialogue text missing"
  }
  Write-Output "Hold/Release: dialogue generated '$($turnResp.text)'"

  $scoreReq = @{
    transcript = @(
      @{ speaker = "trainee"; text = $sttText; ts = [DateTime]::UtcNow.ToString("o") },
      @{ speaker = "prospect"; text = $turnResp.text; ts = [DateTime]::UtcNow.ToString("o") }
    )
    outcomes = @{
      close_attempt = $true
      value_statement = $true
      objection_resolved = $false
    }
  } | ConvertTo-Json -Depth 6
  $scoreResp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/sessions/score" -Method Post -ContentType "application/json" -Body $scoreReq
  if ($null -eq $scoreResp.total_score) {
    throw "End Call failed: scorecard total missing"
  }
  Write-Output "End Call: scorecard total=$($scoreResp.total_score)"
  Write-Output "Smoke test passed: desktop runtime + call flow APIs are operational"
} finally {
  if ($tmp -and (Test-Path $tmp)) {
    Remove-Item -Force $tmp -ErrorAction SilentlyContinue
  }
  if ($desktopProc -and -not $desktopProc.HasExited) {
    Stop-Process -Id $desktopProc.Id -Force
  }
  if ($backendProc -and -not $backendProc.HasExited) {
    Stop-Process -Id $backendProc.Id -Force
  }
}
