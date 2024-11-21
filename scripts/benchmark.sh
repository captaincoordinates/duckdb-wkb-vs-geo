#!/bin/bash

set -e

pushd $(dirname $0)/..

image_name=captaincoordinates/duckdb-wkb-vs-geo-benchmark

docker build \
    -t $image_name \
    -f docker/benchmark/dockerfile \
    .

docker run \
    --rm \
    -v $PWD/output:/parquet:ro \
    -e DDB_BENCH_PATH_PREFIX \
    $image_name \
    python /app/benchmark.py
