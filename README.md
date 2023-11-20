# External Cloud Failover Handler

## Overview

- This Python script is designed to handle External Cloud outages by implementing a [failover](https://en.wikipedia.org/wiki/Failover) mechanism. 
- It checks the availability of the External Cloud by making requests to a specified cloudlookup endpoint. 
- If an outage is detected, the script performs a failover to a backup External Cloud region.

## Features

- Switch between different Ext Cloud Regions: North America (NAM), Europe (EU), and Asia-Pacific (APAC).
- Send log event to [@DataDogCloud](https://github.com/DataDog) , [Doc](https://docs.datadoghq.com/logs/)
- Perform health checks (with [requests](https://pypi.org/project/requests/)) on the Ext Cloud to ensure [Availability](https://en.wikipedia.org/wiki/Availability).
- Monitor network latency using [speedtest-cli](https://github.com/sivel/speedtest-cli/wiki).
- Automatically restart the APP applications when switching regions (via [Supervisord](https://github.com/Supervisor/supervisor)).
- [Failover](https://en.wikipedia.org/wiki/Failover) mechanism in case of Ext Cloud unavailability.

# Architecture Diagram
![_1_Architecture_Diagram.png](Doc%2F_1_Architecture_Diagram.png)

# Component Diagram
![_2_Component_Diagram.png](Doc%2F_2_Component_Diagram.png)

# Flowchart Diagram
![_3_Flowchart_Diagram.png](Doc%2F_3_Flowchart_Diagram.png)TBD

## Prerequisites

- Python 3.9 or later
- Required Python packages can be installed using the command:

  ```bash
  pip install -r requirements.txt
  ```

# Usage

Command Line Arguments
The script accepts the following command line arguments:
`-r` or `--region`: Ext Cloud Region (default: None). 
Specify the Ext Cloud region to be used for the failover.
Example:
```commandline
/usr/local/bin/external_cloud_failover_handler.py --region EU
```

# Environment Variables
- `EXT_CLOUD_FAILOVER_LIST`: Comma-separated list of Ext Clouds for failover.
- `CONNECTION_KEEPALIVE_ORG_ID`: Organization ID for Ext Cloud connection keep-alive.
- `CONNECTION_KEEPALIVE_TXN_ID`: Transaction ID for Ext Cloud connection keep-alive.

# Configuration
- The failover behavior is defined in the ext_clouds_failover_list function. 
- It returns a list of Ext Cloud regions in the preferred failover order based on the provided region argument.
- The script uses an environment file, ext_cloud.env, located at /opt/application/tmp/, to store the current primary Ext Cloud information.

# Logging
- The script uses the logging module to provide detailed logs in JSON format. 
- Log messages include a timestamp, log level, service name, and the log message itself.
- The script logs events using the logging module, providing information about Ext Cloud switching, network latency, and availability checks.

# Failover Logic
- The failover logic is implemented in the check_ext_cloud_availability function. 
- If an Ext Cloud outage is detected, the script attempts to restart the application after a specified timeout.

# File Output
The script writes the selected Ext Cloud and region to the file /opt/application/tmp/ext_cloud.env using the write_ext_cloud_to_file function.

# Restarting the Application
The `restart_application` function stops and then restarts the App application components to get new value from file `/opt/application/tmp/ext_cloud.env`.

# Notes
- The script is configured to run indefinitely, checking Ext Cloud availability every 10 seconds.
- The failover threshold is set to 4 minutes. If the script detects a continuous outage for 4 minutes, it triggers a restart of the application.
- The script uses the speedtest library to measure network latency. Ensure it is installed (pip install speedtest-cli).
- For security reasons, the script disables SSL verification for the localhost connection to the Ext Cloud. 
- Make sure to review and adjust the script according to your specific environment and requirements.
