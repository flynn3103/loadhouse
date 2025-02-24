"""Module with helper functions to interact with test execution environment."""

import os
import sys

# Import after sys.path modification
from lakehouse_engine.core.exec_env import ExecEnv

class ExecEnvHelpers(object):
    """Class with helper functions to interact with test execution environment."""

    @staticmethod
    def prepare_exec_env(spark_driver_memory: str) -> None:
        """Create single execution environment session."""
        ExecEnv.get_or_create(
            app_name="Lakehouse Engine Tests",
            enable_hive_support=False,
            config={
                "spark.master": "local[2]",
                "spark.driver.memory": spark_driver_memory,
                "spark.sql.warehouse.dir": "file:///app/tests/lakehouse/spark-warehouse/",
                "spark.sql.shuffle.partitions": "2",
                "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
                "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog",
                "spark.jars.packages": "io.delta:delta-spark_2.12:3.2.0,org.xerial:sqlite-jdbc:3.45.3.0,com.databricks:spark-xml_2.12:0.18.0",
                "spark.jars.excludes": "net.sourceforge.f2j:arpack_combined_all",
                "spark.sql.sources.parallelPartitionDiscovery.parallelism": "2",
                "spark.sql.legacy.charVarcharAsString": True,
                "spark.driver.extraJavaOptions": "-Xss4M -Djava.security.manager=allow -Djava.security.policy=spark.policy",
                "spark.authenticate": "false",
                "spark.network.crypto.enabled": "false",
                "spark.ui.enabled": "false",
            },
        )


if __name__ == "__main__":
    # Create an instance of ExecEnvHelpers and call prepare_exec_env
    ExecEnvHelpers.prepare_exec_env("2g")  # Replace "4g" with desired memory size
