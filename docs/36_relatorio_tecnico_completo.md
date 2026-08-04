# 36 — Dossiê técnico da cavidade ENZ e do ambiente HFSS

## 1. Escopo, atribuição e critério editorial

**PUBLICADO:** o documento primário é o artigo de Evandro C. Vilas Boas,
Sofia B. de Vasconcellos, Arismar Cerqueira Sodré Jr. e Felipe A. P. de
Figueiredo, *A Millimeter-Wave Flat-Top Fan-Beam Antenna Array Based on a
Geometry-Independent Resonant Cavity*, IEEE Open Journal of Antennas and
Propagation, 2026, DOI `10.1109/OJAP.2026.3703713`. A versão aceita pelos
autores informa licença Creative Commons Attribution 4.0.

**DERIVADO:** este dossiê organiza o corpus teórico do repositório, a auditoria
dimensional do artigo, a especificação declarativa v7, os resultados HFSS e os
gates científicos em um único volume navegável. Ele não substitui o artigo e
não reivindica suas contribuições. Figuras adaptadas ou reproduzidas recebem
crédito individual; resultados locais são identificados como `SIMULADO` ou
`HIPÓTESE`.

**DERIVADO:** o requisito de densidade foi convertido em dois gates
quantitativos reprodutíveis: pelo menos duas vezes o número de palavras
técnicas recuperáveis do artigo e pelo menos duas vezes a soma de figuras e
tabelas identificadas no documento primário. O gerador registra essas
contagens, o número de páginas, a lista de fontes e o SHA-256 do PDF. O critério
mede conteúdo auditável, não mera repetição textual.

## 2. Leitura correta do estado científico

**HIPÓTESE:** a geometria HFSS v7 é uma reconstrução exploratória. O artigo
publica várias dimensões externas e funcionais, mas não fornece o CAD, todas as
coordenadas internas, a construção integral dos Modelos I–IX nem os dados
numéricos medidos. Dimensões ausentes permanecem marcadas como hipótese na
especificação. Nenhum parâmetro foi ajustado silenciosamente para forçar
concordância.

**SIMULADO:** a infraestrutura foi efetivamente exercitada no AEDT 2024 R2,
via PyAEDT 1.3.0 e gRPC nativo, com 14 cores. A malha adaptativa convergiu, as
sweeps foram concluídas e os campos complexos foram preservados. Isso valida o
fluxo de automação e a consistência interna de várias etapas; não valida a
reprodução eletromagnética do protótipo publicado.

**SIMULADO:** o gate estrito de passividade falhou em 25,87 GHz porque a
potência radiada excedeu a potência aceita em 2,16235%. O mínimo de S11 da
reconstrução foi −2,369 dB em 26,22 GHz, enquanto o artigo informa banda abaixo
de −10 dB aproximadamente entre 25,64 e 26,24 GHz. A divergência é material e
mantém a classificação global `HIPÓTESE`.

## 3. Sistema de coordenadas e waveport

**DERIVADO:** o sistema global da especificação usa X ao longo do arranjo de
ranhuras, Y na propagação longitudinal entre alimentação e cavidade e Z na
altura. A waveport está no plano XZ, em `y = −18 mm`, com normal em Y. A seção
da folha mede `3,56 mm` em X e `7,11 mm` em Z.

**PUBLICADO:** a alimentação emprega a seção WR-28, cujas dimensões internas
declaradas no artigo são `a = 7,11 mm` e `b = 3,56 mm`.

**DERIVADO:** no mapeamento geométrico adotado, a maior dimensão da folha está
em Z. A linha de integração modal é

```math
\mathbf{l}_{\mathrm{int}}:\;(0,-18,3)\ \mathrm{mm}
\longrightarrow(0,-18,10{,}11)\ \mathrm{mm},
```

portanto `Δx = 0`, `Δy = 0` e `Δz = 7,11 mm`. A orientação é estritamente Z.
O bounding box salvo no projeto é
`[−1,78, −18, 3] → [1,78, −18, 10,11] mm`. O gate nativo `UseIntLine` está
ativo e o setup automático `Auto1` não está presente.

