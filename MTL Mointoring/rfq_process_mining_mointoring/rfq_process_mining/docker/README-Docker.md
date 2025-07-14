# RFQ Process Mining - Docker Setup for Windows

This guide helps you run the RFQ Process Mining with MTL Monitoring scenario on Windows using Docker.

## Prerequisites

### 1. Install Docker Desktop for Windows
- Download from: https://www.docker.com/products/docker-desktop
- Install and start Docker Desktop
- Ensure Docker is running (check system tray icon)

### 2. Enable WSL 2 (if prompted)
- Docker Desktop may require WSL 2 backend
- Follow Docker's installation guide for WSL 2 setup

## Quick Start

### Option 1: Automated Setup (Recommended)
1. **Extract the project files** to a folder (e.g., `C:\rfq-process-mining\`)
2. **Open Command Prompt as Administrator**
3. **Navigate to the docker directory**:
   ```cmd
   cd C:\rfq-process-mining\rfq_process_mining\docker
   ```
4. **Run the setup script**:
   ```cmd
   setup-windows.bat
   ```

### Option 2: Manual Setup
1. **Open Command Prompt** in the docker directory
2. **Build the Docker image**:
   ```cmd
   docker-compose -f docker-compose.simple.yml build
   ```
3. **Start the container**:
   ```cmd
   docker-compose -f docker-compose.simple.yml up -d
   ```

## Using the Environment

### Core Commands

#### 1. Generate RFQ Process Traces
```cmd
docker exec rfq-mtl-monitoring generate-traces
```
This creates 14 traces (6 compliant + 8 violating) in the `traces/` directory.

#### 2. Run MTL Monitoring
```cmd
docker exec rfq-mtl-monitoring run-monitoring
```
This processes all traces and checks MTL properties for compliance violations.

#### 3. View Results
```cmd
docker exec rfq-mtl-monitoring view-results
```
This displays a summary of monitoring results.

#### 4. Open Interactive Shell
```cmd
docker exec -it rfq-mtl-monitoring bash
```
This opens a bash shell inside the container for manual exploration.

### Advanced Usage

#### Access Jupyter Lab
1. **Start Jupyter Lab**:
   ```cmd
   docker exec rfq-mtl-monitoring jupyter-lab
   ```
2. **Open browser** and go to: http://localhost:8888
3. **Explore notebooks** and run interactive analysis

#### View Container Logs
```cmd
docker-compose -f docker-compose.simple.yml logs -f
```

#### Stop the Environment
```cmd
docker-compose -f docker-compose.simple.yml down
```

#### Restart the Environment
```cmd
docker-compose -f docker-compose.simple.yml restart
```

## Project Structure in Container

```
/app/rfq_process_mining/
├── traces/                     # Generated event traces
│   ├── trace_generator.py      # Trace generation script
│   ├── rfq_event_log.json     # Combined event log
│   └── RFQ_*.json             # Individual traces
├── monitoring/                 # MTL monitoring system
│   ├── simplified_rfq_monitor.py  # Main monitoring script
│   └── rfq_mtl_monitor.py     # Alternative implementation
├── specifications/             # Process definitions
│   └── process_definition.md  # MTL properties & business rules
├── results/                    # Monitoring results
│   └── *.json                 # Generated reports
└── docker/                     # Docker configuration
    ├── Dockerfile
    ├── docker-compose.yml
    └── setup-windows.bat
```

## File Persistence

The Docker setup uses volume mounts to persist data:
- **Project files**: Mounted from your Windows filesystem
- **Generated data**: Stored in Docker volume `rfq_data`
- **Results**: Saved to `results/` directory (accessible from Windows)

## Troubleshooting

### Docker Issues

#### "Docker is not running"
- Start Docker Desktop from Windows Start Menu
- Wait for Docker to fully initialize (green icon in system tray)

#### "Port 8888 already in use"
- Stop other Jupyter instances: `docker stop $(docker ps -q --filter "expose=8888")`
- Or change port in `docker-compose.simple.yml`

#### "Build failed"
- Ensure internet connection for downloading packages
- Try: `docker system prune` to clean up Docker cache
- Rebuild: `docker-compose -f docker-compose.simple.yml build --no-cache`

### Container Issues

#### "Container not found"
- Check if container is running: `docker ps`
- Start if stopped: `docker-compose -f docker-compose.simple.yml up -d`

#### "Permission denied"
- Run Command Prompt as Administrator
- Ensure Docker Desktop has proper permissions

### Python/Code Issues

#### "Module not found"
- The container includes all required Python packages
- If issues persist, rebuild the image: `docker-compose -f docker-compose.simple.yml build --no-cache`

#### "No traces found"
- Run trace generation first: `docker exec rfq-mtl-monitoring generate-traces`
- Check traces directory: `docker exec rfq-mtl-monitoring ls -la /app/rfq_process_mining/traces/`

## Expected Results

### Successful Execution
After running the complete workflow, you should see:

1. **Trace Generation**: 14 JSON files created
   - 6 compliant scenarios
   - 8 violating scenarios

2. **Monitoring Results**: 100% prediction accuracy
   - All compliant traces correctly identified
   - All violations properly detected

3. **Property Violations Detected**:
   - Offer preservation: 3 violations
   - Timely PO response: 2 violations
   - Late PO denial: 3 violations
   - Late PO incorrectly accepted: 3 violations

### Sample Output
```
=== Summary ===
Total traces: 14
Detected compliant: 6
Detected violating: 8
Compliance rate: 42.86%
Prediction accuracy: 100.00%
```

## Development Workflow

### Modifying Code
1. **Edit files** on Windows using your preferred editor
2. **Changes are automatically reflected** in the container (via volume mounts)
3. **Re-run scripts** to test changes:
   ```cmd
   docker exec rfq-mtl-monitoring run-monitoring
   ```

### Adding New Features
1. **Modify Python scripts** in the mounted directories
2. **Install additional packages** if needed:
   ```cmd
   docker exec rfq-mtl-monitoring pip install package-name
   ```
3. **Update Dockerfile** for permanent package additions

### Debugging
1. **Open interactive shell**:
   ```cmd
   docker exec -it rfq-mtl-monitoring bash
   ```
2. **Run Python scripts manually**:
   ```bash
   cd /app/rfq_process_mining/monitoring
   python3 simplified_rfq_monitor.py
   ```
3. **Check logs and outputs** directly

## Performance Notes

- **First build**: May take 5-10 minutes (downloads base image + packages)
- **Subsequent builds**: Much faster (uses Docker cache)
- **Execution time**: Trace generation + monitoring typically < 30 seconds
- **Memory usage**: ~500MB RAM for the container

## Security Considerations

- **Jupyter Lab**: Runs without authentication (localhost only)
- **Container access**: Full access to mounted directories
- **Network**: Container isolated in Docker network
- **Production use**: Add authentication and security measures

## Support

For issues or questions:
1. **Check Docker logs**: `docker-compose -f docker-compose.simple.yml logs`
2. **Verify setup**: Ensure all files are in correct directories
3. **Clean restart**: Stop container, remove, and rebuild if needed

This Docker setup provides a complete, isolated environment for running the RFQ Process Mining scenario on Windows without requiring local Python installation or dependency management.

