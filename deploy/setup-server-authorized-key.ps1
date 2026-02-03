# Run this script from your PC when you have SSH access to the server (e.g. password or existing key).
# It appends the deploy public key to root@38.242.237.64 so GitHub Actions can deploy.

$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$pubKeyPath = Join-Path $projectRoot "deploy_key.pub"

if (-not (Test-Path $pubKeyPath)) {
    Write-Error "Public key not found: $pubKeyPath. Generate it first (see deploy/README.md)."
    exit 1
}

Write-Host "Appending deploy_key.pub to root@38.242.237.64 authorized_keys..."
Get-Content $pubKeyPath | ssh -o StrictHostKeyChecking=accept-new root@38.242.237.64 "mkdir -p ~/.ssh; chmod 700 ~/.ssh; cat >> ~/.ssh/authorized_keys; chmod 600 ~/.ssh/authorized_keys; echo 'Key added.'"
Write-Host "Done. Test with: ssh -i $projectRoot\deploy_key root@38.242.237.64 echo OK"
