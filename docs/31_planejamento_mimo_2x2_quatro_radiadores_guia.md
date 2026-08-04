# 31 — Planejamento do sistema MIMO 2×2 com quatro radiadores e alimentação por guia de onda

## 1. Objetivo

Planejar uma arquitetura de transmissão com **quatro estruturas radiantes completas**, organizadas em **dois pares**, em que cada par é alimentado por uma rede em guia de onda com uma entrada externa própria.

A topologia de referência é:

```text
Porta RF 1
   │
   └── Rede em guia WG-A ──┬── Radiador A1
                            └── Radiador A2

Porta RF 2
   │
   └── Rede em guia WG-B ──┬── Radiador B1
                            └── Radiador B2
```

A arquitetura possui:

- **2 portas RF externas**;
- **2 cadeias de transmissão**;
- **4 radiadores físicos**;
- **2 super-elementos radiantes**, cada um formado por duas estruturas;
- avaliação de sistema **MIMO 2×2** quando combinada com duas portas independentes no receptor ou com um modelo de canal equivalente 2×2.

É importante não confundir essa arquitetura com MIMO 4×4. Os quatro radiadores não são quatro portas RF independentes. Cada par é excitado por uma única entrada externa e forma um padrão embarcado de nível sistêmico.

## 2. Premissa e rastreabilidade

Este planejamento adota como premissa fornecida pelo pesquisador que as quatro estruturas individuais já foram validadas no HFSS.

Antes de iniciar qualquer otimização conjunta, os artefatos individuais devem ser incorporados e congelados no repositório:

- arquivo `.aedt` de cada estrutura validada;
- geometria exportada ou 3D Component;
- versão do AEDT e PyAEDT;
- frequência central e banda validada;
- malha e histórico de convergência;
- Touchstone da porta individual;
- ganho realizado, eficiência e padrão vetorial complexo;
- campos de abertura;
- materiais e perdas;
- commit ou hash de cada modelo;
- relatório de validação individual.

Cada instância deve receber uma identidade imutável:

```text
RAD-A1
RAD-A2
RAD-B1
RAD-B2
```

Caso as quatro estruturas sejam cópias físicas do mesmo modelo, elas ainda devem ser tratadas como instâncias diferentes, pois posição, orientação, ambiente de acoplamento e conexão ao guia modificam seus padrões embarcados.

## 3. Tese da arquitetura

A arquitetura não deve ser projetada apenas como um divisor de potência 1:2 duplicado. O guia de onda e a relação de fase entre as duas saídas de cada par passam a integrar a síntese eletromagnética.

Para o par `k`, a excitação das duas estruturas pode ser escrita como:

```math
\mathbf a_k=
\frac{1}{\sqrt{|A_{k1}|^2+|A_{k2}|^2}}
\begin{bmatrix}
A_{k1}e^{j\phi_{k1}}\\
A_{k2}e^{j\phi_{k2}}
\end{bmatrix}.
```

O campo embarcado do par é:

```math
\mathbf F_k(\Omega,f)=
 a_{k1}\mathbf F_{k1}(\Omega,f)
+
 a_{k2}\mathbf F_{k2}(\Omega,f).
```

O objetivo não é somente maximizar o ganho de cada par. É produzir dois padrões de nível sistêmico,

```math
\mathbf F_A(\Omega,f)
\quad\text{e}\quad
\mathbf F_B(\Omega,f),
```

que sejam simultaneamente:

- bem casados;
- eficientes;
- suficientemente isolados;
- úteis no setor angular desejado;
- de baixa correlação no ambiente de propagação;
- capazes de sustentar dois valores singulares relevantes.

## 4. Estratégias modais

### 4.1 Estratégia de referência — TE10 monomodo

A primeira arquitetura deve usar o modo dominante `TE10` em todas as seções WR-28 e manter cada ramo abaixo do corte dos modos superiores.

Motivos:

