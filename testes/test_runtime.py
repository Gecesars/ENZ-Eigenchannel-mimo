import pytest
from enz_eigenchannel_mimo.aedt.runtime import AedtRuntimeSpec, normalize_aedt_version


def test_normaliza_versoes_2024_r2():
    assert normalize_aedt_version("2024.2") == "2024.2"
    assert normalize_aedt_version("2024 R2") == "2024.2"
    assert normalize_aedt_version("242") == "2024.2"


def test_runtime_rejeita_fallback_de_versao():
    with pytest.raises(ValueError):
        AedtRuntimeSpec(version="2025.1").validate()


def test_attach_exige_endpoint_explicito():
    with pytest.raises(ValueError):
        AedtRuntimeSpec(new_desktop=False).validate()
    AedtRuntimeSpec(new_desktop=False, port=50051).validate()