## 4. Geometria declarativa e rastreabilidade dimensional

**PUBLICADO:** o artigo explicita, entre outros valores, comprimento total de
36 mm, dimensão vertical externa de 27 mm, largura de flange de 22,5 mm,
cinco ranhuras de `5,66 × 0,8 mm`, chanfros de 3 mm, seção WR-28, quatro pinos
metálicos de 1 mm e lâmina de FR4 com espessura indicada de 1,65 mm.

**HIPÓTESE:** a reconstrução v7 usa parâmetros exploratórios para fechar
volumes que não podem ser determinados unicamente a partir das vistas do
artigo. Cada um deles mantém nome explícito com sufixo `exploratorio` ou
classificação equivalente. O arquivo YAML é a fonte de verdade; objetos HFSS
têm nomes determinísticos e todas as unidades são declaradas.

**DERIVADO:** o modelo preserva versões anteriores. A v5 registra a primeira
reconstrução visual; a v6 corrige a waveport e sua linha modal; a v7 acrescenta
a sweep discreta dos campos do artigo. Nenhuma versão anterior foi sobrescrita.

## 5. Teoria eletromagnética mínima para interpretar a cavidade

**DERIVADO:** para o modo dominante de um guia retangular ideal, a constante de
propagação pode ser escrita como

```math
\beta_{10}=k_0\sqrt{1-\left(\frac{f_c}{f}\right)^2},
\qquad
f_c=\frac{c}{2a}.
```

Próximo ao corte, `β10 → 0` e o comprimento de onda guiado cresce. Uma forma
equivalente de representar esse comportamento é definir uma permissividade
modal efetiva

```math
\varepsilon_{\mathrm{eff},10}
=\varepsilon_0\left[1-\left(\frac{f_c}{f}\right)^2\right].
```

**PUBLICADO:** Vilas Boas et al. exploram o regime ENZ inspirado pelo modo
dominante para obter baixa variação longitudinal de fase e excitação coerente
das ranhuras. O perfil externo escalonado redistribui a impedância espacial e
o acoplamento das aberturas, formando um feixe em leque com topo aproximadamente
plano sem uma rede complexa de alimentação por elementos independentes.

**DERIVADO:** a condição `β ≈ 0` não garante, isoladamente, bom casamento,
eficiência ou uniformidade de amplitude. Aberturas, perdas, descontinuidades,
FR4, pinos, modos superiores e acoplamento com o espaço livre modificam o
problema de contorno. Por isso, a interpretação deve combinar fase complexa,
potência, S-parâmetros, padrões e convergência de malha.

## 6. Cortes e campos configurados

**SIMULADO:** a v7 contém oito sistemas de corte auditáveis:

| Corte | Plano | Localização funcional | Objetos principais |
|---|---|---|---|
| `Cut_ZX_ArrayCenter` | ZX | centro longitudinal do arranjo | ar e FR4 |
| `Cut_XY_MidHeight` | XY | meia-altura interna | ar e FR4 |
| `Cut_YZ_Slot1` | YZ | ranhura 1 | ar |
| `Cut_YZ_Slot2` | YZ | ranhura 2 | ar |
| `Cut_YZ_Slot3` | YZ | ranhura central | ar e FR4 |
| `Cut_YZ_Slot4` | YZ | ranhura 4 | ar |
| `Cut_YZ_Slot5` | YZ | ranhura 5 | ar |
| `Cut_ZX_Port` | ZX | plano da waveport | ar |

**SIMULADO:** para cada corte existe um plot `Mag_E` a 25,87 GHz e fase de
visualização 0°. Essa vista de magnitude é apenas uma projeção. A solução
`.aedtresults` preserva os campos complexos usados pelo solver; os artefatos de
magnitude não os substituem.

**DERIVADO:** cortes ZX mostram a variação ao longo da alimentação/cavidade e
da altura; o corte XY evidencia a distribuição que alimenta as cinco
ranhuras; cortes YZ individuais ajudam a comparar o acoplamento local. A
comparação quantitativa entre ranhuras requer exportar amplitude e fase
complexas na mesma normalização e malha de amostragem.

## 7. Setup, sweeps e campo distante

