# MarkLogic Log Collector

Collects MarkLogic logs and exports them to Honeycomb using OpenTelemetry Collector.

## Requirements

- Python 3.7
- pip (latest version)

## Setup

1. Create and activate a Python virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # Or on Windows:
   # .\venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install --upgrade pip
   # You may need to install git if not already installed
   pip install -r requirements.txt
   ```

3. Update configuration in `marklogic_honeycomb_metrics.py`:

   ```python
   # MarkLogic Management API configuration
   MARKLOGIC_MANAGE_HOST = "http://localhost:8002"  # Update if needed
   USERNAME = "admin"                               # Update if needed
   PASSWORD = "admin"                               # Update if needed

   # Honeycomb configuration
   HONEYCOMB_API_KEY = "YourHoneycombAPIKey"       # Required
   HONEYCOMB_DATASET = "YourHoneycombDatasetName"  # Required
   ```

4. Run the collector:
   ```bash
   python3 marklogic_honeycomb_metrics.py
   ```

## License

MIT
