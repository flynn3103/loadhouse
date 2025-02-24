import random
import string
from typing import Optional, OrderedDict

from pyspark.sql import DataFrame
from pyspark.sql.types import StructType

import sys
import os

# Add the parent directory of lakehouse_engine to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# You need to import the Load Data etl config from the Lakehouse Engine, so that you can perform Data Loads.
from lakehouse_engine.engine import load_data

etl_config = {
    "engine": "spark",
    "input_specs": [
        {
            "spec_id": "sales_source",
            "read_type": "batch",
            "data_format": "csv",
            "options": {"header": True, "delimiter": "|", "inferSchema": True},
            "location": "sample/lakehouse/input/part-01.csv",
        }
    ],
    "transform_specs": [
        {
            "spec_id": "filtered_sales",
            "input_id": "sales_source",
            "transformers": [
                {"function": "expression_filter", "args": {"exp": "date like '2016%'"}}
            ],
        }
    ],
    "dq_specs": [
        {
            "spec_id": "check_sales_bronze_with_extraction_date",
            "input_id": "sales_source",
            "dq_type": "validator",
            "fail_on_error": True,
            "result_sink_location": "sample/lakehouse/validation",
            "dq_functions": [
                {
                    "dq_function": "expect_column_values_to_not_be_null",
                    "args": {"column": "item"},
                }
            ],
        }
    ],
    "output_specs": [
        {
            "spec_id": "sales_bronze",
            "input_id": "sales_source",
            "write_type": "overwrite",
            "data_format": "delta",
            "partitions": ["date", "customer"],
            "location": "sample/lakehouse/output",
        }
    ]
}

load_data(etl_config=etl_config)
