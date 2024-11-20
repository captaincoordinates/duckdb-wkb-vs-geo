#!/bin/bash

set -e

pushd $(dirname $0)/..

image_name_100=captaincoordinates/duckdb-wkb-vs-geo-generate-100
image_name_113=captaincoordinates/duckdb-wkb-vs-geo-generate-113

docker build \
    -t $image_name_100 \
    -f docker/generate/dockerfile.100 \
    .
docker build \
    -t $image_name_113 \
    -f docker/generate/dockerfile.113 \
    .

docker run \
    --rm \
    -v $PWD/output:/output:rw \
    -v $PWD/.cache:/app/.cache:rw \
    $image_name_100 \
    python /app/generate.py
docker run \
    --rm \
    -v $PWD/output:/output:rw \
    -v $PWD/.cache:/app/.cache:rw \
    $image_name_113 \
    python /app/generate.py
