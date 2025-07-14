# RFQ Process Mining with MTL Monitoring - Docker Environment
# Base image with Python 3.11
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    git \
    curl \
    wget \
    zip \
    unzip \
    vim \
    nano \
    tree \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    numpy \
    matplotlib \
    pandas \
    scipy \
    seaborn \
    plotly \
    jupyter \
    jupyterlab \
    metric-temporal-logic \
    jsonschema \
    pyyaml \
    requests

# Create application directories
RUN mkdir -p /app/rfq_process_mining/{traces,monitoring,specifications,results,docker}

# Use this:
COPY ../monitoring/ /app/rfq_process_mining/monitoring/
COPY ../traces/ /app/rfq_process_mining/traces/
COPY ../specifications/ /app/rfq_process_mining/specifications/
COPY ../results/ /app/rfq_process_mining/results/

# Create a startup script
RUN echo '#!/bin/bash\n\
echo "=== RFQ Process Mining with MTL Monitoring ==="\n\
echo "Docker environment ready!"\n\
echo ""\n\
echo "Available commands:"\n\
echo "  generate-traces    - Generate RFQ process traces"\n\
echo "  run-monitoring     - Run MTL monitoring"\n\
echo "  view-results       - View monitoring results"\n\
echo "  jupyter-lab        - Start Jupyter Lab"\n\
echo "  bash               - Open bash shell"\n\
echo ""\n\
cd /app/rfq_process_mining\n\
exec "$@"' > /app/entrypoint.sh

# Create convenience scripts
RUN echo '#!/bin/bash\n\
cd /app/rfq_process_mining/traces\n\
python3 trace_generator.py\n\
echo "Traces generated successfully!"' > /app/generate-traces

RUN echo '#!/bin/bash\n\
cd /app/rfq_process_mining/monitoring\n\
python3 rfq_mtl_monitor.py\n\
echo "Monitoring completed!"' > /app/run-monitoring

RUN echo '#!/bin/bash\n\
cd /app/rfq_process_mining/results\n\
echo "=== Monitoring Results ==="\n\
if [ -f simplified_monitoring_report.json ]; then\n\
    python3 -c "import json; data=json.load(open(\"simplified_monitoring_report.json\")); print(f\"Total traces: {data[\"monitoring_summary\"][\"total_traces\"]}\"); print(f\"Compliant: {data[\"monitoring_summary\"][\"compliant_traces\"]}\"); print(f\"Violating: {data[\"monitoring_summary\"][\"violating_traces\"]}\"); print(f\"Accuracy: {data[\"monitoring_summary\"][\"prediction_accuracy\"]:.2%}\")"\n\
    echo ""\n\
    echo "Full report available in: simplified_monitoring_report.json"\n\
else\n\
    echo "No results found. Run monitoring first with: run-monitoring"\n\
fi' > /app/view-results

RUN echo '#!/bin/bash\n\
cd /app/rfq_process_mining\n\
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token="" --NotebookApp.password=""' > /app/jupyter-lab

# Make scripts executable
RUN chmod +x /app/entrypoint.sh /app/generate-traces /app/run-monitoring /app/view-results /app/jupyter-lab

# Add scripts to PATH
ENV PATH="/app:${PATH}"

# Expose ports
EXPOSE 8888

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command
CMD ["bash"]

