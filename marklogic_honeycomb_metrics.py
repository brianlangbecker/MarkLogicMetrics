from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource
from marklogic import Client
import time
import json
from datetime import datetime
import traceback
from opentelemetry.metrics._internal.observation import Observation

# MarkLogic Management API configuration
MARKLOGIC_MANAGE_HOST = "http://localhost:8002"  # For management API
USERNAME = "admin"
PASSWORD = "admin"

# Honeycomb configuration
HONEYCOMB_API_KEY = "your_honeycomb_api_key_here"
HONEYCOMB_DATASET = "HoneycombDatasetName"

print("Initializing MarkLogic client...")
manage_client = Client(MARKLOGIC_MANAGE_HOST, digest=(USERNAME, PASSWORD))

def fetch_metric(resource_type, parent_id=None):
    """Fetch metrics from MarkLogic using the Client."""
    try:
        path = f"/manage/v2/{resource_type}"
        print(f"\nFetching {resource_type} metrics...")
        
        # Get metrics with proper datetime
        end_time = datetime.utcnow().isoformat() + 'Z'
        start_time = (datetime.utcnow().replace(minute=0, second=0, microsecond=0)).isoformat() + 'Z'
        
        # Print full URL for debugging
        metrics_url = (f"{MARKLOGIC_MANAGE_HOST}/manage/v2/{resource_type}?"
                      f"format=json&view=metrics&"
                      f"start={start_time}&end={end_time}&period=hour")
        print(f"Metrics URL: {metrics_url}")
        
        # Get the metrics directly
        metrics_response = manage_client.get(
            path,
            params={
                'format': 'json',
                'view': 'metrics',
                'start': start_time,
                'end': end_time,
                'period': 'hour'
            },
            headers={'Accept': 'application/json'}
        )
        
        if metrics_response.status_code == 200:
            metrics_data = metrics_response.json()
            
            # Only get host name for host metrics
            if resource_type == 'hosts':
                host_response = manage_client.get(
                    path,
                    params={'format': 'json'},
                    headers={'Accept': 'application/json'}
                )
                
                if host_response.status_code == 200:
                    host_data = host_response.json()
                    try:
                        host_items = host_data['host-default-list']['list-items']['list-item']
                        if host_items:
                            host_name = host_items[0].get('nameref')
                            print(f"Found host: {host_name}")
                            metrics_data['host_name'] = host_name
                    except (KeyError, IndexError) as e:
                        print(f"Error getting host name: {e}")
            
            return metrics_data
            
        else:
            print(f"Error getting metrics: {metrics_response.text}")
            return None
            
    except Exception as e:
        print(f"Error fetching metrics: {str(e)}")
        traceback.print_exc()
        return None

def collect_host_metrics(callback_options):
    """Collect all available MarkLogic host metrics."""
    data = fetch_metric('hosts')
    if data:
        metrics_list = data.get('host-metrics-list', {})
        if 'metrics-relations' in metrics_list:
            relations = metrics_list['metrics-relations']
            metrics = relations['host-metrics-list'].get('metrics', [])
            host_name = data.get('host_name', 'unknown')
            
            metric_count = 0
            for metric_obj in metrics:
                for metric_name, metric_info in metric_obj.items():
                    try:
                        value = float(metric_info.get('value', 0))
                        observation = Observation(
                            value=value,
                            attributes={
                                "source": "host",
                                "host": host_name,
                                "metric_name": metric_name,
                                "unit": metric_info.get('units', '1')
                            }
                        )
                        metric_count += 1
                        yield observation
                    except (ValueError, TypeError) as e:
                        print(f"Error with metric {metric_name}: {e}")
            print(f"Collected {metric_count} host metrics")

