# 32 — Relatório de implementação MIMO 2×2: pré-flight e gate Q0

## 1. Escopo e resultado executivo

**DESCONHECIDO:** a arquitetura solicitada pressupõe quatro estruturas
radiantes previamente validadas, identificadas como `RAD_A1`, `RAD_A2`,
`RAD_B1` e `RAD_B2`. Nenhuma dessas quatro identidades possui, no estado
auditado do repositório, o manifesto e o conjunto de evidências exigidos por
`inst.md`.

**DERIVADO:** o gate encerrou com o estado normativo
`BLOCKED_MISSING_VALIDATED_ARTIFACTS`. As fases Q1–Q5 não foram executadas,
pois construir os dois divisores em guia ou duplicar a cavidade v7 converteria
uma hipótese reprovada em componente supostamente validado.

**SIMULADO:** a reconstrução exploratória v7 foi aberta somente para inspeção
no AEDT/HFSS 2024 R2. O projeto permaneceu byte a byte inalterado e a sessão
gráfica foi deixada aberta para auditoria humana.

## 2. Commit, branch e ambiente

| Campo | Valor | Classe |
|---|---|---|
| branch | `research/mimo-2x2-four-radiators-waveguide` | DERIVADO |
| commit de partida | `5c802e19a1fabfb71d98d7a32365f334fa26c28b` | DERIVADO |
| Python | 3.12.10 | DERIVADO |
| PyAEDT | 1.3.0 | DERIVADO |
| AEDT | 2024.2.0, token lógico 242 | SIMULADO |
| transporte | gRPC nativo do AEDT via PyAEDT | SIMULADO |
| licença no pré-flight | disponível | SIMULADO |
| recursos previstos para solve | 14 cores, 1 task, 0 GPU | DERIVADO |
| sistema | Windows 11, 20 processadores lógicos, 42.677.538.816 bytes de RAM | DERIVADO |

O pré-flight completo está em `artefatos/preflight/`. No baseline, os 32 testes
existentes passaram e o lint não encontrou ocorrências. O verificador de
matemática apontou delimitadores legados no documento consolidado; eles foram
normalizados durante esta atualização.

## 3. Artefatos de entrada e busca Q0

**DERIVADO:** a busca recursiva usou as extensões `.aedt`, `.a3dcomp`, `.step`,
`.stp`, `.sat`, `.x_t`, `.s1p`, `.s2p`, `.s3p`, `.s4p`, `.ffd`, `.json`,
`.yaml` e `.csv`.

| Resultado | Quantidade | Interpretação |
|---|---:|---|
| arquivos inventariados | 296 | arquivos candidatos e evidências correlatas |
| projetos `.aedt` no escopo auditado | 22 | inclui cópias de runs e checkpoints |
| hashes `.aedt` distintos | 19 | versões/checkpoints, não radiadores independentes |
| manifestos `RAD_A1/A2/B1/B2` válidos | 0 | bloqueio Q0 |
| `.a3dcomp` encontrados | 0 | nenhum componente 3D versionado |
| Touchstone multiporta válido | 0 | existe apenas S1P da v7 |
| padrões embarcados complexos por radiador | 0 | requisito Q0 ausente |

**HIPÓTESE:** todos os 22 projetos candidatos pertencem a três famílias
exploratórias: smoke M0, reconstrução v5/v6 ou reconstrução v7. Cópias com
hash diferente podem refletir estados de build, solução ou configuração, mas
não criam quatro identidades físicas validadas.

Dois documentos citados pela instrução também estão ausentes:

- `docs/30_implementacao_aedt_2024r2.md`;
- `docs/31_planejamento_mimo_2x2_quatro_radiadores_guia.md`.

A Issue #6 confirma a mesma dependência Q0, mas não fornece os arquivos.

## 4. Classificação dos três grupos de projeto

### 4.1 Smoke M0

**SIMULADO:** o smoke M0 convergiu como cavidade PEC fechada em Eigenmode e
validou infraestrutura, licença, gRPC, malha e encerramento de processo.

**DERIVADO:** ele não possui waveport, campo distante ou comportamento de
radiador. Portanto não pode ser importado como `RAD_A1`–`RAD_B2`.

### 4.2 Reconstrução v5

