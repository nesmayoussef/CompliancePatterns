# RFQ Process Mining Docker Setup Script for Windows PowerShell
# This script sets up and runs the RFQ process mining environment using Docker

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "RFQ Process Mining with MTL Monitoring - Docker Setup" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
try {
    $dockerVersion = docker --version 2>$null
    Write-Host "Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Docker is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Docker Desktop for Windows from:" -ForegroundColor Yellow
    Write-Host "https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Docker is running
try {
    docker info 2>$null | Out-Null
    Write-Host "Docker is running." -ForegroundColor Green
} catch {
    Write-Host "ERROR: Docker is not running" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Setting up RFQ Process Mining environment..." -ForegroundColor Yellow
Write-Host ""

# Navigate to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Build the Docker image
Write-Host "Building Docker image..." -ForegroundColor Yellow
try {
    docker-compose -f docker-compose.simple.yml build
    if ($LASTEXITCODE -ne 0) {
        throw "Build failed"
    }
    Write-Host "Docker image built successfully!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to build Docker image" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Start the container
Write-Host "Starting RFQ Process Mining container..." -ForegroundColor Yellow
try {
    docker-compose -f docker-compose.simple.yml up -d
    if ($LASTEXITCODE -ne 0) {
        throw "Container start failed"
    }
} catch {
    Write-Host "ERROR: Failed to start container" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "RFQ Process Mining Environment is Ready!" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Container Status:" -ForegroundColor Yellow
docker-compose -f docker-compose.simple.yml ps

Write-Host ""
Write-Host "Available Services:" -ForegroundColor Yellow
Write-Host "  - Main Container: rfq-mtl-monitoring" -ForegroundColor White
Write-Host "  - Jupyter Lab: http://localhost:8888" -ForegroundColor White

Write-Host ""
Write-Host "Quick Commands:" -ForegroundColor Yellow
Write-Host "  1. Generate traces:    docker exec rfq-mtl-monitoring generate-traces" -ForegroundColor White
Write-Host "  2. Run monitoring:     docker exec rfq-mtl-monitoring run-monitoring" -ForegroundColor White
Write-Host "  3. View results:       docker exec rfq-mtl-monitoring view-results" -ForegroundColor White
Write-Host "  4. Open shell:         docker exec -it rfq-mtl-monitoring bash" -ForegroundColor White
Write-Host "  5. Stop container:     docker-compose -f docker-compose.simple.yml down" -ForegroundColor White

Write-Host ""
Write-Host "For detailed instructions, see README-Docker.md" -ForegroundColor Cyan
Write-Host ""

# Offer to run the complete workflow
$runWorkflow = Read-Host "Would you like to run the complete RFQ monitoring workflow now? (y/n)"
if ($runWorkflow -eq 'y' -or $runWorkflow -eq 'Y') {
    Write-Host ""
    Write-Host "Running complete workflow..." -ForegroundColor Yellow
    
    Write-Host "Step 1: Generating traces..." -ForegroundColor Cyan
    docker exec rfq-mtl-monitoring generate-traces
    
    Write-Host ""
    Write-Host "Step 2: Running MTL monitoring..." -ForegroundColor Cyan
    docker exec rfq-mtl-monitoring run-monitoring
    
    Write-Host ""
    Write-Host "Step 3: Viewing results..." -ForegroundColor Cyan
    docker exec rfq-mtl-monitoring view-results
    
    Write-Host ""
    Write-Host "Workflow completed! Check the results above." -ForegroundColor Green
}

Read-Host "Press Enter to exit"

