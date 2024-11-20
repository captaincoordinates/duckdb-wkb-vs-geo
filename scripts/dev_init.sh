#!/bin/bash

set -e

pushd $(dirname $0)/..

pip install -r src/generate/requirements.txt