**HIPÓTESE:** o manifesto registra estado `BUILT` e `solve_requested=false`.
Não há regressão eletromagnética individual, Touchstone validado, padrão
complexo ou fechamento de potência.

### 4.3 Reconstrução v7

**SIMULADO:** a v7 possui solve convergido, waveport com linha de integração em
Z, S1P, malha, campos e relatórios. Entretanto:

- passividade estrita: `FAIL`, com excesso radiado/aceito de 2,16235%;
- correspondência de S11: `FAIL`;
- S11 em 25,87 GHz: −0,997 dB;
- mínimo de S11: −2,369 dB em 26,22 GHz;
- classificação global: `HIPÓTESE`.

**DERIVADO:** convergência de `MaxDeltaS` não compensa falha de passividade nem
divergência de matching. A v7 é um candidato de pesquisa, não um componente
Q0 validado.

## 5. Geometria observada no HFSS

**SIMULADO:** a inspeção em sessão gráfica capturou:

| Item | Valor |
|---|---:|
| objetos | 11 |
| sólidos | 10 |
| folhas | 1 |
| fronteiras | 2 |
| excitações | 1 |
| setups | 1 |
| sweeps | 2 |
| relatórios | 8 |
| plots de campo | 8 |
| sistemas locais de corte | 8 |
| estudos paramétricos | 3 |
| operações explícitas de mesh | 0 |
| erros de extração | 0 |

Objetos: `Cavity_Air`, `FR4_Slab`, `Housing_Cavity`, `MountHole_L`,
`MountHole_R`, `Open_Region`, `Port_WR28_Sheet`, `Rod_PEC_NE`, `Rod_PEC_NW`,
`Rod_PEC_SE` e `Rod_PEC_SW`.

**SIMULADO:** o SHA-256 do projeto antes e depois da inspeção foi
`c65aac7fa669d6b98264081712e29c335eb1f1ae1f72d40d0eac61921573ad4d`.
Logo, a inspeção não salvou nem modificou o modelo.

### 5.1 Estado operacional da sessão deixada aberta

**SIMULADO:** a sessão gráfica AEDT 2024.2 permaneceu aberta no processo
`ansysedt` PID 22204, porta gRPC 49782, e respondeu ao último teste de saúde.
O projeto principal conservou o mesmo SHA-256.

**DERIVADO:** enquanto a sessão está aberta, o AEDT administra estado
transitório no diretório `.aedtresults`. O manifesto global registrou 24
arquivos efêmeros excluídos, dos quais um lock ativo e 20 arquivos temporários
gerados pela sessão. Também registrou sete caches versionados temporariamente
ausentes da árvore de trabalho. Nenhum desses estados foi promovido ao pacote:
o inventário científico contém 518 arquivos, e a lista nominal de exclusões e
ausências está em `poros_aedt/manifest.json`.

**INFERIDO:** fechar normalmente a interface permitirá ao próprio AEDT
finalizar ou descartar seus caches privados. Não se removeu nem restaurou
manualmente arquivo sob posse da sessão, evitando corromper a solução aberta.

## 6. Porta, fronteiras, setup e sweeps

**SIMULADO:** a excitação ativa é `P1_WR28_TE10:1`; a fronteira de porta é
`P1_WR28_TE10` e a região aberta usa `Radiation_Open_5Faces`.

O setup `Setup_Driven_25p87_HIPOTESE` usa 25,87 GHz, `MaxDeltaS=0,02`, máximo
de 15 passes, mínimo de dois passes e dois passes convergidos, refinamento de
20% e solver direto. As sweeps presentes são:

- `Sweep_25_27GHz`;
- `Sweep_Fields_Article`.

**SIMULADO:** o run limpo convergiu em quatro passes com `MaxDeltaS=0,0041377`
e 33.723 tetraedros. Não há operação local explícita de malha no projeto.

## 7. Cortes, campos e relatórios

**SIMULADO:** foram confirmados os oito sistemas locais:

`Cut_ZX_ArrayCenter`, `Cut_XY_MidHeight`, `Cut_YZ_Slot1`, `Cut_YZ_Slot2`,
`Cut_YZ_Slot3`, `Cut_YZ_Slot4`, `Cut_YZ_Slot5` e `Cut_ZX_Port`.

