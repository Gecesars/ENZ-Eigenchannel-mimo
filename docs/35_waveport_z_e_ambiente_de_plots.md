# 35 — Waveport em Z e ambiente de plots do artigo

## 1. Resultado executado

**SIMULADO:** a reconstrução exploratória v7 está aberta no AEDT 2024 R2 no
design `HFSS_ENZ_G0_figura2_reconstrucao_v7_M4`. A sessão é dedicada e não
substituiu nem encerrou a sessão gráfica preexistente do usuário.

**HIPÓTESE:** a geometria continua sendo uma reconstrução exploratória das
Figuras 1(a) e 2(a) de Vilas Boas et al., DOI
`10.1109/OJAP.2026.3703713`. O artigo não publica CAD nem coordenadas
suficientes para reconstruir fielmente todos os Modelos I–IX.

## 2. Correção auditada da waveport

**PUBLICADO:** a seção interna WR-28 é `a=7,11 mm` e `b=3,56 mm`.

**DERIVADO:** no sistema de coordenadas declarado, a folha corrigida ocupa
`3,56 mm` em X e `7,11 mm` em Z. A linha de integração modal vai de
`(0, -18, 3) mm` a `(0, -18, 10,11) mm`, portanto é estritamente paralela a Z.

**SIMULADO:** a inspeção do projeto salvo pelo AEDT retornou:

| Gate | Resultado |
|---|---|
| bounding box da folha | `[-1,78,-18,3]` a `[1,78,-18,10,11]` mm |
| extensão | `3,56 × 0 × 7,11 mm` |
| normal da folha | `[0,1,0]` |
| `UseIntLine` | `true` |
| linha nativa | `z=3,00 → 10,11 mm`, com X e Y constantes |
| setups | somente `Setup_Driven_25p87_HIPOTESE` |
| setup automático | `Auto1` ausente |

## 3. Ambiente de pós-processamento

**SIMULADO:** foram materializados no projeto:

- oito sistemas de coordenadas/cortes: ZX central, XY na meia-altura, YZ nas
  cinco ranhuras e ZX na porta;
- oito plots `Mag_E` em 25,87 GHz, um para cada corte;
- oito relatórios: S11, eficiência, ganho realizado, dois padrões E-plane,
  padrões E/H co- e cross-polarizados em três frequências e ganho 3D;
- três estudos paramétricos configurados, mas não executados: `c`, `wsp` e
  `hsp`;
- esfera `FF_Sphere_2deg`, com passo angular de 2 graus.

**SIMULADO:** a v7 contém uma sweep discreta adicional,
`Sweep_Fields_Article`, nos pontos `25,65`, `25,87` e `26,22 GHz`, com campos
e campos radiados salvos. Ela foi necessária porque a sweep interpolante não
preservou dados radiados utilizáveis nos três pontos exatos da Figura 4.

**SIMULADO:** todos os oito relatórios possuem traços e foram exportados em
CSV e JPG. Os dois relatórios da Figura 4 contêm seis curvas cada: co-pol. e
cross-pol. em três frequências.

**DERIVADO:** os gráficos HFSS são absolutos em dB. As figuras publicadas são
normalizadas no pico. Os dados absolutos são preservados; uma normalização
posterior deve gerar novos artefatos e nunca substituir os dados originais.

## 4. Solve e recursos

**SIMULADO:** o run configurado `ENZ-20260803-191731-ed5384a5` usou AEDT
2024.2.0, PyAEDT 1.3.0 e gRPC nativo. O worker solicitou 14 cores, uma task e
zero GPU. O AEDT redistribuiu os cores entre grupos MPI durante sweeps
paralelas.

**SIMULADO:** o run limpo e imutável de validação é
`ENZ-20260803-192218-ed5384a5`. Seu manifesto registra conclusão normal, zero
erros, ausência de processo órfão e verificação positiva de tamanho e SHA-256
para todos os artefatos. O ambiente de pós-processamento foi aplicado somente
à cópia configurada, preservando esse run como evidência reprodutível.

**SIMULADO:** o adaptativo convergiu em quatro passes, com
`Max Mag. Delta S=0,0041377 < 0,02`; a estatística final contém 33.723
tetraedros. As sweeps discreta e interpolante concluíram normalmente.

## 5. Balanço de potência e divergências

**SIMULADO:** em 25,87 GHz, o projeto retorna:

| Quantidade | Valor |
|---|---:|
| potência incidente | 1,000000 |
| potência aceita | 0,38535475 |
| potência radiada | 0,39368747 |
| eficiência de radiação | 1,02162350 |
| eficiência total | 0,39368747 |
| ganho realizado de pico | 3,28777 dBi |

**DERIVADO:** as identidades internas fecham:
`Prad/Pacc = RadiationEfficiency` e
`Prad/Pinc = TotalEfficiency`. Contudo, `Prad` excede `Pacc` em 2,16235%, o
que viola o gate estrito de passividade. Logo, o balanço é algebricamente
consistente, mas fisicamente reprovado.

**SIMULADO:** o mínimo de S11 da reconstrução é apenas `−2,369 dB` em
26,22 GHz; em 25,87 GHz, S11 é `−0,997 dB`. Isso diverge da faixa publicada de
S11 abaixo de −10 dB entre aproximadamente 25,64 e 26,24 GHz. Nenhum parâmetro
foi ajustado para esconder essa diferença.

## 6. Cobertura e bloqueios

| Conteúdo do artigo | Estado |
|---|---|
| Figura 1(a), campos dos Modelos I–IX | **DESCONHECIDO:** CAD dos perfis não publicado; plots do modelo v7 disponíveis, não equivalentes |
| Figura 1(b–d), evolução dos padrões | **DESCONHECIDO:** geometrias I–IX não reconstruídas |
| Figura 2(b), S11/eficiência nominal | **SIMULADO:** relatórios configurados; resultados divergem da publicação |
| Figura 2(c–d), `c`, `wsp`, `hsp` | **HIPÓTESE:** estudos configurados, não resolvidos |
| Figura 3(b–d), curvas simuladas | **SIMULADO:** S11, ganho e E-plane configurados |
| Figuras 3–4, curvas medidas | **MEDIDO/PUBLICADO:** dados numéricos originais não fornecidos; não recriados |
| Figura 4, E/H co/cross em três frequências | **SIMULADO:** sweep discreta e relatórios completos na v7 |

Por causa das geometrias ausentes, da discrepância de S11 e da reprovação de
passividade, a classificação global permanece **HIPÓTESE**. O projeto é um
ambiente auditável de reconstrução e pós-processamento, não uma reprodução
validada do artigo.
