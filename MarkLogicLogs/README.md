# README

This document is designed to guide the process of loading MarkLogic logs into Honeycomb.

## How to Start the Collector

To start the collector, use the following command:

```bash
otelcol --config collector.yml
```

## Pointing to the `collector.yml` File

Ensure the `collector.yml` configuration file is located in your current working directory or specify its full path when starting the collector. For example:

```bash
otelcol --config /path/to/collector.yml
```

## How to Test by Downloading a Local Collector

1. Download the OpenTelemetry Collector binary from the [official releases page](https://github.com/open-telemetry/opentelemetry-collector-releases).

2. Extract the downloaded file:

   ```bash
   tar -xvzf otelcol_<version>_<platform>.tar.gz
   cd otelcol_<version>_<platform>
   ```

3. Verify the collector is working by running:

   ```bash
   ./otelcol --version
   ```

4. Start the collector with your configuration:

   ```bash
   ./otelcol --config collector.yml
   ```

5. Test Logging Output
   The following commands will produce logging output for testing purposes:

### Single Line Echo:

```bash
echo '2025-01-27 12:33:00.001 Info: Script: wco-admin cleanup-expired-sessions' >> logfile.log
```

### Multiline Echo:

```bash
echo "2025-01-23 09:26:17.753 Notice: XDMP-ZIPDUPNAME: xdmp:zip-create(<parts xmlns=\"xdmp:zip\"><part>Bill of Sale_.docx</part><part>Bill...</part>...</parts>, (fn:doc(\"/practices/2898207634023500640/client-intake/823783237863574986/attachments/property_bankaccount_documents/Bill of Sale.docx\"), fn:doc(\"/practices/2898207634023500640/client-intake/823783237863574986/attachments/additionaldocs_question/Bill of Sale.docx\"), fn:doc(\"/practices/2898207634023500640/client-intake/823783237863574986/attachments/property_realproperty_documents/Bill of Sale.docx\"))) -- Duplicate names not allowed in zip files: Bill of Sale_.docx
2025-01-23 09:26:17.753 Notice:+in /api/client-intake/file-download.xqy, at 44:4 [1.0-ml]
2025-01-23 09:26:17.753 Notice:+ \$intake-id = \"823783237863574986\"
2025-01-23 09:26:17.753 Notice:+ \$question-id = ()
2025-01-23 09:26:17.753 Notice:+ \$file-name = ()
2025-01-23 09:26:17.753 Notice:+ \$part = \"all\"
2025-01-23 09:26:17.753 Notice:+ \$root = \"/practices/2898207634023500640/client-intake/823783237863574986/...\"
2025-01-23 09:26:17.753 Notice:+ \$uris = (\"/practices/2898207634023500640/client-intake/823783237863574986/...\", \"/practices/2898207634023500640/client-intake/823783237863574986/...\", \"/practices/2898207634023500640/client-intake/823783237863574986/...\")
2025-01-23 09:26:17.753 Notice:+ \$names = map:map(<map:map xmlns:xs=\"http://www.w3.org/2001/XMLSchema\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" .../>)
2025-01-23 09:26:17.753 Notice:+ \$map = map:map(<map:map xmlns:xs=\"http://www.w3.org/2001/XMLSchema\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" .../>)
2025-01-23 09:26:17.753 Notice:+ \$dw-fact = ()" >> logfile.log
```
