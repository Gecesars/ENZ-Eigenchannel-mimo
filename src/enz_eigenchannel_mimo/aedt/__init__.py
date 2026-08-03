"""Camada estrita de automação do AEDT/HFSS."""

from .runtime import AedtRuntimeSpec, ErroRuntimeAedt, preflight_aedt

__all__ = ["AedtRuntimeSpec", "ErroRuntimeAedt", "preflight_aedt"]
