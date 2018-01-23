#!/bin/sh

HOST=$1
TOKEN=$2

curl -H "x-auth-token: ${TOKEN}" ${HOST}/placement/resource_providers > resource_providers.json