def collect_database_metrics(callback_options):
    """Collect all available MarkLogic database metrics."""
    data = fetch_metric('databases')
    if data:
        metrics_list = data.get('database-metrics-list', {})
        if 'metrics-relations' in metrics_list:
            relations = metrics_list['metrics-relations']
            metrics = relations['database-metrics-list'].get('metrics', [])
            
            metric_count = 0
            for metric_group in metrics:
                # Handle master metrics
                if 'master' in metric_group:
                    for metric_obj in metric_group['master']:
                        for metric_name, metric_info in metric_obj.items():
                            try:
                                # Get the value from the first entry
                                entries = metric_info.get('summary', {}).get('data', {}).get('entry', [])
                                if entries:
                                    value = float(entries[0].get('value', 0))
                                    observation = Observation(
                                        value=value,
                                        attributes={
                                            "source": "database",
                                            "metric_name": metric_name,
                                            "unit": metric_info.get('units', '1'),
                                            "type": "master"
                                        }
                                    )
                                    metric_count += 1
                                    yield observation
                            except (ValueError, TypeError, IndexError) as e:
                                print(f"Error with metric {metric_name}: {e}")
            
            print(f"Collected {metric_count} database metrics")

# Now configure OpenTelemetry
print("Configuring OpenTelemetry with Honeycomb...")
honeycomb_exporter = OTLPMetricExporter(
    endpoint="https://api.honeycomb.io/v1/metrics",
    headers={
        "x-honeycomb-team": HONEYCOMB_API_KEY,
        "x-honeycomb-dataset": HONEYCOMB_DATASET,
    },
)

# Configure readers with shorter intervals for testing
print("Setting up metric readers...")
honeycomb_reader = PeriodicExportingMetricReader(
    honeycomb_exporter,
    export_interval_millis=5000  # Export every 5 seconds
)

# Add a custom console exporter that's more verbose
class VerboseConsoleMetricExporter(ConsoleMetricExporter):
    def export(self, metrics_data, **kwargs):
        print("\n=== Metric Export ===")
        try:
            for resource_metrics in metrics_data.resource_metrics:
                for scope_metrics in resource_metrics.scope_metrics:
                    for metric in scope_metrics.metrics:
                        for point in metric.data.data_points:
                            # Only print the source, metric name, and value
                            source = point.attributes.get('source', 'unknown')
                            metric_name = point.attributes.get('metric_name', 'unknown')
                            value = point.value
                            print(f"{source}: {metric_name} = {value}")
        except Exception as e:
            print(f"Error in metric export: {e}")
        return True  # Skip parent class export to avoid metadata output

# Update the console reader to use the verbose exporter
console_reader = PeriodicExportingMetricReader(
    VerboseConsoleMetricExporter(),
    export_interval_millis=5000  # Export every 5 seconds
)

# Update meter provider configuration
print("Initializing meter provider...")
resource = Resource.create({
    "service.name": "marklogic-metrics",
    "service.version": "1.0.0",
    "host.name": "marklogic-host"
})

meter_provider = MeterProvider(
    resource=resource,
    metric_readers=[honeycomb_reader, console_reader],
)

# Force metrics to be synchronous for testing
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter(__name__, schema_url="https://opentelemetry.io/schemas/1.9.0")

print("Defining metrics...")
host_metrics = meter.create_observable_gauge(
    name="marklogic.host.metrics",
    description="All MarkLogic host metrics",
    unit="1",
    callbacks=[collect_host_metrics]
)

database_metrics = meter.create_observable_gauge(
    name="marklogic.database.metrics",
    description="All MarkLogic database metrics",
    unit="1",
    callbacks=[collect_database_metrics]
)

def main():
    print("\n=== Starting MarkLogic Metrics Collection ===")
    
    try:
        while True:
            print(f"\n=== Collection Cycle at {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
            
            # For debugging only - collect and print metrics
            host_metrics_list = list(collect_host_metrics(None))
            print(f"Collected {len(host_metrics_list)} host metrics")
            
            db_metrics_list = list(collect_database_metrics(None))
            print(f"Collected {len(db_metrics_list)} database metrics")
            
            # Force export
            honeycomb_reader.force_flush()
            console_reader.force_flush()
            
            # Wait before next collection
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\nStopping metrics collection...")
        honeycomb_reader.force_flush()
        console_reader.force_flush()
    except Exception as e:
        print(f"\nUnexpected error: {type(e).__name__}")
        print(f"Error details: {str(e)}")
        raise

if __name__ == "__main__":
    main()

