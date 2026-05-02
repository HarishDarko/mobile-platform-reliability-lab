param(
    [string]$ApiBaseUrl = "http://127.0.0.1:8000",
    [int]$NormalRequests = 3,
    [int]$SlowRequests = 2,
    [int]$ErrorRequests = 2
)

$ErrorActionPreference = "Stop"

function Invoke-LabRequest {
    param(
        [string]$Method,
        [string]$Path,
        [object]$Body = $null
    )

    $requestId = "demo-$([guid]::NewGuid().ToString())"
    $url = "$ApiBaseUrl$Path"
    $headers = @{ "x-request-id" = $requestId }
    $started = Get-Date

    try {
        if ($null -eq $Body) {
            $response = Invoke-WebRequest -Uri $url -Method $Method -Headers $headers -UseBasicParsing
        } else {
            $json = $Body | ConvertTo-Json -Depth 5
            $response = Invoke-WebRequest -Uri $url -Method $Method -Headers $headers -Body $json -ContentType "application/json" -UseBasicParsing
        }

        $durationMs = [math]::Round(((Get-Date) - $started).TotalMilliseconds, 2)
        [pscustomobject]@{
            Method = $Method
            Path = $Path
            Status = [int]$response.StatusCode
            DurationMs = $durationMs
            RequestId = $requestId
        }
    } catch {
        $durationMs = [math]::Round(((Get-Date) - $started).TotalMilliseconds, 2)
        $statusCode = if ($_.Exception.Response) { [int]$_.Exception.Response.StatusCode } else { 0 }
        [pscustomobject]@{
            Method = $Method
            Path = $Path
            Status = $statusCode
            DurationMs = $durationMs
            RequestId = $requestId
        }
    }
}

Write-Host "Sending observability traffic to $ApiBaseUrl"

if ($NormalRequests -gt 0) {
    1..$NormalRequests | ForEach-Object {
        Invoke-LabRequest -Method "GET" -Path "/health"
        Invoke-LabRequest -Method "GET" -Path "/accounts"
        Invoke-LabRequest -Method "POST" -Path "/payments" -Body @{
            from_account_id = "demo-chequing-001"
            to_payee = "Demo Utility"
            amount = 12.34
            currency = "CAD"
        }
    }
}

if ($SlowRequests -gt 0) {
    1..$SlowRequests | ForEach-Object {
        Invoke-LabRequest -Method "GET" -Path "/slow"
    }
}

if ($ErrorRequests -gt 0) {
    1..$ErrorRequests | ForEach-Object {
        Invoke-LabRequest -Method "GET" -Path "/error"
    }
}

Write-Host "Fetch metrics after traffic:"
Write-Host "Invoke-RestMethod `"$ApiBaseUrl/metrics`""
