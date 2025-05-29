#!/bin/bash

cd "$DAGSTER_HOME"

mkdir .dagster_home

DAGSTER_HOME="$(pwd)/.dagster_home"

export DAGSTER_HOME

dagster dev -m aemo_etl.definitions -h 0.0.0.0
