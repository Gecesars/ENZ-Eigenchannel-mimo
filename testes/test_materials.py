from enz_eigenchannel_mimo.aedt.materials import candidate_materials, fr4_doe


def test_fr4_doe_tem_25_casos_explicitamente_hipoteticos():
    cases = fr4_doe()
    assert len(cases) == 25
    assert all(case.classification == "HYPOTHESIS" for case in cases)
    assert all(not case.valid_at_operating_frequency for case in cases)


def test_candidatos_com_fonte_e_frequencia():
    for material in candidate_materials():
        material.validate()
        assert material.reference_frequency_ghz == 10.0
        assert material.source
