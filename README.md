# Loadhouse

A powerful ETL (Extract, Transform, Load) tool designed for data lakehouse architectures with JSON-based configuration.

## Overview

Loadhouse is a flexible data processing tool that simplifies ETL operations through JSON configuration. It supports various data sources and provides robust data transformation capabilities using Apache Spark.

## Features

- **Configurable Data Sources**
  - File-based (CSV, Delta, etc.)
  - JDBC connections
  - SQL queries
  - DataFrame operations

- **Data Transformations**
  - Expression filtering
  - Custom transformations
  - Data quality validation

- **Multiple Output Formats**
  - Delta Lake
  - File formats (CSV, Parquet, etc.)
  - Console output for debugging
- **Quality Checker**
  - Data quality patterns with Apache Airflow
  - Unit test Spark
  - Data validation with GX