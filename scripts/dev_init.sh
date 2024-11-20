#!/bin/bash

set -e

pushd $(dirname $0)/..

# These deps to support a local IDE in syntax highlighting etc., all execution happens in Docker containers
pip install -r src/requirements_common.txt
pip install -r src/requirements_113.txt

# Enforce pre-commit hook
pip install pre-commit
pre-commit install
