# PowerShell script for testing the Cloud Function worker

# Get the directory of this script and navigate to backend directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path (Join-Path $ScriptDir "../..")

# Generate the mock CloudEvent
Write-Host "Generating mock CloudEvent from payload..."
python tests/cloud_run/prepare_test_event.py

# Check if a service is running on port 8080
$portInUse = $null
try {
    $portInUse = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
} catch {}

if ($portInUse) {
    Write-Host "A service is already running on port 8080. Please stop it before running this test."
    exit 1
}

# Start the functions-framework in a separate process
Write-Host "Starting Functions Framework..."
$process = Start-Process -FilePath "functions-framework" -ArgumentList "--source=cloud_run/worker/main.py", "--target=handle_pubsub", "--signature-type=cloudevent", "--port=8080" -PassThru -WindowStyle Hidden

# Give it a moment to start up
Start-Sleep -Seconds 2

# Send the test request
Write-Host "Sending test request..."
Invoke-WebRequest -Method POST -Uri "http://localhost:8080" -Headers @{"Content-Type"="application/cloudevents+json"} -InFile "tests/cloud_run/mock_cloudevent.json"

# Cleanup
Write-Host "Stopping Functions Framework (PID: $($process.Id))..."
Stop-Process -Id $process.Id
Write-Host "Test completed."
