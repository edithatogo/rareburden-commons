"""Compatibility imports for the acquisition download API."""

from .core import (
    AcquisitionError,
    AcquisitionRequest,
    AcquisitionResult,
    DownloadPolicy,
    SourceChangedError,
    acquire_http,
    download_public_artifact,
    redact_url,
)

__all__ = [
    "AcquisitionError",
    "AcquisitionRequest",
    "AcquisitionResult",
    "DownloadPolicy",
    "SourceChangedError",
    "acquire_http",
    "download_public_artifact",
    "redact_url",
]
