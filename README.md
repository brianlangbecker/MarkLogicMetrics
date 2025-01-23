# MarkLogic Metrics Collector

Collects metrics from MarkLogic and exports them to Honeycomb using OpenTelemetry.

## Setup Instructions

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Configure the script:

   - Update MARKLOGIC_MANAGE_HOST if needed (default: "http://localhost:8002")
   - Set your HONEYCOMB_API_KEY in the script
   - Update USERNAME and PASSWORD if needed (default: "admin"/"admin")

4. Run the script:

```bash
python marklogic_honeycomb_metrics.py
```

## Expected Output

You should see:

- Metrics being collected from MarkLogic
- Console output showing metric values
- Metrics being exported to Honeycomb

## Stopping the Collector

Press Ctrl+C to stop the collector. It will flush any remaining metrics before exiting.

## Troubleshooting

1. If you see connection errors:

   - Verify MarkLogic is running
   - Check your host/port settings
   - Verify username/password

2. If metrics aren't appearing in Honeycomb:
   - Verify your API key
   - Check the console output for errors
   - Verify network connectivity

## Development

The project structure is:

```
marklogic-metrics/
├── .gitignore
├── README.md
├── requirements.txt
├── setup.py
└── marklogic_honeycomb_metrics.py
```
