#!/bin/bash

set -e

pushd $(dirname $0)/..

image_name_100=captaincoordinates/duckdb-wkb-vs-geo-generate-100
image_name_113=captaincoordinates/duckdb-wkb-vs-geo-generate-113
feature_count=${DDB_BENCH_FEAT_COUNT:-10000000}

docker build \
    -t $image_name_100 \
    -f docker/generate/dockerfile.100 \
    .
docker build \
    -t $image_name_113 \
    -f docker/generate/dockerfile.113 \
    .

echo "generating $feature_count features in 1.0.0"
docker run \
    --rm \
    -v $PWD/output:/output:rw \
    -v $PWD/.cache:/app/.cache:rw \
    -e DDB_BENCH_FEAT_COUNT=$feature_count \
    $image_name_100 \
    python /app/generate.py
echo "generating $feature_count features in 1.1.3"
docker run \
    --rm \
    -v $PWD/output:/output:rw \
    -v $PWD/.cache:/app/.cache:rw \
    -e DDB_BENCH_FEAT_COUNT=$feature_count \
    $image_name_113 \
    python /app/generate.py
