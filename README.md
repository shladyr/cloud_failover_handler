# External Cloud Failover Handler

## Overview

This Python script is designed to handle External Cloud outages by implementing a failover mechanism. 
It checks the availability of the External Cloud by making requests to a specified cloudlookup endpoint. 
If an outage is detected, the script performs a failover to a backup External Cloud region.

## Prerequisites

- Python 3.9 or later
- Required Python packages can be installed using the command:

  ```bash
  pip install -r requirements.txt
  ```

# Usage

Command Line Arguments
The script accepts the following command line arguments:
`-r` or `--region`: Ext Cloud Region (default: None). Specify the Ext Cloud region to be used for the failover.
Example:
```commandline
/usr/local/bin/external_cloud_failover_handler.py --region EU
```

# Environment Variables
`EXT_CLOUD_FAILOVER_LIST`: Set this environment variable with a comma-separated list of Ext Cloud regions for failover.

# Configuration
The failover behavior is defined in the ext_clouds_failover_list function. 
It returns a list of Ext Cloud regions in the preferred failover order based on the provided region argument.

# Logging
The script uses the logging module to provide detailed logs in JSON format. 
Log messages include a timestamp, log level, service name, and the log message itself.

# Failover Logic
The failover logic is implemented in the check_ext_cloud_availability function. 
If an Ext Cloud outage is detected, the script attempts to restart the application after a specified timeout.

# File Output
The script writes the selected Ext Cloud and region to the file /opt/application/tmp/ext_cloud.env using the write_ext_cloud_to_file function.

# Restarting the Application
The `restart_application` function stops and then restarts the App application components to get new value from file `/opt/application/tmp/ext_cloud.env`.

# Notes
The script is configured to run indefinitely, checking Ext Cloud availability every 10 seconds.
The failover threshold is set to 4 minutes. If the script detects a continuous outage for 4 minutes, it triggers a restart of the application.
Make sure to review and adjust the script according to your specific environment and requirements.