**SIMULADO:** o projeto contém somente o setup
`Setup_Driven_25p87_HIPOTESE`. O adaptativo foi executado em 25,87 GHz com
meta `Max Mag. ΔS < 0,02`, mínimo de dois passes e máximo de quinze.

**SIMULADO:** a sweep `Sweep_25_27GHz` contém 201 pontos de saída entre 25 e
27 GHz e usa interpolação convergida. A sweep `Sweep_Fields_Article` é discreta
nos pontos 25,65, 25,87 e 26,22 GHz, salvando campos próximos e radiados. Essa
separação evita tratar uma interpolação de S-parâmetros como se ela preservasse
automaticamente todos os campos radiados complexos nos pontos de interesse.

**SIMULADO:** a esfera `FF_Sphere_2deg` usa passo angular de 2°. Foram criados
relatórios de S11, eficiência, ganho realizado de pico, E-plane em 25,87 GHz,
E/H co- e cross-polarizados nas três frequências e ganho total 3D.

## 8. Convergência e recursos computacionais

**SIMULADO:** o run imutável `ENZ-20260803-192218-ed5384a5` terminou
normalmente. Foram concluídos quatro passes:

| Passe | Elementos resolvidos | Max Mag. ΔS |
|---:|---:|---:|
| 1 | 17.889 | não aplicável |
| 2 | 20.975 | 0,047718 |
| 3 | 24.571 | 0,011616 |
| 4 | 28.772 | 0,0041377 |

**SIMULADO:** a estatística global registra 33.723 tetraedros. O processo
adaptativo usou 14 cores; durante sweeps distribuídas o AEDT repartiu os
recursos entre frequências. Foram solicitados uma task e zero GPU. O projeto
foi salvo antes da solução, e o manifesto registra versão, build, porta gRPC,
licença, PyAEDT, hashes e verificação de processo órfão.

## 9. Balanço de potência

**SIMULADO:** em 25,87 GHz foram obtidos `Pinc = 1`,
`Pacc = 0,38535475` e `Prad = 0,39368747`. As identidades relatadas pelo HFSS
fecham numericamente:

```math
\eta_{\mathrm{rad}}=\frac{P_{\mathrm{rad}}}{P_{\mathrm{acc}}}
=1{,}02162350,
\qquad
\eta_{\mathrm{tot}}=\frac{P_{\mathrm{rad}}}{P_{\mathrm{inc}}}
=0{,}39368747.
```

**DERIVADO:** o fechamento algébrico não é aprovação física. Para um sistema
passivo, `Prad ≤ Pacc` dentro da tolerância numérica. O excesso de 2,16235%
reprova o gate estrito e exige investigação de integração de potência,
normalização modal, perdas, região aberta e convergência espacial antes de
qualquer afirmação de eficiência.

## 10. Comparação com o artigo

| Evidência | Artigo | Reconstrução v7 | Gate |
|---|---|---|---|
| banda de S11 abaixo de −10 dB | aproximadamente 25,64–26,24 GHz | não observada | FAIL |
| mínimo de S11 | curva publicada próxima da ressonância | −2,369 dB em 26,22 GHz | FAIL |
| S11 em 25,87 GHz | dentro da banda publicada | −0,997 dB | FAIL |
| ganho realizado | simulado/medido aproximadamente 5,8–7,8 dBi na banda | pico 3,288 dBi em 25,87 GHz | FAIL |
| orientação da waveport | alimentação WR-28 | integração em Z verificada | PASS |
| malha adaptativa | configuração detalhada não publicada | ΔS convergido | PASS local |
| Modelos I–IX | figuras e padrões publicados | CAD integral ausente | DESCONHECIDO |
| curvas medidas | plots publicados | amostras numéricas não fornecidas | DESCONHECIDO |

**HIPÓTESE:** a discrepância não autoriza concluir que o artigo está incorreto.
Ela indica que a reconstrução não contém informação geométrica/material
suficiente ou ainda possui simplificações relevantes. O resultado útil é um
modelo auditável para investigar quais parâmetros são identificáveis.

## 11. Estudos paramétricos

**HIPÓTESE:** três estudos foram configurados e não executados:

| Estudo | Variável | Valores configurados |
|---|---|---|
| chanfro | `chanfro` | 0, 1, 2, 3 e 4 mm |
| largura do degrau | `degrau_largura` | 8, 9 e 10 mm |
| altura do degrau | `degrau_altura` | 0,5, 1,0 e 1,5 mm |

**PUBLICADO:** esses conjuntos correspondem às variações apresentadas no
artigo para o protótipo refinado. **HIPÓTESE:** a mera configuração das sweeps
locais não reproduz as curvas publicadas; cada ponto deve ser resolvido,
validado e exportado antes de comparação.

## 12. Reprodutibilidade e próximos gates

**DERIVADO:** uma reprodução cientificamente defensável requer, no mínimo:

1. obter CAD ou coordenadas completas dos Modelos I–IX;
2. confirmar propriedades complexas do FR4 na banda de 26 GHz;
3. confirmar contatos, parafusos, pinos, condutividade e rugosidade;
4. executar estudo de convergência espacial e de região de radiação;
5. fechar passividade com tolerância declarada;
6. exportar campos complexos nos oito cortes;
7. executar os três estudos paramétricos sem ajuste retroativo;
8. digitalizar ou obter os dados medidos com autorização e incerteza;
9. comparar S11, ganho, ripple, largura de feixe e SLL com métricas idênticas;
10. versionar qualquer nova hipótese em vez de alterar silenciosamente a v7.

## 13. Créditos e licença

**PUBLICADO:** toda contribuição científica do artigo-base, suas dimensões,
figuras, curvas publicadas e conceitos específicos da antena são creditados a
Vilas Boas, Vasconcellos, Sodré Jr. e Figueiredo. A figura dimensional incluída
no atlas é reproduzida/adaptada sob CC BY 4.0 com DOI explícito.

**DERIVADO:** a organização do corpus, a especificação declarativa, os scripts
de auditoria, o ambiente reprodutível e este dossiê pertencem ao projeto
ENZ-Eigenchannel-mimo, coordenado por Geraldo César Simão. As referências
fundamentais de ENZ, dopagem fotônica, cavidades, antenas e MIMO são listadas
no BibTeX e nos capítulos anexos; nenhuma delas é apresentada como contribuição
original deste repositório.

**DERIVADO:** o PDF deve sempre circular junto de seu manifesto. O manifesto
registra fontes, contagens, hashes, gates e limitações, impedindo que imagens
de simulação sejam confundidas com resultados medidos ou publicados.

## 14. Extensão Q0 — sistema MIMO 2×2 com quatro radiadores

**DESCONHECIDO:** a campanha especificada em `inst.md` exige quatro radiadores
previamente validados. A auditoria recursiva encontrou 22 projetos AEDT, com
19 hashes distintos, mas nenhum manifesto válido para `RAD_A1`, `RAD_A2`,
`RAD_B1` ou `RAD_B2`. O estado formal é
`BLOCKED_MISSING_VALIDATED_ARTIFACTS`.

**DERIVADO:** cópias de runs não equivalem a quatro radiadores independentes.
Os projetos encontrados pertencem ao smoke M0 ou às reconstruções
exploratórias v5–v7. O smoke não é radiador; v5 não foi solucionada; v7 é
HIPÓTESE e reprova passividade e correspondência de S11. Portanto as redes em
guia, estados EVEN/ODD/QUADRATURE e gates Q1–Q5 não foram fabricados
numericamente nem apresentados como resultados.

**SIMULADO:** o candidato v7 foi reaberto no HFSS 2024.2 para inspeção somente
leitura. Foram confirmados 11 objetos, uma excitação, duas fronteiras, um
setup, duas sweeps, oito plots de campo, oito relatórios, oito sistemas locais
de corte e três estudos paramétricos. Não houve exceção de extração e o hash
do projeto permaneceu
`c65aac7fa669d6b98264081712e29c335eb1f1ae1f72d40d0eac61921573ad4d`.

