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
HONEYCOMB_API_KEY = "YOUR_HONEYCOMB_API_KEY"
HONEYCOMB_DATASET = "MarkLogicMetrics"

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
        
        # First get the host name
        host_response = manage_client.get(
            path,
            params={'format': 'json'},
            headers={'Accept': 'application/json'}
        )
        
        if host_response.status_code != 200:
            print(f"Error getting host info: {host_response.text}")
            return None
            
        host_data = host_response.json()
        host_name = None
        try:
            host_items = host_data['host-default-list']['list-items']['list-item']
            if host_items:
                host_name = host_items[0].get('nameref')
                print(f"Found host: {host_name}")
        except (KeyError, IndexError) as e:
            print(f"Error getting host name: {e}")
            return None
        
        # Now get the metrics
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
            
            metrics_list = metrics_data.get('host-metrics-list', {})
            
            if 'metrics-relations' in metrics_list:
                relations = metrics_list['metrics-relations']
                metrics = relations['host-metrics-list'].get('metrics', [])
                print(f"Found {len(metrics)} metrics")
                # Print first 3 metrics found
                print("First 3 metrics found:")
                for i, metric_obj in enumerate(metrics[:3]):
                    for metric_name, metric_info in metric_obj.items():
                        print(f"  {metric_name}")
                
                # Create status data from metrics
                status_data = {}
                for metric_obj in metrics:
                    for metric_name, metric_info in metric_obj.items():
                        if 'summary' in metric_info and metric_info['summary']:
                            summary = metric_info['summary']
                            if 'data' in summary and 'entry' in summary['data']:
                                entries = summary['data']['entry']
                                if entries:
                                    latest_entry = entries[-1]
                                    value = latest_entry.get('value', 0)
                                    status_data[metric_name] = value
                
                # Create a data structure that matches the default view
                data = {
                    'host-default-list': {
                        'list-items': {
                            'list-item': [{
                                'nameref': host_name,
                                'status': status_data
                            }]
                        }
                    }
                }
                
                # Print first 3 metrics added
                print("\nFirst 3 metrics added to host:")
                for i, (metric_name, value) in enumerate(list(status_data.items())[:3]):
                    print(f"  {metric_name}: {value}")
                
                print(f"Added {len(status_data)} metrics to host: {host_name}")
                return data
            
        else:
            print(f"Error response: {metrics_response.text}")
            return None
            
    except Exception as e:
        print(f"Error fetching metrics: {str(e)}")
        print(f"Full traceback:", traceback.format_exc())
        return None

def collect_node_cpu_usage(callback_options):
    """Collect all available MarkLogic host metrics."""
    print("\nStarting metric collection...")
    
    # Get metrics data once
    data = fetch_metric('hosts')
    if data and 'host-default-list' in data:
        items = data['host-default-list']['list-items'].get('list-item', [])
        for item in items:
            host_name = item.get('nameref', 'unknown')
            if 'status' in item:
                status = item['status']
                # Collect all available metrics
                for metric_name, value in status.items():
                    try:
                        value = float(value)  # Convert to float
                        # Create proper Observation object
                        observation = Observation(
                            value=value,
                            attributes={
                                "host": host_name,
                                "metric_name": metric_name,
                                "unit": "1"
                            }
                        )
                        yield observation
                        print(f"Added observation for {metric_name}: {value}")
                    except (ValueError, TypeError) as e:
                        print(f"Skipping metric {metric_name}: {e}")

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
        print("\n================================ Console Metric Export ===")
        print(f"Exporting {len(metrics_data.resource_metrics)} resource metrics")
        for resource_metrics in metrics_data.resource_metrics:
            print(f"\nResource attributes: {resource_metrics.resource.attributes}")
            for scope_metrics in resource_metrics.scope_metrics:
                for metric in scope_metrics.metrics:
                    print(f"\nMetric: {metric.name}")
                    try:
                        for point in metric.data.data_points:
                            print(f"  Value: {point.value}")
                            print(f"  Attributes: {point.attributes}")
                            print(f"  Timestamp: {point.timestamp}")
                    except Exception as e:
                        print(f"Error processing metric point: {e}")
        return super().export(metrics_data, **kwargs)

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
    "host.name": "marklogic-host"  # Add host identifier
})

meter_provider = MeterProvider(
    resource=resource,
    metric_readers=[honeycomb_reader, console_reader],
)

# Force metrics to be synchronous for testing
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter(__name__, schema_url="https://opentelemetry.io/schemas/1.9.0")

print("Defining metrics...")
node_metrics = meter.create_observable_gauge(
    name="marklogic.host.metrics",  # Changed to plural
    description="All MarkLogic host metrics",
    unit="1",
    callbacks=[collect_node_cpu_usage]
)

def main():
    print("\n=== Starting MarkLogic Host Metrics Collection ===")
    
    try:
        while True:
            print(f"\n=== Collection Cycle at {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
            
            # Force metric collection and export
            metrics_list = list(collect_node_cpu_usage(None))
            print(f"Collected {len(metrics_list)} metrics")
            
            # Explicitly observe each metric
            for observation in metrics_list:
                node_metrics.observe(observation.value, observation.attributes)
            
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

