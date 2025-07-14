@echo off
REM RFQ Process Mining Docker Setup Script for Windows
REM This script sets up and runs the RFQ process mining environment using Docker

echo ===================================================
echo RFQ Process Mining with MTL Monitoring - Docker Setup
echo ===================================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop for Windows from:
    echo https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo Docker found. Checking Docker status...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

echo Docker is running. Setting up RFQ Process Mining environment...
echo.

REM Navigate to docker directory
cd /d "%~dp0"

REM Build the Docker image
echo Building Docker image...
docker-compose -f docker-compose.simple.yml build

if %errorlevel% neq 0 (
    echo ERROR: Failed to build Docker image
    pause
    exit /b 1
)

echo.
echo Docker image built successfully!
echo.

REM Start the container
echo Starting RFQ Process Mining container...
docker-compose -f docker-compose.simple.yml up -d

if %errorlevel% neq 0 (
    echo ERROR: Failed to start container
    pause
    exit /b 1
)

echo.
echo ===================================================
echo RFQ Process Mining Environment is Ready!
echo ===================================================
echo.
echo Container Status:
docker-compose -f docker-compose.simple.yml ps
echo.
echo Available Services:
echo   - Main Container: rfq-mtl-monitoring
echo   - Jupyter Lab: http://localhost:8888
echo.
echo Quick Commands:
echo   1. Generate traces:    docker exec rfq-mtl-monitoring generate-traces
echo   2. Run monitoring:     docker exec rfq-mtl-monitoring run-monitoring
echo   3. View results:       docker exec rfq-mtl-monitoring view-results
echo   4. Open shell:         docker exec -it rfq-mtl-monitoring bash
echo   5. Stop container:     docker-compose -f docker-compose.simple.yml down
echo.
echo For detailed instructions, see README-Docker.md
echo.
pause