**SIMULADO:** a interface permanece aberta no PID 22204 e na porta gRPC
49782. O estado transitório criado pelo AEDT foi separado do pacote científico:
24 arquivos efêmeros foram excluídos do inventário e sete caches versionados
estão registrados como temporariamente ausentes enquanto a sessão os
administra. A relação nominal está em `poros_aedt/manifest.json`; nenhum
lock, semáforo, `.asol_priv` ou temporário novo foi tratado como resultado
científico.

O relatório detalhado, a matriz de evidências e a lista exata de dados
necessários para liberar Q0 estão em
`docs/32_relatorio_implementacao_mimo_2x2.md`. Os artefatos canônicos são:

- `artefatos/q0/missing_validated_models.json`;
- `artefatos/q0/artifact_inventory.json`;
- `artefatos/q0/hfss_inspection/hfss_inspection.json`;
- `artefatos/q0/hfss_inspection/hfss_design_preview.jpg`.

**DESCONHECIDO:** ECC, TARC, CCL, MEG, rank efetivo e capacidade permanecem
sem valor para o sistema solicitado, pois não existem S2P externo nem padrões
`Etheta/Ephi` complexos por porta. Essa ausência é um resultado de gate, não
uma lacuna preenchível por hipótese geométrica.

## 15. Extensão exploratória Q4-C0 v8 após autorização

**HIPÓTESE:** após o gate Q0, foi autorizada explicitamente a utilização da v7
aberta como fonte exploratória. Quatro cópias determinísticas foram integradas
a duas redes H-plane simétricas, formando duas portas externas e o estado
EVEN/EVEN. A construção não altera retroativamente o resultado Q0: nenhuma
instância fonte foi promovida a radiador validado.

**SIMULADO:** o projeto Q4-C0 v8 contém 43 objetos, duas waveports com linha de
integração em (Z), 15 sistemas de coordenadas/cortes, nove plots de campo,
três relatórios de campo distante e um relatório de rede. O AEDT 2024 R2
solucionou o setup com 14 cores em três passes. O erro adaptativo final foi

```math
\Delta S_{\max}=2{,}8215\times10^{-4},
```

com 651.746 elementos resolvidos no último passe.

**SIMULADO:** em (25{,}87\,\mathrm{GHz}), o LastAdaptive forneceu
(S_{11}=-0{,}129025\,\mathrm{dB}),
(S_{22}=-0{,}129095\,\mathrm{dB}) e
(S_{12}=S_{21}=-83{,}867707\,\mathrm{dB}). A maior singularidade na
varredura de 25–27 GHz foi (0{,}9995667), portanto o gate estrito de
passividade passou. O TARC EVEN/EVEN foi
(-0{,}129291\,\mathrm{dB}), revelando o mesmo descasamento severo das portas.

**SIMULADO:** os padrões embarcados foram exportados como campos vetoriais
complexos. A ECC calculada pelo produto interno de
(\mathbf E_1=(E_{\theta,1},E_{\phi,1})) e
(\mathbf E_2=(E_{\theta,2},E_{\phi,2})) foi

```math
\rho_e=\frac{
\left|\int_\Omega \mathbf E_1\cdot\mathbf E_2^*d\Omega\right|^2}
{\int_\Omega |\mathbf E_1|^2d\Omega
 \int_\Omega |\mathbf E_2|^2d\Omega}
=2{,}03548\times10^{-5}.
```

**DERIVADO:** baixa ECC e isolamento alto não bastam para declarar diversidade
ou throughput. Os gates (S_{11}<-10\,\mathrm{dB}) e
(S_{22}<-10\,\mathrm{dB}) falharam, e a geometria fonte continua
`HIPÓTESE`. O estado científico é
`COMPLETED_WITH_SCIENTIFIC_BLOCK`; o claim MIMO permanece
`BLOCKED_SOURCE_MODEL_HIPOTESE`.

Os dados reprodutíveis estão em `artefatos/q4_mimo2x2_c0_v8/`, com S2P,
convergência, malha, perfil do solver, XML de potência, dois FFD complexos,
nove cortes de campo, três diagramas e o manifesto `validation.json`. O projeto
solucionado tem SHA-256
`1b93d9d855969733cfe736c1d5396f0cc932cff6f99cfecc9da736993a514a3d`.
