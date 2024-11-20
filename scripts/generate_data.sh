#!/bin/bash

set -e

pushd $(dirname $0)/..

docker run \
    --rm \
    -v $PWD/output:/output:rw \
    -v $PWD/src:/src:ro \
    python:3.12-slim \
    python /src/generate_data.py
