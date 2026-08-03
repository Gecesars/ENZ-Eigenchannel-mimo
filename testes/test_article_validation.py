from enz_eigenchannel_mimo.article_validation import (
    frequencia_corte_te10_ghz,
    largura_banda_fracionaria_percentual,
    validar_artigo_base,
)


def test_corte_te10_wr28_confere_com_valor_publicado():
    assert abs(frequencia_corte_te10_ghz(7.11) - 21.08) < 0.01


def test_fbw_medida_confere_com_tabela_4():
    assert abs(largura_banda_fracionaria_percentual(25.60, 26.71) - 4.24) < 0.01


def test_todas_as_checagens_aritmeticas_sao_consistentes():
    resultado = validar_artigo_base()
    assert all(
        item["resultado"] == "CONSISTENTE"
        for item in resultado["checagens_aritmeticas"]
    )
    assert len(resultado["divergencias_documentais"]) == 4
