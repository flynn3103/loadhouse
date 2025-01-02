"""Module for common file storage functions."""

import json
from abc import ABC
from typing import Any
from urllib.parse import ParseResult, urlparse
from lakehouse_engine.utils.storage.local_fs_storage import LocalFSStorage

class FileStorageFunctions(ABC):
    """Class for common file storage functions."""

    @classmethod
    def read_json(cls, path: str) -> Any:
        """Read a json file.

        The file should be in a supported file system (e.g., s3, dbfs or
        local filesystem).

        Args:
            path: path to the json file.
            disable_dbfs_retry: optional flag to disable file storage dbfs.

        Returns:
            Dict with json file content.
        """
        url = urlparse(path, allow_fragments=False)
        if url.scheme == "file":
            return json.load(LocalFSStorage.get_file_payload(url))
        else:
            raise NotImplementedError(
                f"File storage protocol not implemented for {path}."
            )