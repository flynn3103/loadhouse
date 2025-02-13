SHELL := /bin/bash -euxo pipefail

# Default values for build variables
container_cli := docker
image_name := lakehouse-engine
version := 1.0.0
python_image ?= python:3.11-slim-bullseye
cpu_architecture ?= $(shell uname -m)
group_id ?= $(shell id -g ${USER})

# Spark driver memory configuration
# Example: make test spark_driver_memory=3g
# WARNING: When the tests are being run 2 spark nodes are created, so despite
# the default value being 2g, your configured docker environment should have
# extra memory for communication and overhead.
ifndef spark_driver_memory
	spark_driver_memory := "2g"
endif

.PHONY: build-image terminal

# Verify required variables
verify-variables:
	@if [ -z "$(USER)" ]; then echo "USER is not set"; exit 1; fi

# Build the Docker image
build-image: verify-variables
	$(container_cli) build \
		--build-arg USER_ID=$(shell id -u ${USER}) \
		--build-arg GROUP_ID=$(group_id) \
		--build-arg PYTHON_IMAGE=$(python_image) \
		--build-arg CPU_ARCHITECTURE=$(cpu_architecture) \
		-t $(image_name):$(version) . -f Dockerfile

# Start an interactive terminal in the container
terminal: build-image
	$(container_cli) run \
		-it \
		--rm \
		-w /app \
		-v "$$PWD":/app \
		$(image_name):$(version) \
		/bin/bash


# Start PySpark environment for MacOS M1
pyspark-m1: build-image
	$(container_cli) run \
		-it \
		--rm \
		-w /app \
		-v "$$PWD":/app \
		-e SPARK_DRIVER_MEMORY=$(spark_driver_memory) \
		-e JAVA_HOME=/usr/lib/jvm/temurin-8-jdk-aarch64 \
		-e DOCKER_DEFAULT_PLATFORM=linux/arm64 \
		-p 4040:4040 \
		$(image_name):$(version) \
		python3 -c "from tests.utils.exec_env_helpers import ExecEnvHelpers; ExecEnvHelpers.prepare_exec_env('$(spark_driver_memory)'); from pyspark.sql import SparkSession; spark = SparkSession.getActiveSession(); spark.sparkContext.setLogLevel('INFO'); print('PySpark shell is ready.'); import IPython; IPython.embed()"

