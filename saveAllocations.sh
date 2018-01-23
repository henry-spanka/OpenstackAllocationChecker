#!/bin/sh

HOST=$1
TOKEN=$2
RESOURCE=$3

curl -H "x-auth-token: ${TOKEN}" ${HOST}/placement/resource_providers/${RESOURCE}/allocations > allocation_${RESOURCE}.json
