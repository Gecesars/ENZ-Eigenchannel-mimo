from __future__ import annotations

from typing import Any

C0_M_S = 299_792_458.0


def frequencia_corte_te10_ghz(a_mm: float) -> float:
    return C0_M_S / (2.0 * a_mm * 1e-3) / 1e9


def comprimento_onda_livre_mm(f_ghz: float) -> float:
    return C0_M_S / (f_ghz * 1e9) * 1e3


def largura_banda_ghz(inferior_ghz: float, superior_ghz: float) -> float:
    return superior_ghz - inferior_ghz


def largura_banda_fracionaria_percentual(
    inferior_ghz: float, superior_ghz: float
) -> float:
    centro = (inferior_ghz + superior_ghz) / 2.0
    return largura_banda_ghz(inferior_ghz, superior_ghz) / centro * 100.0


def _checagem(
    id_: str,
    publicado: Any,
    derivado: Any,
    unidade: str,
    consistente: bool,
    fonte: str,
    observacao: str = "",
) -> dict[str, Any]:
    return {
        "id": id_,
        "classificacao_publicado": "PUBLICADO",
        "classificacao_calculo": "DERIVADO",
        "publicado": publicado,
        "derivado": derivado,
        "unidade": unidade,
        "resultado": "CONSISTENTE" if consistente else "DIVERGENTE",
        "fonte": fonte,
        "observacao": observacao,
    }


