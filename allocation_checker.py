#!/usr/bin/python
#
# Check Placement Allocations
#
# Copyright (C) 2018 Henry Spanka
#
# Authors:
#  Henry Spanka <henry@myvirtualserver.de>
#
# This work is licensed under the terms of the GNU GPL, version 2.  See
# the COPYING file in the root directory.

import argparse
import os
import sys
import dumper
from classes.credentials import Credentials
from classes.nova import Nova
from datetime import datetime
import time
import json

def checkEnvExists(name):
    if os.environ.get(name) is None:
        displayMessage('error', "Error: Environment variable %s not set." % name)
        sys.exit(1)

def displayMessage(level, message):
    date = datetime.now()
    print date.strftime('%Y-%m-%d %H:%M:%S - ') + level.upper() + ': ' + message

def fixSuggestion(consumer_id, used, resource_class_id):
    return ('update allocations set used = \'{}\' where consumer_id = \'{}\' and resource_class_id = \'{}\';'
        .format(used, consumer_id, resource_class_id))

def main():
    parser = argparse.ArgumentParser(description='OpenStack Allocation Checker')

    displayMessage('info', 'Starting OpenStack Allocation Checker')

    for env in ['OS_AUTH_URL', 'OS_PROJECT_ID', 'OS_USERNAME',
    'OS_PASSWORD', 'OS_REGION_NAME', 'OS_USER_DOMAIN_NAME']:
        checkEnvExists(env)

    json_data = ''

    for line in sys.stdin:
        json_data += line

    if not json_data:
        displayMessage('error', "Error: no json data provided")
        sys.exit(1)

    auth_url = os.environ.get('OS_AUTH_URL')
    project_id = os.environ.get('OS_PROJECT_ID')
    username = os.environ.get('OS_USERNAME')
    password = os.environ.get('OS_PASSWORD')
    user_domain_name = os.environ.get('OS_USER_DOMAIN_NAME')

    credentials = Credentials(auth_url=auth_url,
                              username=username,
                              password=password,
                              project_id=project_id,
                              user_domain_name=user_domain_name)

    nova = Nova(credentials)

    allocations = json.loads(json_data)['allocations']

    sqlFixCommands = []

    for instance in allocations:
        allocation = allocations[instance]

        vCPU = allocation['resources']['VCPU']
        memory_mb = allocation['resources']['MEMORY_MB']
        disk_gb = allocation['resources']['DISK_GB']

        server = nova.getServer(instance)

        flavor_id = server.flavor['id']

        flavor = nova.getFlavor(flavor_id)

        vCPU_flavor = flavor.vcpus
        memory_mb_flavor = flavor.ram
        disk_gb_flavor = flavor.disk

        inconsistent = False

        if vCPU != vCPU_flavor:
            displayMessage('warning', 'instance {} vCPU inconsistent: {}/{} (allocated/real)'.format(instance, vCPU, vCPU_flavor))
            sqlFixCommands.append(fixSuggestion(instance, vCPU_flavor, '0'))
            inconsistent = True

        if memory_mb != memory_mb_flavor:
            displayMessage('warning', 'instance {} memory inconsistent: {}/{} (allocated/real)'.format(instance, memory_mb, memory_mb_flavor))
            sqlFixCommands.append(fixSuggestion(instance, memory_mb_flavor, '1'))
            inconsistent = True

        if disk_gb != disk_gb_flavor:
            displayMessage('warning', 'instance {} disk inconsistent: {}/{} (allocated/real)'.format(instance, disk_gb, disk_gb_flavor))
            sqlFixCommands.append(fixSuggestion(instance, disk_gb_flavor, '2'))
            inconsistent = True

        if inconsistent:
            displayMessage('warning', 'instance {} is INCONSISTENT'.format(instance))
        else:
            displayMessage('info', 'instance {} is CONSISTENT'.format(instance))

    sqlFixFile = open('sqlFixes.sql', 'w')
    for fix in sqlFixCommands:
        sqlFixFile.write('%s\n' % fix)
    sqlFixFile.close()

    exit(0)

if __name__ == '__main__':
    main()