- é o modo já compatível com as portas validadas;
- possui polarização e distribuição de campo conhecidas;
- reduz conversão modal não controlada;
- facilita de-embedding e fabricação;
- oferece a referência mais limpa para comparar o sistema com as estruturas individuais.

O modo `TE10` será excitado na entrada de cada rede. A rede define a relação de amplitude e fase entre seus dois ramos.

### 4.2 Supermodo par

Excitação de referência:

```math
\mathbf a_{\mathrm{even}}=
\frac{1}{\sqrt{2}}
\begin{bmatrix}
1\\
1
\end{bmatrix}.
```

Propriedades esperadas:

- soma coerente no broadside ou na direção de projeto;
- maior ganho no lóbulo principal;
- padrão mais próximo de um subarranjo convencional de dois elementos;
- boa referência para o primeiro par.

### 4.3 Supermodo ímpar

Excitação:

```math
\mathbf a_{\mathrm{odd}}=
\frac{1}{\sqrt{2}}
\begin{bmatrix}
1\\
-1
\end{bmatrix}.
```

O guia continua localmente em `TE10`; a diferença de 180° é criada pela rede de alimentação, por diferença de comprimento, inversão de orientação, híbrida em guia ou transformação equivalente.

Propriedades esperadas:

- padrão complementar ao modo par;
- possível nulo em broadside;
- maior diversidade angular;
- potencial redução de correlação entre os dois super-elementos.

### 4.4 Excitação em quadratura

```math
\mathbf a_{90}=
\frac{1}{\sqrt{2}}
\begin{bmatrix}
1\\
j
\end{bmatrix}.
```

Deve ser estudada como variante para:

- deslocamento do máximo angular;
- síntese de padrão assimétrico;
- diversidade de fase;
- possível geração de polarização composta quando a orientação física permitir.

### 4.5 Seção multimodo real

Uma seção comum alargada poderá ser estudada posteriormente para suportar combinações `TE10/TE20` ou `TE10/TE01`.

Essa opção não pertence ao primeiro gate porque:

- aumenta o número de estados internos;
- exige launchers e filtros modais;
- pode introduzir ressonâncias e modos parasitas;
- dificulta atribuir o ganho MIMO à geometria radiante ou à rede modal;
- pode transformar cada porta física em um terminal multimodo, alterando a contagem de canais.

A seção multimodo somente avança após a arquitetura monomodo TE10 ser validada.

## 5. Arquiteturas candidatas

### C0 — dois pares idênticos, ambos em fase

```text
WG-A → [A1  0°] + [A2  0°]
WG-B → [B1  0°] + [B2  0°]
```

Função:

- benchmark de integração;
- medir quanto o espaçamento, a orientação e o acoplamento entre pares produzem diversidade por si só.

Risco:

- padrões muito semelhantes;
- rank efetivo próximo de um em canais com baixa dispersão angular.

### C1 — par A par e par B ímpar

```text
WG-A → [A1  0°] + [A2    0°]
WG-B → [B1  0°] + [B2  180°]
```

Esta é a **arquitetura prioritária** para a primeira prova de diversidade por padrão.

Vantagens:

- duas bases espaciais claramente distintas;
- implementação passiva;
- comparação direta entre supermodos par e ímpar;
- evita exigir modos superiores no guia de entrada.

### C2 — pares com polarizações ortogonais

O par B é rotacionado ou configurado para radiar polarização ortogonal ao par A.

Vantagens:

- diversidade polarimétrica forte;
- robustez em ambientes com despolarização;
- menor correlação em muitos cenários.

Riscos:

- alteração mecânica;
- dificuldade de manter as mesmas características de ganho e cobertura;
- necessidade de analisar XPD e acoplamento polarimétrico.

### C3 — par A em fase e par B em quadratura

```text
WG-A → [A1  0°] + [A2   0°]
WG-B → [B1  0°] + [B2  90°]
```

Função:

- explorar diversidade angular sem introduzir um nulo profundo em broadside.

### C4 — pares espacialmente deslocados e/ou espelhados

Variáveis:

