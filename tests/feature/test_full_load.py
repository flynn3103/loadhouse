"""Test full loads."""

from typing import List

import pytest

from loadhouse.core.definitions import InputFormat

from loadhouse.engine import load_data
from tests.utils.local_storage import LocalStorage
from tests.conftest import (
    FEATURE_RESOURCES,
    LAKEHOUSE_FEATURE_CONTROL,
    LAKEHOUSE_FEATURE_IN,
    LAKEHOUSE_FEATURE_OUT,
)

TEST_PATH = "full_load"
TEST_RESOURCES = f"{FEATURE_RESOURCES}/{TEST_PATH}"
TEST_LAKEHOUSE_IN = f"{LAKEHOUSE_FEATURE_IN}/{TEST_PATH}"
TEST_LAKEHOUSE_CONTROL = f"{LAKEHOUSE_FEATURE_CONTROL}/{TEST_PATH}"
TEST_LAKEHOUSE_OUT = f"{LAKEHOUSE_FEATURE_OUT}/{TEST_PATH}"


@pytest.mark.parametrize(
    "scenario",
    [
        ["full_overwrite", InputFormat.DELTAFILES.value],
        ["with_filter", InputFormat.PARQUET.value]
    ],
)
def test_batch_full_load(scenario: List[str]) -> None:
    """Test full loads in batch mode.

    Args:
        scenario: scenario to test.
             with_filter - loads in full but applies a filter to the source.
             with_filter_partition_overwrite - loads in full but only overwrites
             partitions that are contained in the data being loaded, keeping
             untouched partitions in the target table, therefore not doing a
             complete overwrite.
             full_overwrite - loads in full and overwrites target table.
    """
    LocalStorage.copy_file(
        f"{TEST_RESOURCES}/{scenario[0]}/data/source/part-01.csv",
        f"{TEST_LAKEHOUSE_IN}/{scenario[0]}/data/",
    )
    # breakpoint()
    # load_data(f"file://{TEST_RESOURCES}/{scenario[0]}/batch_init.json")
    # LocalStorage.clean_folder(
    #     f"{TEST_LAKEHOUSE_IN}/{scenario[0]}/data",
    # )