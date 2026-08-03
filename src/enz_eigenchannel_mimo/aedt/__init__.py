"""Integração estrita com Ansys AEDT/HFSS 2024 R2."""

from .campaign import CampaignRequest, CampaignResult, G0CampaignRunner
from .runtime import (
    AEDT_VERSION,
    AedtRuntimeError,
    AedtRuntimeIdentity,
    AedtRuntimeSpec,
    normalize_aedt_version,
)
from .session import Aedt2024R2Session

__all__ = [
    "AEDT_VERSION",
    "Aedt2024R2Session",
    "AedtRuntimeError",
    "AedtRuntimeIdentity",
    "AedtRuntimeSpec",
    "CampaignRequest",
    "CampaignResult",
    "G0CampaignRunner",
    "normalize_aedt_version",
]
