#!/bin/bash

set -e

pushd $(dirname $0)/..

image_name=captaincoordinates/duckdb-wkb-vs-geo-generate

docker build \
    -t $image_name \
    -f docker/generate/Dockerfile \
    .

docker run \
    --rm \
    -v $PWD/output:/output:rw \
    $image_name \
    python /app.py
