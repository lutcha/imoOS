# ============================================================================
# ImoOS - DigitalOcean Deploy Script
# Deploy to DigitalOcean App Platform (No Docker Desktop needed!)
# ============================================================================

param(
    [string]$Branch = "develop",
    [switch]$SkipPush = $false,
    [switch]$SkipSuperuser = $false
)

$ErrorActionPreference = "Stop"
$API_BASE = "https://imos-staging-jiow3.ondigitalocean.app"
$SETUP_TOKEN = "imos-setup-2026"

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "🚀 ImoOS - DigitalOcean Deploy Script" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# Step 1: Verify Git Status
# ============================================================================
Write-Host "[1/4] Verifying git status..." -ForegroundColor Yellow
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "⚠️  You have uncommitted changes:" -ForegroundColor Yellow
    Write-Host $gitStatus
    $confirm = Read-Host "Continue anyway? (y/n)"
    if ($confirm -ne 'y') {
        Write-Host "❌ Aborted" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ Git status OK" -ForegroundColor Green
Write-Host ""

# ============================================================================
# Step 2: Commit and Push (optional)
# ============================================================================
if (-not $SkipPush) {
    Write-Host "[2/4] Committing and pushing to $Branch..." -ForegroundColor Yellow
    
    git add .
    git commit -m "deploy: fix auth for DigitalOcean staging"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  No changes to commit or commit failed, continuing..." -ForegroundColor Yellow
    } else {
        Write-Host "✅ Changes committed" -ForegroundColor Green
    }
    
    git push origin $Branch
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Push failed!" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Pushed to $Branch" -ForegroundColor Green
    Write-Host ""
    Write-Host "⏳ DigitalOcean is deploying automatically (5-10 minutes)..." -ForegroundColor Cyan
    Write-Host "   Check status: https://cloud.digitalocean.com/apps" -ForegroundColor Cyan
    Write-Host ""
    
    # Wait a bit for deployment to start
    Write-Host "Waiting 60 seconds for deployment to begin..." -ForegroundColor Yellow
    Start-Sleep -Seconds 60
} else {
    Write-Host "[2/4] Skipping push (already deployed)" -ForegroundColor Yellow
}
Write-Host ""

# ============================================================================
# Step 3: Check if deployment is ready
# ============================================================================
Write-Host "[3/4] Checking if API is ready..." -ForegroundColor Yellow
$healthUrl = "$API_BASE/api/v1/health/"
$maxAttempts = 30
$attempt = 0

while ($attempt -lt $maxAttempts) {
    try {
        $response = Invoke-WebRequest -Uri $healthUrl -Method GET -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ API is healthy!" -ForegroundColor Green
            break
        }
    } catch {
        $attempt++
        if ($attempt -ge $maxAttempts) {
            Write-Host "⚠️  API not ready after $($maxAttempts) attempts" -ForegroundColor Yellow
            Write-Host "   You may need to wait longer or check DO Dashboard" -ForegroundColor Yellow
            Write-Host "   https://cloud.digitalocean.com/apps" -ForegroundColor Cyan
            break
        }
        Write-Host "   Attempt $attempt/$maxAttempts - API not ready yet..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
    }
}
Write-Host ""

# ============================================================================
# Step 4: Create Superuser (optional)
# ============================================================================
if (-not $SkipSuperuser) {
    Write-Host "[4/4] Creating superuser..." -ForegroundColor Yellow
    
    # Check if superuser already exists
    try {
        $statusUrl = "$API_BASE/api/v1/setup/status/"
        $statusResponse = Invoke-RestMethod -Uri $statusUrl -Method GET -UseBasicParsing -TimeoutSec 10
        
        if ($statusResponse.has_superuser -eq $true) {
            Write-Host "✅ Superuser already exists!" -ForegroundColor Green
        } else {
            # Create superuser
            $body = @{
                email = "admin@proptech.cv"
                password = "ImoOS2026"
                first_name = "Admin"
                last_name = "ImoOS"
            } | ConvertTo-Json
            
            $superuserResponse = Invoke-RestMethod `
                -Uri "$API_BASE/api/v1/setup/superuser/" `
                -Method POST `
                -Headers @{
                    "Content-Type" = "application/json"
                    "X-Setup-Token" = $SETUP_TOKEN
                } `
                -Body $body `
                -UseBasicParsing `
                -TimeoutSec 10
            
            if ($superuserResponse.message -like "*created successfully*") {
                Write-Host "✅ Superuser created!" -ForegroundColor Green
                Write-Host "   Email: admin@proptech.cv" -ForegroundColor Cyan
                Write-Host "   Password: ImoOS2026" -ForegroundColor Cyan
            } else {
                Write-Host "⚠️  Unexpected response: $($superuserResponse | ConvertTo-Json)" -ForegroundColor Yellow
            }
        }
    } catch {
        Write-Host "⚠️  Could not check/create superuser: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "   You can try manually via DO Console or API" -ForegroundColor Yellow
    }
} else {
    Write-Host "[4/4] Skipping superuser creation" -ForegroundColor Yellow
}
Write-Host ""

# ============================================================================
# Step 5: Test Login
# ============================================================================
Write-Host "🧪 Testing superadmin login..." -ForegroundColor Yellow
try {
    $loginBody = @{
        email = "admin@proptech.cv"
        password = "ImoOS2026"
    } | ConvertTo-Json
    
    $loginResponse = Invoke-RestMethod `
        -Uri "$API_BASE/api/v1/users/auth/superadmin/token/" `
        -Method POST `
        -Headers @{
            "Content-Type" = "application/json"
        } `
        -Body $loginBody `
        -UseBasicParsing `
        -TimeoutSec 10
    
    if ($loginResponse.access) {
        Write-Host "✅ Login successful!" -ForegroundColor Green
        Write-Host "   User: $($loginResponse.user.email)" -ForegroundColor Cyan
        Write-Host "   Schema: $($loginResponse.tenant_schema)" -ForegroundColor Cyan
        Write-Host "   Staff: $($loginResponse.user.is_staff)" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "🎉 Deployment complete!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🌐 Super Admin: https://proptech.cv/superadmin/login" -ForegroundColor Cyan
        Write-Host "🌐 Tenant: https://demo.proptech.cv/login" -ForegroundColor Cyan
        Write-Host "📊 DO Dashboard: https://cloud.digitalocean.com/apps" -ForegroundColor Cyan
    } else {
        Write-Host "⚠️  Login failed - check credentials or deployment status" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Login test failed: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "   This is normal if tenant/users don't exist yet" -ForegroundColor Yellow
    Write-Host "   Check DO Dashboard for deployment status" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Done!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
