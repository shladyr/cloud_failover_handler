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
