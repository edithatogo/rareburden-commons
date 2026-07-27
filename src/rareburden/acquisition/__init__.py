"""Provenance-first acquisition, normalisation and source-adapter utilities."""

from .core import (
    AcquisitionError,
    AcquisitionRequest,
    AcquisitionResult,
    DownloadPolicy,
    SourceChangedError,
    acquire_http,
    download_public_artifact,
    redact_url,
    register_local_release,
    validate_acquisition_manifest,
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
    "register_local_release",
    "validate_acquisition_manifest",
]