- separação entre elementos de cada par;
- separação entre centros dos pares;
- deslocamento longitudinal;
- deslocamento vertical;
- espelhamento;
- rotação de 180°;
- rotação de 90°;
- inclinação mecânica.

A orientação deve ser otimizada junto com a rede de alimentação, não depois.

## 6. Decomposição eletromagnética

A arquitetura deve ser validada em blocos para evitar um solve monolítico sem diagnóstico.

### Bloco R — radiadores

Modelo interno de quatro portas:

```text
R1 = porta do radiador A1
R2 = porta do radiador A2
R3 = porta do radiador B1
R4 = porta do radiador B2
```

Extrair:

- matriz `S_R` 4×4;
- padrões embarcados de cada radiador;
- potência aceita;
- acoplamento mútuo entre todas as estruturas.

### Bloco F — redes de alimentação

Cada rede é inicialmente um bloco de três portas:

```text
F-A: entrada P1, saídas R1 e R2
F-B: entrada P2, saídas R3 e R4
```

Extrair:

- `S_F_A` e `S_F_B`;
- balanço de amplitude;
- fase relativa;
- perda de inserção;
- retorno nas três portas;
- conversão modal;
- sensibilidade a tolerâncias.

### Bloco S — sistema integrado

Depois da conexão interna, as únicas portas externas são:

```text
P1 = entrada do par A
P2 = entrada do par B
```

O sistema completo é uma rede de duas portas com dois padrões embarcados externos.

Devem ser extraídos:

- matriz `S_SYS` 2×2;
- padrões embarcados de `P1` e `P2`;
- TARC para conjuntos de excitação definidos;
- eficiência ativa;
- correlação de campo;
- valores singulares do canal.

## 7. Rede em guia de onda

### 7.1 Topologia inicial

A primeira rede deve ser um divisor em guia de onda com:

- uma entrada WR-28;
- duas saídas compatíveis com as portas das estruturas;
- junção em plano E ou plano H avaliada por DOE;
- seções de transformação de impedância;
- possibilidade de poste, íris ou degrau de matching;
- trechos de fase independentes;
- geometria simétrica na versão em fase;
- assimetria controlada na versão de 180° ou 90°.

### 7.2 Variáveis principais

```text
wg_input_a, wg_input_b
junction_type
junction_length
branch_a, branch_b
branch_length_1, branch_length_2
phase_trim_1, phase_trim_2
iris_width, iris_height, iris_position
post_diameter, post_position
bend_radius
output_spacing
output_rotation
pair_spacing
interpair_spacing
```

### 7.3 Relação de fase

A primeira estimativa de diferença de comprimento para uma fase alvo é:

```math
\Delta L(f_0)=
\frac{\Delta\phi}{\beta_g(f_0)}.
```

Para 180°:

```math
\Delta L_{180}(f_0)=\frac{\pi}{\beta_g(f_0)}=\frac{\lambda_g(f_0)}{2}.
```

Para 90°:

```math
\Delta L_{90}(f_0)=\frac{\pi/2}{\beta_g(f_0)}=\frac{\lambda_g(f_0)}{4}.
```

Como `\lambda_g` varia com a frequência, uma simples diferença de comprimento será inicialmente estreita em banda. O DOE deve comparar:

- linha de atraso simples;
- fase por seção carregada;
- degraus de impedância;
- híbrida ou inversor de fase em guia;
- solução otimizada para banda.

## 8. Hierarquia de modelos HFSS

Para não confundir com os modelos G0/M0–M4, esta campanha usará a série `Q`.

### Q0 — radiador individual congelado

- importar a geometria validada;
- confirmar hash e versão;
- repetir um solve mínimo de regressão;
- não alterar dimensões internas.

### Q1 — rede de alimentação isolada

- três wave ports;
- sem radiadores;
- otimizar matching, balanço e fase;
- terminar as saídas em impedâncias modais equivalentes.

### Q2 — um par completo

- dois radiadores;
- uma rede de alimentação;
- uma porta externa;
- comparar supermodo par, ímpar e quadratura;
- extrair padrão embarcado do par.