Os oito plots são `EMag_ZX_ArrayCenter_25p87`, `EMag_XY_MidHeight_25p87`,
`EMag_YZ_Slot1_25p87` a `EMag_YZ_Slot5_25p87` e
`EMag_ZX_Port_25p87`. Os oito relatórios previamente configurados cobrem S11,
eficiências, ganho realizado, cortes E/H co- e cross-polarizados e ganho 3D.

**DERIVADO:** esses plots são do candidato v7 de uma porta. Eles não equivalem
aos quatro padrões embarcados vetoriais complexos necessários para ECC e MIMO.

## 8. Rede em guia, matching e estados modais

**DESCONHECIDO:** nenhuma rede de três portas `P_EXT/P_OUT_1/P_OUT_2` foi
encontrada. Não há S3P, geometria de divisor 1:2, íris, poste, taper, degrau de
matching ou referência de fase comum validada.

**DERIVADO:** embora as dimensões nominais WR-28 de 7,11 mm × 3,56 mm sejam
publicadas para a alimentação do artigo, elas não autorizam definir dimensões
das junções, comprimentos de ramo, bends ou elementos de matching do novo
sistema.

**DESCONHECIDO:** `EVEN`, `ODD` e `QUADRATURE` não foram resolvidos. Seus
comprimentos de fase dependem da seção realmente validada, da carga complexa
dos radiadores e da dispersão full-wave.

## 9. Pares, quatro portas e sistema completo

**DESCONHECIDO:** Q2, Q3 e Q4 permanecem não construídos. Consequentemente não
existem `feed_A.s3p`, `feed_B.s3p`, `radiators_open.s4p` ou `system.s2p`.

Nenhuma afirmação é feita para:

- amplitude e fase entregue a cada radiador;
- acoplamento dentro ou entre pares;
- active S-parameters e TARC do sistema;
- eficiência ativa;
- ECC de campo, CCL ou MEG;
- valores singulares, rank efetivo ou capacidade;
- benefício de `EVEN/ODD` sobre `EVEN/EVEN`.

## 10. Balanço de potência, ganho e eficiência

**SIMULADO:** para a v7 em 25,87 GHz, com normalização declarada de 1 W
incidente, foram extraídos 0,38535475 W aceitos e 0,39368747 W radiados. O pico
de ganho realizado foi 3,28777 dBi.

**DERIVADO:** como a potência radiada excede a aceita, esse conjunto reprova o
gate de passividade. Os valores são evidência diagnóstica e não baseline de
radiador validado.

## 11. MIMO, canal e benchmarks

**DESCONHECIDO:** sem dois padrões externos complexos e sem S2P válido, ECC,
TARC, CCL, MEG, rank e capacidade não podem ser calculados com significado
físico para a arquitetura solicitada.

**DERIVADO:** executar fórmulas MIMO com padrões duplicados ou sintéticos neste
gate produziria apenas um exemplo matemático, não evidência do sistema. Os
benchmarks B0–B6 e os modelos de canal H0–H5 permanecem planejados.

## 12. Sensibilidade e robustez

**HIPÓTESE:** três estudos existem no projeto v7 — chanfro, largura e altura do
degrau — mas não foram executados. A campanha Q5 de tolerâncias não pode
preceder a seleção e validação Q1–Q4.

## 13. Falhas, limitações e decisões

| Gate/tema | Estado | Evidência | Decisão |
|---|---|---|---|
| Q0 — quatro radiadores | BLOCKED | 0/4 manifestos válidos | parar |
| v7 — convergência adaptativa | PASS local | 4 passes, ΔS 0,0041377 | preservar como diagnóstico |
| v7 — passividade | FAIL | +2,16235% radiado/aceito | não promover |
| v7 — matching publicado | FAIL | S11 muito acima de −10 dB | não promover |
| Q1 — redes 1:2 | NÃO EXECUTADO | Q0 bloqueado | não inventar geometria |
| Q2–Q5 | NÃO EXECUTADO | dependência de Q0/Q1 | não mascarar gate anterior |

Risco principal: duplicar quatro vezes a v7 produziria uma montagem visualmente
completa, porém cientificamente inválida. As métricas MIMO herdariam a mesma
incerteza de geometria, matching, potência e padrão.

