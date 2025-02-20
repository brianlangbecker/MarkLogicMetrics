# MarkLogic Log Collector

Collects MarkLogic logs and exports them to Honeycomb using OpenTelemetry Collector.

## Setup

1. Download and install the OpenTelemetry Collector Contrib from the [official releases page](https://github.com/open-telemetry/opentelemetry-collector-releases/releases)

   - Look for the latest `otelcol-contrib` release
   - The contrib version is required for the filelog receiver
   - After downloading, make the binary executable:
     ```bash
     chmod 755 otelcol-contrib
     ```

2. Configure collector.yml:

   - Update log file path in `include: [ logs/*log.txt ]`
   - Set your Honeycomb API key
   - Set your Honeycomb dataset name
   - To collect existing logs, uncomment:
     ```yaml
     # start_at: beginning
     ```

3. Start the collector:
   ```bash
   ./otelcol-contrib --config collector.yml
   ```

## Test Log Generation

**Note:** Log dates must be within the last 60 days and in UTC timezone for Honeycomb to accept them.

### Single Line Log:

```bash
# Current UTC date minus 1 hour
echo '$(date -u -v-1H "+%Y-%m-%d %H:%M:%S").001 Info: Script: wco-admin cleanup-expired-sessions' >> logs/logfile.log.txt
```

### Multiline Log:

```bash
# Current UTC date minus 1 hour
timestamp=$(date -u -v-24H "+%Y-%m-%d %H:%M:%S")
echo "$timestamp.753 Notice: XDMP-ZIPDUPNAME: Error message
$timestamp.753 Notice:+ Stack trace line 1
$timestamp.753 Notice:+ Stack trace line 2" >> logs/logfile.log.txt
```

### Full Test Suite:

To run a comprehensive test with various log patterns:

```bash
chmod 755 test-script.sh
./test-script.sh >> logs/logfile.log.txt
```

**Note:** The test script is configured for macOS. For Linux or other operating systems, you'll need to modify the `date` commands in the script. On Linux, replace:

```bash
date -j -f %s $timestamp
```

with:

```bash
date -u -d "@$timestamp"
```

This will generate a variety of test log entries in the logfile.log.txt file for testing the collector's parsing capabilities.

## Troubleshooting

- Check file paths in collector.yml
- Verify Honeycomb credentials
- For historical logs, enable `start_at: beginning`
- Check console output for parsing errors
- Ensure log dates are within the last 60 days and in UTC timezone
