import random
import string
from typing import Optional, OrderedDict

from pyspark.sql import DataFrame
from pyspark.sql.types import StructType

import sys
import os

# Add the parent directory of lakehouse_engine to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# You need to import the Load Data algorithm from the Lakehouse Engine, so that you can perform Data Loads.
from lakehouse_engine.engine import load_data

acon = {
    "input_specs": [
      {
        "spec_id": "sales_source",
        "read_type": "batch",
        "data_format": "csv",
        "options": {
          "header": True,
          "delimiter": "|",
          "inferSchema": True
        },
        "location": "file:///app/tests/lakehouse/in/feature/full_load/full_overwrite/data"
      }
    ],
    "transform_specs": [
      {
        "spec_id": "filtered_sales",
        "input_id": "sales_source",
        "transformers": [
          {
            "function": "expression_filter",
            "args": {
              "exp": "date like '2016%'"
            }
          }
        ]
      }
    ],
    "output_specs": [
      {
        "spec_id": "sales_bronze",
        "input_id": "sales_source",
        "write_type": "overwrite",
        "data_format": "delta",
        "partitions": [
          "date",
          "customer"
        ],
        "location": "file:///app/tests/lakehouse/out/feature/full_load/full_overwrite/data"
      }
    ]
  }

load_data(acon=acon)