## 14. Ação necessária para liberar Q0

Para cada identidade `RAD_A1`, `RAD_A2`, `RAD_B1` e `RAD_B2`, fornecer:

1. projeto `.aedt` ou `.a3dcomp` de origem;
2. SHA-256 e commit de origem;
3. AEDT/PyAEDT, design, solução e porta TE10;
4. sistema de coordenadas e orientação;
5. materiais, fronteiras, setup, sweeps e malha;
6. convergência e regressão contra referência;
7. Touchstone;
8. padrão `Etheta/Ephi` complexo com fase, real e imaginário;
9. ganho, eficiência e balanço de potência;
10. relatório de validação com gates explícitos.

Somente então podem ser criados os manifestos em
`modelos/componentes_validados/RAD_*/manifest.json` e iniciada Q1.

## 15. Matriz de evidências

| Claim | Valor | Unidade | Frequência | Modelo | Evidência | Artefato | SHA-256 |
|---|---:|---|---|---|---|---|---|
| inventário Q0 | 296 | arquivos | N/A | repositório | DERIVADO | `artefatos/q0/artifact_inventory.json` | `c98b01b6e7f118d95f20a2f7f0fb0364d81fc2e6f6edce0875f1c7daeee558be` |
| radiadores Q0 validados | 0 de 4 | instâncias | banda não definida | RAD_A1–RAD_B2 | DESCONHECIDO | `artefatos/q0/missing_validated_models.json` | `a1c3a780fa0eb47fd03ccddd5605f4efed18f51724122902c05faf60de8d93f4` |
| projeto inspecionado sem alteração | verdadeiro | booleano | N/A | v7 | SIMULADO | `artefatos/q0/hfss_inspection/hfss_inspection.json` | `f9c9de4c366d97c3c6e7e03f2ad6b3606b87480050a4395c74b47491b40cc496` |
| waveport em Z | PASS | gate | 25,87 GHz | v7 | SIMULADO | validação v7 | `e9566b6e4e70db533bcbd97c4adda5ac11a018803975a029ea286b4842269dd0` |
| convergência adaptativa | PASS | gate | 25,87 GHz | v7 | SIMULADO | `convergence.csv` | `9700a1dd530c380852a00fff7591bf18f94c1b0ca24847154592c99f21b7c508` |
| passividade estrita | FAIL | gate | 25,87 GHz | v7 | SIMULADO | validação v7 | `e9566b6e4e70db533bcbd97c4adda5ac11a018803975a029ea286b4842269dd0` |
| S1P de diagnóstico | disponível | arquivo | 25–27 GHz | v7 | SIMULADO | `sparameters.s1p` | `03f0f1f39d9160c443f09a835ef91b1eb391e544dd5d4ed98d2263ae618fde88` |
| S2P MIMO | ausente | arquivo | banda não definida | Q4 | DESCONHECIDO | bloqueio Q0 | N/A |
| padrões complexos por porta externa | ausentes | conjunto | banda não definida | Q4 | DESCONHECIDO | bloqueio Q0 | N/A |
| ECC/rank/capacidade | não calculados | métricas | banda/canal não definidos | Q4 | DESCONHECIDO | bloqueio Q0 | N/A |

## 16. Resumo obrigatório da fase

```text
FASE: Q0 — localizar e congelar quatro estruturas validadas
STATUS: BLOCKED_MISSING_VALIDATED_ARTIFACTS
COMMIT: 5c802e19a1fabfb71d98d7a32365f334fa26c28b (commit de partida)
ARQUIVOS ALTERADOS: preflight, auditor Q0, inspetor HFSS, testes e documentação
TESTES: 35 testes aprovados; ruff, compilação, fórmulas e integridade aprovados
ARTEFATOS: preflight, inventário Q0, relatório de bloqueio, inspeção e preview HFSS
RESULTADOS: 22 AEDT/19 hashes; 0/4 radiadores validados; v7 aberta sem alteração
LIMITAÇÕES: ausência dos componentes, S3P/S4P/S2P e padrões complexos individuais
RISCOS: promover cópias exploratórias e produzir claims MIMO sem evidência
PRÓXIMO GATE: Q0 continua; fornecer os quatro pacotes validados
```
