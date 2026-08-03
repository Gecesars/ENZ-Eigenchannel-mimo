# Corpus PDF auditado

## Escopo

**DERIVADO:** o escopo corresponde ao artigo-base, ao seu predecessor direto
adicionado durante a auditoria e a todas as entradas `@article` de
`referencias/references.bib`: 14 referências primárias.

**PUBLICADO:** o artigo-base é
*A Millimeter-Wave Flat-Top Fan-Beam Antenna Array Based on a
Geometry-Independent Resonant Cavity*, DOI
`10.1109/OJAP.2026.3703713`. O arquivo local é a versão aceita dos autores sob
CC BY 4.0.

## Dossiê técnico consolidado

**DERIVADO:** `Relatorio_Tecnico_ENZ_Cavidade_VilasBoas_v1.pdf` reúne em 99
páginas a teoria do corpus, a auditoria dimensional, a geometria exploratória,
a waveport em Z, os cortes de campo, os relatórios HFSS e os gates de
validação. O PDF contém 25.530 palavras extraíveis, 18 figuras e 19 tabelas.

**HIPÓTESE:** o dossiê não promove a reconstrução a reprodução do artigo. O
gate de passividade e a correspondência de S11 permanecem reprovados. Métricas,
fontes e SHA-256 estão em
`Relatorio_Tecnico_ENZ_Cavidade_VilasBoas_v1.manifest.json`.

Para regenerar:

```powershell
python scripts/gerar_relatorio_tecnico_pdf.py
```

## Resultado da aquisição

| Chave | Estado | Páginas | Arquivo ou ação |
|---|---|---:|---|
| `VilasBoas2026FlatTop` | validado | 10 | `VilasBoas_2026_OJAP_FlatTop.pdf` |
| `VilasBoas2025PhotonicDoping` | indisponível | — | atalho DOI em `indisponiveis/` |
| `VilasBoas2026DielectricLoaded` | indisponível | — | atalho DOI em `indisponiveis/` |
| `Li2022GeometryIndependent` | validado | 8 | `Li2022GeometryIndependent.pdf` |
| `Silveirinha2006Supercoupling` | validado | 4 | `Silveirinha2006Supercoupling.pdf` |
| `Liberal2017PhotonicDoping` | indisponível | — | atalho DOI em `indisponiveis/` |
| `Liberal2017NZIPhotonics` | indisponível | — | atalho DOI em `indisponiveis/` |
| `Yan2024FanoENZ` | validado | 7 | `Yan2024FanoENZ.pdf` |
| `Harrington1971CharacteristicModes` | indisponível | — | atalho DOI em `indisponiveis/` |
| `Telatar1999Capacity` | validado | 28 | `Telatar1999Capacity.pdf` |
| `Ayach2014SparsePrecoding` | validado | 30 | `Ayach2014SparsePrecoding.pdf` |
| `Molisch2017HybridBeamforming` | validado | 13 | `Molisch2017HybridBeamforming.pdf` |
| `Slater1946MicrowaveElectronics` | validado | 72 | `Slater1946MicrowaveElectronics.pdf` |
| `Lai1990LeakingModes` | validado | 12 | `Lai1990LeakingModes.pdf` |

**DERIVADO:** 9 de 14 PDFs passaram todos os gates. Os cinco itens restantes
foram bloqueados por HTTP 403/202 ou por incompatibilidade de título. Nenhum
HTML, relatório precursor diferente ou arquivo paywalled obtido por contorno
foi renomeado como se fosse o artigo.

**DESCONHECIDO:** o suplemento de Li et al. está registrado no manifesto, mas o
endpoint do PubMed Central devolveu HTML em vez de PDF nesta execução.

## Gates

Cada PDF aceito tem assinatura `%PDF`, marcador `%%EOF`, parse estrito,
contagem de páginas, compatibilidade lexical de título ou checksum publicado,
tamanho e SHA-256. O resultado integral, URLs e erros estão em `manifest.json`.

Para repetir a aquisição:

```powershell
python scripts/adquirir_corpus_pdfs.py
```

O código de saída `2` indica que ao menos uma referência permaneceu
indisponível; o manifesto ainda é produzido.

## Correção bibliográfica

**PUBLICADO:** o DOI correto de *Photonic doping of epsilon-near-zero media* é
`10.1126/science.aal2672`. O valor anterior `10.1126/science.aag0332` não
resolvia para esse artigo e foi corrigido no BibTeX.