def validar_artigo_base() -> dict[str, Any]:
    area = 14.0 * 7.7143
    fc = frequencia_corte_te10_ghz(7.11)
    lambda0 = comprimento_onda_livre_mm(25.87)
    dimensoes_normalizadas = [valor / lambda0 for valor in (11.0, 27.0, 36.0)]
    fbw_medida = largura_banda_fracionaria_percentual(25.60, 26.71)

    checagens = [
        _checagem(
            "area_transversal_inicial",
            108.0,
            area,
            "mm2",
            abs(area - 108.0) <= 0.001,
            "Secao III, pagina 4",
            "14 mm x 7.7143 mm; diferenca apenas da precisao decimal publicada.",
        ),
        _checagem(
            "corte_te10_wr28",
            21.08,
            fc,
            "GHz",
            abs(fc - 21.08) <= 0.01,
            "Secao III, pagina 4",
            "Calculado com c0 exato e a=7.11 mm.",
        ),
        _checagem(
            "bandwidth_modelo_i",
            0.600,
            largura_banda_ghz(25.63, 26.23),
            "GHz",
            abs(largura_banda_ghz(25.63, 26.23) - 0.600) < 1e-12,
            "Secao III, pagina 4",
        ),
        _checagem(
            "bandwidth_final_25p64_26p24",
            0.600,
            largura_banda_ghz(25.64, 26.24),
            "GHz",
            abs(largura_banda_ghz(25.64, 26.24) - 0.600) < 1e-12,
            "Secao III, pagina 5",
        ),
        _checagem(
            "bandwidth_medido",
            1.110,
            largura_banda_ghz(25.60, 26.71),
            "GHz",
            abs(largura_banda_ghz(25.60, 26.71) - 1.110) < 1e-12,
            "Resumo e Secao IV, pagina 5",
        ),
        _checagem(
            "fbw_medido",
            4.24,
            fbw_medida,
            "%",
            abs(fbw_medida - 4.24) <= 0.01,
            "Tabela 4, pagina 8",
            "FBW derivada usando a media aritmetica dos limites medidos.",
        ),
        _checagem(
            "dimensoes_normalizadas",
            [0.95, 2.33, 3.10],
            dimensoes_normalizadas,
            "lambda0",
            all(
                abs(observado - esperado) <= 0.01
                for observado, esperado in zip(
                    dimensoes_normalizadas, (0.95, 2.33, 3.10), strict=True
                )
            ),
            "Figura 2(a), pagina 4, e Tabela 4, pagina 8",
            "Usa dimensoes externas 11 x 27 x 36 mm e lambda0 em 25.87 GHz.",
        ),
    ]

    return {
        "schema_version": "validacao-artigo-base-v1",
        "artigo": {
            "doi": "10.1109/OJAP.2026.3703713",
            "arquivo": "doc/pdfs/VilasBoas_2026_OJAP_FlatTop.pdf",
            "sha256": "57f4627b41767a8edc07eca437fb62c192fe277d3d891df39ce4bf53d101a40a",
            "classificacao": "PUBLICADO",
        },
        "constantes": {"c0_m_s": C0_M_S, "classificacao": "DERIVADO"},
        "checagens_aritmeticas": checagens,
        "divergencias_documentais": [
            {
                "id": "limite_superior_banda_simulada",
                "classificacao": "PUBLICADO",
                "resultado": "DIVERGENTE",
                "valores": [
                    "25.63-26.23 GHz (Modelo I, pagina 4)",
                    "25.64-26.25 GHz (texto associado a Tabela 1, pagina 4)",
                    "25.64-26.24 GHz (refinamento final, pagina 5)",
                    "25.64-26.25 GHz (comparacao medida/simulada, pagina 5)",
                ],
                "impacto": "A largura simulada final pode ser 600 ou 610 MHz conforme o trecho.",
            },
            {
                "id": "frequencia_superior_padrao",
                "classificacao": "PUBLICADO",
                "resultado": "DIVERGENTE",
                "valores": ["26.25 GHz na Tabela 3", "26.22 GHz na Figura 4"],
                "impacto": "Nao tratar as duas curvas como a mesma frequencia sem dados brutos.",
            },
            {
                "id": "doi_placeholder_cabecalho",
                "classificacao": "PUBLICADO",
                "resultado": "DIVERGENTE",
                "valores": [
                    "10.1109/OJAP.2020.1234567 no cabecalho da pagina 1",
                    "10.1109/OJAP.2026.3703713 no rodape e metadados IEEE",
                ],
                "impacto": "O primeiro valor e um placeholder editorial; o segundo identifica o artigo.",
            },
            {
                "id": "convencao_sll",
                "classificacao": "PUBLICADO",
                "resultado": "AMBIGUIDADE_DE_CONVENCAO",
                "valores": ["abaixo de -10.02 dB no resumo", ">10.02 dB nas tabelas"],
                "impacto": "As tabelas usam magnitude positiva de supressao; as curvas usam nivel negativo.",
            },
        ],
        "caracteristicas_sem_dados_brutos": [
            {
                "grupo": "S11 complexo e ressonancia",
                "classificacao": "PUBLICADO",
                "resultado": "NAO_REPRODUZIVEL",
                "motivo": "O artigo fornece curvas rasterizadas, nao Touchstone complexo.",
            },
            {
                "grupo": "campos E/H complexos e coerencia de fase",
                "classificacao": "PUBLICADO",
                "resultado": "NAO_REPRODUZIVEL",
                "motivo": "Nao ha exportacao de campo complexo ou fase por ranhura.",
            },
            {
                "grupo": "ganho, eficiencia, beamwidth, ripple, SLL e x-pol",
                "classificacao": "PUBLICADO",
                "resultado": "NAO_REPRODUZIVEL",
                "motivo": "Padroes complexos, malha, setup e dados tabulados completos nao foram publicados.",
            },
            {
                "grupo": "matching por FR4 e supressao TE10-TM11",
                "classificacao": "PUBLICADO",
                "resultado": "NAO_REPRODUZIVEL",
                "motivo": "epsilon_r, tan_delta, coordenadas dos pinos e propriedades do condutor estao DESCONHECIDOS.",
            },
        ],
        "derivacoes_adicionais": {
            "lambda0_mm_em_25p87_ghz": lambda0,
            "desvio_largura_ranhura_medida_percentual": [
                (0.93 / 0.8 - 1.0) * 100.0,
                (0.94 / 0.8 - 1.0) * 100.0,
            ],
            "desvio_comprimento_ranhura_medido_percentual": [
                0.0,
                (5.68 / 5.66 - 1.0) * 100.0,
            ],
            "classificacao": "DERIVADO",
        },
    }
