# MarkLogic Log Collector

Collects MarkLogic logs and exports them to Honeycomb using OpenTelemetry Collector. Installing this directly on the MarkLogic AMI is not recommended due to dependency issues. It best to install this on a separate small EC2 instance.

- Python 3.7 or higher
- pip (latest version)

## Setup

1. Install Python (if not already installed):

   On Amazon Linux:

   ```bash
   # Install development tools
   sudo yum groupinstall "Development Tools"

   # Install Python and development headers
   sudo amazon-linux-extras install python3
   sudo yum install python3-devel
   ```

2. Create and activate a Python virtual environment:

   ```bash
   # Create virtual environment
   python3 -m venv venv

   # Activate virtual environment
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip3 install --upgrade pip
   pip3 install -r requirements.txt
   ```

4. Create a .env file with your credentials:

   ```bash
   # Create and edit .env file
   cp .env.example .env
   vi .env
   ```

   Update the following variables:

   ```
   MARKLOGIC_MANAGE_HOST=http://localhost:8002
   MARKLOGIC_USERNAME=your_username
   MARKLOGIC_PASSWORD=your_password
   HONEYCOMB_API_KEY=your_api_key
   HONEYCOMB_DATASET=your_dataset
   ```

5. Run the collector:

   ```bash
   python3 marklogic_honeycomb_metrics.py
   ```

## License

MIT