### Q3 — quatro radiadores sem redes

- quatro portas individuais;
- mapear o acoplamento mútuo completo;
- determinar a matriz de interação antes da integração.

### Q4 — sistema completo de duas portas

- quatro radiadores;
- duas redes em guia;
- duas portas externas;
- solução Driven Modal completa;
- padrões embarcados de P1 e P2.

### Q5 — robustez e fabricação

- condutividade real;
- rugosidade;
- gaps;
- flange e parafusos;
- desalinhamento;
- tolerâncias de usinagem;
- Monte Carlo ou Latin Hypercube.

### Q6 — canal MIMO

- importar os padrões externos complexos;
- aplicar modelos de canal;
- calcular rank, ECC, CCL, MEG e capacidade;
- comparar com dois radiadores isolados e quatro radiadores alimentados independentemente.

## 9. Estratégia de simulação

### 9.1 Frequência

Usar como referência a banda já validada da estrutura individual. A campanha deve incluir:

- frequência central validada;
- banda de −10 dB validada;
- margem inferior e superior para observar modos parasitas;
- pontos densos para fase e padrão.

### 9.2 Solvers

- `Driven Modal` para redes e sistema integrado;
- `Eigenmode` em seções alargadas ou cavidades de junção quando houver suspeita de ressonância;
- sweep discreto nos pontos usados para campo distante;
- sweep interpolante apenas depois da validação dos pontos discretos.

### 9.3 Domínio aberto

Comparar:

- Radiation Boundary;
- PML;
- distância do airbox;
- convergência do campo distante.

### 9.4 Malha

Refinar em:

- ranhuras;
- junções dos guias;
- íris e postes;
- descontinuidades de fase;
- flanges;
- gaps;
- regiões de forte corrente superficial;
- interfaces entre guia e radiador.

### 9.5 Reuso de geometria

As estruturas validadas devem ser reutilizadas por:

- 3D Component versionado; ou
- módulo geométrico imutável com hash; ou
- duplicação controlada do mesmo grupo de objetos.

Não reconstruir manualmente quatro vezes a estrutura validada.

## 10. Espaço de projeto

### 10.1 Variáveis discretas

- topologia da junção: plano E, plano H, híbrida;
- estado do par: `EVEN`, `ODD`, `QUADRATURE`;
- orientação do par B: 0°, 90°, 180°;
- polarização: co-polar, cross-polar;
- rede simétrica ou assimétrica;
- uso de íris, poste ou degrau.

### 10.2 Variáveis contínuas

- separação interna do par;
- separação entre pares;
- comprimento dos ramos;
- comprimento de fase;
- dimensões de matching;
- offsets espaciais;
- ângulos de orientação;
- dimensões de transições;
- posição de elementos de supressão modal.

### 10.3 Ordem de otimização

1. rede isolada, sem radiadores;
2. um par conectado;
3. acoplamento entre quatro radiadores sem redes;
4. sistema completo;
5. objetivos MIMO;
6. robustez e fabricação.

Não otimizar todos os parâmetros simultaneamente desde o primeiro solve.

## 11. Funções objetivo

### 11.1 Rede de alimentação

```math
J_F=
 w_1L_{\mathrm{return}}
+w_2L_{\mathrm{imbalance}}
+w_3L_{\mathrm{phase}}
+w_4L_{\mathrm{insertion}}
+w_5L_{\mathrm{mode\ conversion}}.
```

### 11.2 Par radiante

```math
J_P=
 w_1L_{S_{11}}
+w_2L_{\eta}
+w_3L_{\mathrm{pattern}}
+w_4L_{\mathrm{ripple}}
+w_5L_{\mathrm{SLL}}.
```

### 11.3 Sistema MIMO

```math
J_{MIMO}=
 w_1L_{\mathrm{TARC}}
+w_2L_{\mathrm{ECC}}
+w_3L_{\mathrm{rank}}
+w_4L_{\mathrm{capacity}}
+w_5L_{\mathrm{efficiency}}
+w_6L_{\mathrm{coverage}}.
```

