import os, sys, config

# Force sys.path to have our own directory first, so we can import from it.
sys.path.insert(0, config.APP_ROOT_DIR)
sys.path.insert(1, os.path.join(config.APP_ROOT_DIR, 'external'))

import boto.ec2
import math

# The bootstrap script.
# It starts a simple Python HTTP server to serve static files.
# It shuts the machine down automatically after 45 minutes.
BOOTSTRAP_SCRIPT = """#!/bin/bash
umask 077
mkdir /mnt/data
chmod 700 /mnt/data
cd /mnt/data
echo `hostname` > info
echo %(REGION)s >> info
python -m SimpleHTTPServer 8080
/sbin/shutdown -P +45 &
"""

# The default AMI is Ubuntu 12.04.2 64-bit instance store.
REGIONS = [
        {'name': 'us-west-1', 'city': 'Northern California',
            'ami': 'ami-72072e37', 'lat': 36.4885, 'long': -119.7014},
        {'name': 'us-east-1', 'city': 'Northern Virginia',
            'ami': 'ami-d9d6a6b0', 'lat': 37.6666, 'long': -78.6146},
        {'name': 'us-west-2', 'city': 'Oregon',
            'ami': 'ami-5168f861', 'lat': 45.5236, 'long': -122.6750},
        {'name': 'sa-east-1', 'city': 'Sao Paulo',
            'ami': 'ami-027edb1f', 'lat': -23.5000, 'long': -46.6167},
        {'name': 'eu-west-1', 'city': 'Ireland',
            'ami': 'ami-57b0a223', 'lat': 53.0000, 'long': -7.0000},
        {'name': 'ap-southeast-1', 'city': 'Singapore',
            'ami': 'ami-b02f66e2', 'lat': 1.3667, 'long': 103.7500},
        {'name': 'ap-southeast-2', 'city': 'Sydney',
            'ami': 'ami-934ddea9', 'lat': -33.8683, 'long': 151.2086},
        {'name': 'ap-northeast-1', 'city': 'Tokyo',
            'ami': 'ami-7d1d977c', 'lat': 35.6833, 'long': 139.7667},
        ]

# Method to calculate the distance between two coordinates (haversine formula).
def _haversine_distance(location1, location2):
    lat1, long1 = location1
    lat2, long2 = location2
    earth = 6371 # The earth's radius in kms.

    dlat = math.radians(lat2-lat1)
    dlong = math.radians(long2-long1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlong/2) * math.sin(dlong/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = earth * c
    return d

def closest_region(lati, longi):
    shortest =  float('inf') # Infinity.
    closest = REGIONS[0] # Default region.
    for region in REGIONS:
        location1 = (lati, longi)
        location2 = (region['lat'], region['long'])
        distance = _haversine_distance(location1, location2)
        if distance < shortest:
            shortest = distance
            closest = region
    return closest

def count_instances(region, state):
    conn = boto.ec2.connect_to_region(region['name'], aws_access_key_id=config.AWS_ACCESS_KEY, aws_secret_access_key=config.AWS_SECRET_KEY)
    filters = {'tag:server_type': 'mako-mori', 'instance-state-name': state}
    reservations = conn.get_all_instances(filters=filters)
    instances = [i for r in reservations for i in r.instances]
    count = len(instances)
    return count

def create_an_instance(region):
    conn = boto.ec2.connect_to_region(region['name'], aws_access_key_id=config.AWS_ACCESS_KEY, aws_secret_access_key=config.AWS_SECRET_KEY)
    images = conn.get_all_images(image_ids=[region['ami']])
    image = images[0]
    user_data = BOOTSTRAP_SCRIPT % {'REGION': region['name']}
    key_name = 'mako-mori'
    security_group = 'mako-mori'
    instance_type = 'm1.small'
    tag_type = 'mako-mori'

    reservation = image.run(key_name=key_name, security_groups=[security_group], instance_type=instance_type, user_data=user_data)
    instance = reservation.instances[0]
    instance.add_tag('server_type', tag_type)

def get_an_instance_dns(region):
    conn = boto.ec2.connect_to_region(region['name'], aws_access_key_id=config.AWS_ACCESS_KEY, aws_secret_access_key=config.AWS_SECRET_KEY)
    filters = {'tag:server_type': 'mako-mori', 'instance-state-name': 'running'}
    reservations = conn.get_all_instances(filters=filters)
    instances = [i for r in reservations for i in r.instances]
    instance = instances[0]
    return instance.public_dns_name

def get_status():
    results = []
    for region in REGIONS:
        pending = count_instances(region, 'pending')
        running = count_instances(region, 'running')
        result = {}
        result['name'] = region['name']
        result['city'] = region['city']
        result['pending'] = pending
        result['running'] = running
        results.append(result)
    return results
