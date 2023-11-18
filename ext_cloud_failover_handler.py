#!/usr/bin/env python3
import argparse
import hashlib
import itertools
import logging
import os
import requests
import speedtest
import time
import urllib3
from datetime import datetime, timedelta

parser = argparse.ArgumentParser(description='Switch Ext Cloud Region via cli')
parser.add_argument('-r', '--region', help='[Required] Ext Cloud Region.', default=None, required=False)
args = parser.parse_args()

test_org_id = os.environ.get("CONNECTION_KEEPALIVE_ORG_ID")
test_tx_id = os.environ.get("CONNECTION_KEEPALIVE_TXN_ID")
ext_url = "https://localhost:8443/v2/{0}/cloudlookup/{1}".format(test_org_id, test_tx_id)
ext_clouds_failover_list_os = os.environ.get("EXT_CLOUD_FAILOVER_LIST").split(",")


logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp" : "%(asctime)s","level" : "%(levelname)s","service" : "ext_cloud_outage_handler","message":"%(message)s"}'
)

# Switch to another default Ext Cloud from command line
print(f'\nThe default list of Ext Clouds is next: {ext_clouds_failover_list_os}')
print(f'\nThe next primary Ext Region will be as --region={args.region}')


def ext_clouds_failover_list(region):
    nam = 'NAM=cloud.nam.ext.com'
    eu = 'EU=cloud.eu.ext.com'
    apac = 'APAC=cloud.apac.ext.com'
    ext_clouds_failover_list = os.environ.get("EXT_CLOUD_FAILOVER_LIST").split(",")
    if (region):
        if (region == 'NAM'):
            ext_clouds_failover_list = [nam, eu, apac]
            return ext_clouds_failover_list
        elif (region == 'EU'):
            ext_clouds_failover_list = [eu, nam, apac]
            return ext_clouds_failover_list
        elif (region == 'APAC'):
            ext_clouds_failover_list = [apac, nam, eu]
            return ext_clouds_failover_list
        else:
            return ext_clouds_failover_list
    else:
        return ext_clouds_failover_list

print(f'\nYou are switching to the next list of Ext Clouds: {ext_clouds_failover_list(args.region)}')

def check_ext_cloud_availability():
    try:
        logging.info("Attempt to reach out to Ext Cloud via localhost:8443")
        urllib3.disable_warnings()
        sha256 = hashlib.sha256().hexdigest()
        headers = {"X-SIG-Sha256": sha256}
        result = requests.get(url=ext_url, headers=headers, timeout=20, verify=False)
        if result.status_code != 200:
            logging.error("Error happened during Ext Cloud health check")
            return False
        return True
    except requests.exceptions.Timeout:
        logging.exception("Cannot curl cloudlookup endpoint, cannot determine EXT cloud availability")
        return False
    except Exception as e:
        logging.exception("Cannot curl cloudlookup endpoint, cannot determine EXT cloud availability")
        return True


def check_network_latency():
    try:
        logging.info("Start Network Latency checking via speedtest")
        threads = None
        # default timeout = 10 sec
        speed_test = speedtest.Speedtest()
        # get result in bit/s and convert to mbits/s
        latency_result = speed_test.download(threads=threads) * 0.000001
        logging.info(f'Network Latency is {int(latency_result)} Mbit/s')

        # Writing Network Latency to file
        file_path = "/tmp/latency.txt"
        print(f'\nWriting Network Latency into linux file: {file_path}\n')
        with open(file_path, 'w') as f:
            f.write(str(int(latency_result)))
            f.close()

        print(f'\nSpeedtest successful or not ? isinstance() =  {isinstance(latency_result, (int, float))}\n')
        if not isinstance(latency_result, (int, float)):
            print(f'\nSpeedtest successful or not ? isinstance() =  {isinstance(latency_result, (int, float))}\n')
            raise Exception('Speedtest-cli failure.')
        return int(latency_result)
    except Exception as e:
        logging.exception("Cannot speedtest, cannot measure network Latency. %s", e)


def restart_application():
    os.system('supervisorctl stop app:application')
    os.system('supervisorctl stop app:cloud-client')
    os.system('supervisorctl stop app:stunnel')
    os.system('supervisorctl start app:stunnel')
    os.system('supervisorctl start app:cloud-client')
    os.system('supervisorctl start app:application')


def write_ext_cloud_to_file(ext_cloud, ext_region):
    with open('/opt/application/tmp/ext_cloud.env', 'w') as cloud_file:
        cloud_file.write("export EXT_CLOUD={0}\n".format(ext_cloud))
        cloud_file.write("export EXT_REGION={0}".format(ext_region))


for cloud in itertools.cycle(ext_clouds_failover_list(args.region)):
    ext_region, ext_cloud = cloud.split('=')
    write_ext_cloud_to_file(ext_cloud, ext_region)
    logging.warning("Re-starting application with the new region {0} and cloud {1}.".format(ext_region, ext_cloud))
    restart_application()
    first_failure_time = None
    while True:
        latency_result = check_network_latency()
        logging.info("while True: Initial Network Latency is {0} Mbit/s".format(latency_result))
        if latency_result and latency_result < 100:
            logging.warning(
                "Network Latency is CRITICAL - {0}Mbit/s! Waiting for additional 60 sec before Ext Cloud checking".format(
                    latency_result))
            time.sleep(60)
        logging.info("Waiting for regular 15 sec before Ext Cloud Availability checking")
        time.sleep(15)  # Frequency of health checks
        result = check_ext_cloud_availability()
        logging.info("Ext cloud is available: {0}".format(result))
        if not result:
            if first_failure_time is None:
                first_failure_time = datetime.now()
                logging.error("!!!!!!!!!! FAILURE_TIME {0} - connecting to {1}".format(first_failure_time, ext_cloud))
            if (datetime.now() - timedelta(minutes=4)) > first_failure_time:
                # The next message is used by DataDog log-based monitor "Ext Cloud Switching event"
                logging.warning(
                    "Waited for 4 min. Application restarting due to failure with Ext Cloud: {0}".format(ext_cloud))
                break
        else:
            first_failure_time = None