A otimização deve ser multiobjetivo. Uma solução que maximize capacidade sacrificando eficiência, cobertura ou fabricabilidade não será aceita automaticamente.

## 12. Métricas obrigatórias

### Rede e portas

- `S11`, `S22` externos;
- `S21` entre as duas entradas externas;
- perdas de inserção internas;
- balanço de potência entre os dois radiadores do par;
- fase relativa por frequência;
- pureza modal;
- active reflection coefficient;
- TARC.

### Radiação

- ganho realizado por porta externa;
- eficiência de radiação;
- eficiência total;
- `Eθ` e `Eφ` complexos;
- beamwidth;
- ripple;
- SLL;
- cross-polarização;
- phase center;
- cobertura angular conjunta;
- campos de abertura.

### MIMO

- ECC de campo isotrópica;
- ECC ponderada pelo canal;
- diversity gain;
- MEG;
- CCL;
- matriz de Gram dos padrões;
- valores singulares;
- condição numérica;
- rank efetivo;
- capacidade mediana;
- capacidade no percentil 5%;
- outage.

## 13. Modelos de canal

A validação não deve depender de um único ambiente.

### H0 — isotrópico

Referência matemática, não cenário de mercado.

### H1 — Laplaciano de baixa dispersão

Representa enlace direcional ou corredor angular estreito.

### H2 — Laplaciano de média dispersão

Representa ambiente urbano ou indoor com múltiplos clusters.

### H3 — LOS com componente especular dominante

Avaliar a sensibilidade do rank à orientação e ao espaçamento.

### H4 — canal polarimétrico

Incluir XPR e rotação de polarização.

### H5 — canal medido

Quando dados reais estiverem disponíveis, substituir ou complementar os modelos sintéticos.

## 14. Critérios iniciais de aceite

Os valores abaixo são **metas de engenharia**, não resultados já obtidos.

### Gate Q1 — rede isolada

- retorno externo melhor que −15 dB na frequência central;
- retorno melhor que −10 dB na banda de operação;
- desequilíbrio de amplitude menor que 0,5 dB;
- erro de fase menor que ±5° no ponto central;
- perda de inserção adicional minimizada e documentada;
- ausência de modo superior propagante não planejado.

### Gate Q2 — par completo

- degradação de eficiência claramente quantificada;
- padrão correspondente ao estado par, ímpar ou quadratura;
- balanço de potência residual inferior a 2%;
- convergência simultânea de S-parameters e campo distante;
- diferença de fase nas portas radiantes dentro da meta.

### Gate Q4 — sistema completo

- `S11` e `S22` melhores que −10 dB na banda alvo;
- isolamento externo melhor que −15 dB, com meta estendida de −20 dB;
- eficiência total por porta preferencialmente superior a 75%, ou perda relativa inferior a 1 dB contra o benchmark;
- ECC de campo inferior a 0,10 no cenário de referência;
- rank efetivo próximo de 2 em pelo menos um conjunto relevante de canais;
- ganho de capacidade demonstrado contra C0 e contra dois radiadores correlacionados;
- ausência de benefício obtido apenas por diferença de potência total.

## 15. Comparações obrigatórias

A arquitetura proposta deve ser comparada com:

1. um único radiador;
2. dois radiadores independentes, um por porta;
3. quatro radiadores com dois pares em fase;
4. par A par e par B ímpar;
5. polarizações ortogonais;
6. quatro radiadores idealmente alimentados por quatro portas, como limite superior;
7. sistema com mesma potência total, mesma abertura e mesma banda.

## 16. Estrutura de software planejada

