
import ast
import os

from pyspark.sql import SparkSession
from lakehouse_engine.utils.logging_handler import LoggingHandler
from lakehouse_engine.core.definitions import EngineConfig
from lakehouse_engine.utils.configs.config_utils import ConfigUtils

class ExecEnv(object):
    """Represents the basic resources regarding the engine execution environment.

    Currently, it is used to encapsulate both the logic to get the Spark
    session and the engine configurations.
    """
    DEFAULT_AWS_REGION = "eu-west-1"
    SESSION: SparkSession
    _LOGGER = LoggingHandler(__name__).get_logger()

    @classmethod
    def get_or_create(
        cls,
        session: SparkSession = None,
        spark_driver_memory: str = '2g',
        enable_hive_support: bool = True,
        app_name: str = None,
        config: dict = None,
    ) -> None:
        """Get or create an execution environment session (currently Spark).

        It instantiates a singleton session that can be accessed anywhere from the
        lakehouse engine. By default, if there is an existing Spark Session in
        the environment (getActiveSession()), this function re-uses it. It can
        be further extended in the future to support forcing the creation of new
        isolated sessions even when a Spark Session is already active.

        Args:
            session: spark session.
            enable_hive_support: whether to enable hive support or not.
            app_name: application name.
            config: extra spark configs to supply to the spark session.
        """
        default_config = {
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
            "spark.databricks.delta.optimizeWrite.enabled": True,
            "spark.sql.adaptive.enabled": True,
            "spark.databricks.delta.merge.enableLowShuffle": True,
        }
        cls._LOGGER.info(
            f"Using the following default configs you may want to override them for "
            f"your job: {default_config}"
        )
        final_config: dict = {**default_config, **(config if config else {})}
        cls._LOGGER.info(f"Final config is: {final_config}")

        if session:
            cls.SESSION = session
        elif SparkSession.getActiveSession():
            cls.SESSION = SparkSession.getActiveSession()
            for key, value in final_config.items():
                cls.SESSION.conf.set(key, value)
        else:
            cls._LOGGER.info("Creating a new Spark Session")

            session_builder = SparkSession.builder.appName(app_name)
            for k, v in final_config.items():
                session_builder.config(k, v)

            if enable_hive_support:
                session_builder = session_builder.enableHiveSupport()
            cls.SESSION = session_builder.getOrCreate()

        if not session:
            cls._set_environment_variables(final_config.get("os_env_vars"))

    @classmethod
    def _set_environment_variables(cls, os_env_vars: dict = None) -> None:
        """Set environment variables at OS level.

        By default, we are setting the AWS_DEFAULT_REGION as we have identified this is
        beneficial to avoid getBucketLocation permission problems.

        Args:
            os_env_vars: this parameter can be used to pass the environment variables to
                be defined.
        """
        if os_env_vars is None:
            os_env_vars = {}

        for env_var in os_env_vars.items():
            os.environ[env_var[0]] = env_var[1]

        if "AWS_DEFAULT_REGION" not in os_env_vars:
            os.environ["AWS_DEFAULT_REGION"] = cls.SESSION.conf.get(
                "spark.databricks.clusterUsageTags.region", cls.DEFAULT_AWS_REGION
            )