```text
src/enz_eigenchannel_mimo/
├── pair_feed/
│   ├── spec.py
│   ├── modes.py
│   ├── waveguide.py
│   ├── junctions.py
│   ├── phase_network.py
│   └── validation.py
├── four_radiator/
│   ├── spec.py
│   ├── placement.py
│   ├── assembly.py
│   ├── coupling.py
│   └── campaign.py
├── mimo2x2/
│   ├── embedded_patterns.py
│   ├── active_network.py
│   ├── channel_models.py
│   ├── eigenchannels.py
│   └── metrics.py
└── aedt/
    ├── component_import.py
    ├── modal_export.py
    └── full_system_post.py
```

Especificações:

```text
modelos/especificacoes/
├── q0_validated_radiator.yaml
├── q1_pair_feed_even.yaml
├── q1_pair_feed_odd.yaml
├── q2_pair_complete.yaml
├── q3_four_radiators_open_ports.yaml
├── q4_mimo2x2_four_radiators.yaml
└── q5_tolerance_campaign.yaml
```

## 17. Artefatos por campanha

```text
artefatos/runs/<run_id>/
├── spec.yaml
├── source_components.json
├── geometry_manifest.json
├── network_topology.json
├── modes.json
├── model.aedt
├── system.s2p
├── internal_network.s6p
├── pair_feed_A.s3p
├── pair_feed_B.s3p
├── convergence.csv
├── mesh_statistics.json
├── power_balance.json
├── embedded_patterns/
├── aperture_fields/
├── channel_ensemble/
├── mimo_metrics.json
├── plots/
└── report.md
```

## 18. Sequência de execução

### Fase 0 — congelamento

- importar as quatro estruturas validadas;
- registrar hashes;
- executar regressão de uma estrutura;
- confirmar portas e coordenadas.

### Fase 1 — rede do par

- criar divisor TE10 1:2;
- validar versão em fase;
- criar versão 180°;
- criar versão 90°;
- selecionar duas melhores redes.

### Fase 2 — um par completo

- conectar duas estruturas;
- validar matching e padrão;
- medir interação entre rede e radiadores;
- congelar `PAIR-EVEN` e `PAIR-ODD`.

### Fase 3 — quatro radiadores

- montar os dois pares;
- mapear acoplamento espacial;
- otimizar separação e orientação;
- escolher C1, C2 ou C3.

### Fase 4 — MIMO 2×2

- extrair padrões externos de P1 e P2;
- construir ensemble de canais;
- calcular métricas;
- comparar benchmarks.

### Fase 5 — robustez

- materiais reais;
- rugosidade;
- tolerâncias;
- gaps;
- temperatura quando aplicável;
- Monte Carlo.

### Fase 6 — protótipo

- detalhamento mecânico;
- flanges;
- metrologia de guia;
- calibração VNA;
- medição de padrão e MIMO.

## 19. Decisões tomadas neste planejamento

1. O sistema será tratado como **2 portas externas e 4 radiadores**, não como 4×4.
2. Cada par constitui um **super-elemento**.
3. O baseline usa `TE10` monomodo.
4. Modos par e ímpar serão criados por relação de fase entre os ramos, não pela introdução prematura de modos superiores.
5. A primeira arquitetura prioritária é `C1`: par A em fase e par B em oposição de fase.
6. A alternativa prioritária é `C2`: pares com polarizações ortogonais.
7. O projeto será decomposto em rede, radiadores, par e sistema.
8. O modelo completo somente será otimizado após validação das redes isoladas.
9. O benefício será demonstrado por padrões complexos, TARC, ECC de campo, valores singulares e capacidade.
10. Nenhum resultado será chamado de MIMO útil apenas por apresentar baixo `S21`.

## 20. Próximo gate

O próximo gate formal será:

```text
Q0-IMPORT-VALIDATED-FOUR
```

Critério:

- as quatro estruturas validadas estão importadas;
- cada uma possui hash, versão, porta e orientação registradas;
- o solve de regressão confirma o comportamento individual;
- nenhuma dimensão interna foi alterada;
- os quatro padrões embarcados individuais podem ser exportados.

Depois disso inicia-se:

```text
Q1-PAIR-FEED-TE10
```

com a síntese da rede em guia de onda para os estados `EVEN`, `ODD` e `QUADRATURE`.
