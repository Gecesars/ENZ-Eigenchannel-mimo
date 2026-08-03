# ENZ Eigenchannel MIMO

**Cavidades ressonantes inspiradas em epsilon-near-zero para síntese geométrica de feixes, geração de estados radiantes e desenvolvimento de arquiteturas MIMO multiporta em ondas milimétricas.**

![Status](https://img.shields.io/badge/status-pesquisa%20e%20valida%C3%A7%C3%A3o-blue)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![AEDT](https://img.shields.io/badge/Ansys%20AEDT-2024%20R2-orange)
![HFSS](https://img.shields.io/badge/HFSS-Eigenmode%20%7C%20Driven%20Modal-orange)
![Idioma](https://img.shields.io/badge/documenta%C3%A7%C3%A3o-pt--BR-green)
![License](https://img.shields.io/badge/c%C3%B3digo-Apache--2.0-green)

> **Estado científico:** teoria consolidada, reprodução geométrica em preparação e suíte Python para AEDT/HFSS 2024 R2 implementada.  
> **Estado numérico:** testes offline concluídos; nenhum resultado eletromagnético é considerado validado enquanto não houver execução licenciada no AEDT 2024 R2, convergência demonstrada e artefatos publicados.  
> **Próximo gate:** `AEDT-BUILD-01`, seguido por `AEDT-EIGENMODE-01`, `AEDT-DRIVEN-01`, `AEDT-POST-01` e `EM-VALIDATION-01`.

---

## Sumário

1. [Visão geral](#1-visão-geral)
2. [Tese científica](#2-tese-científica)
3. [Artigo-base do Inatel](#3-artigo-base-do-inatel)
4. [Problema de engenharia](#4-problema-de-engenharia)
5. [Hipótese original](#5-hipótese-original)
6. [Modelos G0: M0–M4](#6-modelos-g0-m0m4)
7. [Automação AEDT/HFSS 2024 R2](#7-automação-aedthfss-2024-r2)
8. [Arquitetura do código](#8-arquitetura-do-código)
9. [Instalação](#9-instalação)
10. [Uso rápido](#10-uso-rápido)
11. [Geometria científica e smoke seed](#11-geometria-científica-e-smoke-seed)
12. [Materiais e política do FR4](#12-materiais-e-política-do-fr4)
13. [Plano de validação](#13-plano-de-validação)
14. [Artefatos e rastreabilidade](#14-artefatos-e-rastreabilidade)
15. [Métricas eletromagnéticas e MIMO](#15-métricas-eletromagnéticas-e-mimo)
16. [Aplicações de mercado](#16-aplicações-de-mercado)
17. [Limitações atuais](#17-limitações-atuais)
18. [Roadmap](#18-roadmap)
19. [Estrutura do repositório](#19-estrutura-do-repositório)
20. [Contribuição, créditos e licença](#20-contribuição-créditos-e-licença)

---

## 1. Visão geral

Este repositório é uma plataforma aberta de pesquisa e engenharia para estudar, reproduzir, validar e ampliar uma classe de antenas baseada em cavidades metálicas operando próximas ao corte modal, em regime equivalente a **epsilon-near-zero estrutural**.

O objetivo inicial é reproduzir de forma auditável o modelo publicado por pesquisadores do Inatel em aproximadamente **25,87 GHz**. Em seguida, o projeto investigará se a mesma coerência de fase interna pode ser usada para criar:

- múltiplos padrões embarcados;
- diversidade espacial e polarimétrica;
- cavidades compartilhadas com várias portas;
- estados radiantes de baixa correlação;
- autocanais eletromagnéticos orientados à capacidade MIMO;
- dispositivos compactos de formação passiva de feixes e canais.

O repositório combina cinco frentes:

1. **fundamentação pós-doc** em Maxwell, teoria modal, ENZ, dopagem fotônica, aberturas e teoria da informação;
2. **reprodução científica** do artigo-base;
3. **automação completa** do Ansys Electronics Desktop 2024 R2 e HFSS via PyAEDT/gRPC;
4. **validação numérica e experimental** com rastreabilidade de dados;
5. **desenvolvimento de arquiteturas originais** multiporta e MIMO.

---

## 2. Tese científica

Em um guia retangular próximo ao corte do modo dominante, a constante de propagação longitudinal tende a valores pequenos:

```math
\beta_z=
\sqrt{k_0^2\varepsilon_r\mu_r-k_c^2}
\longrightarrow 0.
```

Consequentemente,

```math
\lambda_g=\frac{2\pi}{\beta_z}
\longrightarrow \infty,
```

e a fase acumulada ao longo de uma região de comprimento $L$ pode permanecer pequena:

```math
\Delta\phi=\beta_zL.
```

Essa baixa progressão de fase permite tratar uma cavidade extensa como uma abertura aproximadamente coerente em uma banda finita. A geometria deixa de ser apenas uma embalagem mecânica e passa a atuar como variável de síntese do campo.

A tese central deste projeto é:

```math
\boxed{
\text{fase coerente interna}
+
\text{geometria}
+
\text{portas}
+
\text{polarização}
+
\text{perturbações locais}
\longrightarrow
\text{base de estados radiantes úteis}
}
```

O encadeamento físico e sistêmico é representado por:

```math
\mathbf v(f)
\xrightarrow{\mathcal T}
\mathbf J(\mathbf r,f)
\xrightarrow{\mathcal R}
\mathbf F(\Omega,f)
\xrightarrow{\mathcal P}
\mathbf H(f),
```

onde:

- $\mathbf v$ contém as excitações complexas das portas;
- $\mathbf J$ representa as correntes induzidas;
- $\mathbf F$ reúne os padrões embarcados vetoriais;
- $\mathbf H$ é a matriz de canal efetiva.

O projeto não assume que várias portas geram automaticamente MIMO útil. A estrutura somente será considerada multiestado ou MIMO quando os padrões, perdas, acoplamentos e valores singulares demonstrarem graus de liberdade reais sob um ambiente de propagação declarado.

---

## 3. Artigo-base do Inatel

A referência experimental inicial é:

> **E. C. Vilas Boas, S. B. de Vasconcellos, A. C. Sodré Jr. e F. A. P. de Figueiredo**,  
> *A Millimeter-Wave Flat-Top Fan-Beam Antenna Array Based on a Geometry-Independent Resonant Cavity*,  
> IEEE Open Journal of Antennas and Propagation, 2026.  
> DOI: `10.1109/OJAP.2026.3703713`.

O trabalho demonstra uma cavidade ranhurada cuja geometria é modificada mantendo a área transversal. A transformação converte um feixe estreito em um feixe em leque de topo plano sem deslocamento relevante da frequência de ressonância.

Resultados publicados usados como alvos de reprodução:

| Parâmetro | Valor publicado |
|---|---:|
| Frequência central | aproximadamente 25,87 GHz |
| Área transversal inicial | 108 mm² |
| Seção inicial | 14 mm × 7,7143 mm |
| Guia de alimentação | WR-28 |
| Corte $TE_{10}$ informado | 21,08 GHz |
| Modelo inicial | 3 ranhuras |
| Modelo final | 5 ranhuras |
| Largura do degrau | 9 mm |
| Altura do degrau | 1 mm |
| Chanfros | 3 mm |
| Banda medida de −10 dB | 1,11 GHz |
| Largura de 1 dB | aproximadamente 60°–70° |
| Ripple máximo medido | inferior a 0,71 dB |
| Largura de 3 dB | superior a 80° |
| Ganho realizado máximo | 7,84 dBi |
| SLL | inferior a −10,02 dB |

O artigo, seus autores, laboratórios, instituições e agências de fomento são formalmente creditados em [`CREDITOS.md`](CREDITOS.md) e [`docs/01_artigo_base_inatel.md`](docs/01_artigo_base_inatel.md).

Dimensões não publicadas não serão inventadas. Cada grandeza recebe uma origem explícita:

- `PUBLISHED_TEXT`;
- `PUBLISHED_FIGURE`;
- `DERIVED`;
- `INFERRED`;
- `OPTIMIZED`;
- `HYPOTHESIS`;
- `UNKNOWN`.

---

## 4. Problema de engenharia

Antenas mmWave convencionais com controle fino de feixe normalmente exigem redes de alimentação complexas, phase shifters, amplificadores, calibração e grande número de interconexões. Essas soluções podem apresentar:

- perdas de inserção elevadas;
- custo e consumo de energia;
- sensibilidade a tolerâncias;
- dificuldades térmicas;
- calibração de amplitude e fase;
- aumento do volume e da massa;
- menor confiabilidade mecânica;
- complexidade de produção em grande escala.

A cavidade ENZ inspirada sugere uma abordagem alternativa: usar a própria física distribuída da estrutura para organizar a fase e redistribuir a amplitude nas aberturas.

A pergunta de engenharia é:

> Até que ponto uma cavidade passiva pode substituir parte da complexidade de uma rede ativa de formação de feixe ou de canais?

---

## 5. Hipótese original

A extensão proposta não consiste apenas em duplicar a antena original. A hipótese é que uma cavidade compartilhada ou um conjunto fortemente acoplado possa sustentar excitações diferentes na mesma banda, produzindo padrões embarcados distintos.

O primeiro experimento crítico será:

```math
\boxed{
\text{uma estrutura compartilhada}
+
\text{duas portas}
+
\text{dois estados radiantes úteis}
}
```

O sucesso exige simultaneamente:

- ressonâncias próximas ou sobrepostas;
- casamento ativo aceitável;
- eficiência de radiação adequada;
- controle do acoplamento e das perdas;
- padrões embarcados complexos distintos;
- correlação baixa no canal de interesse;
- melhoria de rank efetivo ou capacidade.

Somente após essa prova serão estudadas estruturas de quatro portas:

```math
4\ \text{portas}
=
2\ \text{famílias de padrão}
\times
2\ \text{polarizações}.
```

---

## 6. Modelos G0: M0–M4

A reprodução foi dividida em cinco modelos incrementais. Cada etapa isola uma parte da física e reduz a possibilidade de ajuste oculto.

### M0 — cavidade fechada

Objetivos:

- validar dimensões internas;
- localizar modos próprios;
- confirmar o comportamento próximo ao corte;
- identificar modos parasitas;
- analisar energia elétrica e magnética;
- preparar o modelo Eigenmode.

Configuração inicial:

- solução `Eigenmode`;
- faixa de busca de 18 a 32 GHz;
- até 12 modos;
- convergência de frequência alvo inferior a 0,1%.

### M1 — cavidade com três ranhuras

Objetivos:

- reproduzir o modelo inicial do artigo;
- criar alimentação WR-28;
- configurar wave port;
- validar $S_{11}$;
- verificar o pencil beam;
- extrair amplitude e fase em cada ranhura.

### M2 — cavidade com cinco ranhuras

Objetivos:

- preservar a área transversal;
- acrescentar duas ranhuras;
- verificar a invariância aproximada da ressonância;
- observar a formação do fan beam;
- comparar os campos de abertura com M1.

### M3 — perfil em degrau

Objetivos:

- incluir o degrau de 9 mm × 1 mm;
- estudar a redistribuição de amplitude;
- minimizar ripple;
- controlar beamwidth e SLL;
- mapear sensitividade da posição e extensão do degrau.

### M4 — modelo fabricável

Inclui:

- paredes com espessura real;
- material condutor real;
- inclusão dielétrica;
- pinos metálicos;
- chanfros;
- gaps e tolerâncias quando conhecidos;
- rugosidade;
- preparação para comparação FR4 versus materiais de baixa perda.

---

## 7. Automação AEDT/HFSS 2024 R2

A suíte Python foi construída especificamente para o **Ansys Electronics Desktop 2024 R2**.

Princípios obrigatórios:

- versão estrita `2024.2`;
- nenhum fallback silencioso para outra versão;
- importação tardia do PyAEDT;
- uma sessão AEDT por worker/processo;
- comunicação por gRPC nativo do AEDT;
- geometria declarativa e auditável;
- variáveis criadas antes dos objetos;
- nomes determinísticos;
- build separado de solve;
- preflight antes do uso de licença;
- validação após a construção;
- salvamento, reabertura e inventário dos artefatos;
- testes offline sem exigir AEDT.

Fluxo operacional:

```text
especificação científica
        ↓
plano geométrico independente de AEDT
        ↓
preflight offline
        ↓
worker Python
        ↓
PyAEDT
        ↓
gRPC nativo
        ↓
AEDT 2024 R2 / HFSS
        ↓
validação live
        ↓
solve e pós-processamento
        ↓
manifesto + hashes + artefatos
```

Modos suportados:

- `local_launch`: inicia uma sessão dedicada;
- `local_attach`: anexa a uma porta gRPC explícita;
- `non_graphical`: execução headless;
- `graphical`: inspeção manual e depuração.

A CLI não procura sessões ambiguamente. O attach exige porta conhecida.

---

## 8. Arquitetura do código

```text
src/enz_eigenchannel_mimo/
├── aedt/
│   ├── runtime.py       contrato e identidade do AEDT 2024.2
│   ├── session.py       ciclo de vida PyAEDT/gRPC
│   ├── materials.py     FR4 DOE e materiais candidatos
│   ├── builder.py       criação de objetos e operações HFSS
│   ├── validation.py    preflight offline e validação live
│   ├── artifacts.py     manifestos, inventário e SHA-256
│   ├── post.py          Touchstone e pós-processamento
│   ├── campaign.py      orquestração build/solve/export
│   └── cli.py           comando enz-aedt
├── geometry/
│   ├── spec.py          contrato científico das dimensões
│   ├── plan.py          plano CAD independente de PyAEDT
│   └── g0.py            geradores M0–M4
├── claims.py            classificação de evidências
└── metrics.py           métricas MIMO iniciais
```

A separação entre especificação, plano CAD e builder evita que decisões científicas fiquem escondidas em chamadas diretas ao modeler.

---

## 9. Instalação

### 9.1 Requisitos gerais

- Windows 10 ou 11 para execução com AEDT;
- Ansys Electronics Desktop 2024 R2 instalado;
- licença HFSS compatível;
- Python 3.11 ou 3.12;
- Git;
- espaço de armazenamento para projetos e resultados.

### 9.2 Instalação para documentação e testes offline

```bash
git clone https://github.com/Gecesars/ENZ-Eigenchannel-mimo.git
cd ENZ-Eigenchannel-mimo
git checkout feat/aedt-2024r2-geometry-validation
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Linux:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### 9.3 Instalação para AEDT/HFSS

Na máquina Windows com AEDT 2024 R2:

```powershell
py -3.12 -m venv .venv-aedt242
.\.venv-aedt242\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,aedt]"
```

A dependência AEDT está fixada para evitar alterações silenciosas de API:

```text
pyaedt==1.3.0
```

Antes de atualizar PyAEDT, toda a suíte deve ser executada novamente no AEDT 2024 R2.

---

## 10. Uso rápido

### 10.1 Testes offline

```bash
pytest -q
python -m compileall -q src scripts testes
python scripts/normalizar_formulas_markdown.py --check
```

Os testes offline verificam:

- normalização da versão AEDT;
- rejeição de fallback;
- regras de attach;
- contratos geométricos;
- geração dos planos M0–M4;
- contagem de ranhuras;
- materiais;
- preflight;
- builder com backend AEDT falso;
- bloqueio de hipóteses em execução científica.

### 10.2 Build gráfico sem solve

```powershell
enz-aedt M1 --graphical --allow-smoke-seed --output D:\ENZ\runs\M1
```

### 10.3 Build headless sem solve

```powershell
enz-aedt M4 --allow-smoke-seed --output D:\ENZ\runs\M4
```

### 10.4 Build e solve provisório

```powershell
enz-aedt M2 --allow-smoke-seed --solve --output D:\ENZ\runs\M2
```

### 10.5 Attach a uma sessão gRPC conhecida

```powershell
enz-aedt M4 \
  --allow-smoke-seed \
  --graphical \
  --attach-port 50051 \
  --output D:\ENZ\runs\M4_attach
```

### 10.6 Gerar todos os modelos para auditoria CAD

```powershell
enz-aedt M0 --allow-smoke-seed --output D:\ENZ\runs\M0
enz-aedt M1 --allow-smoke-seed --output D:\ENZ\runs\M1
enz-aedt M2 --allow-smoke-seed --output D:\ENZ\runs\M2
enz-aedt M3 --allow-smoke-seed --output D:\ENZ\runs\M3
enz-aedt M4 --allow-smoke-seed --output D:\ENZ\runs\M4
```

A ausência de `--solve` significa **construir, configurar, validar e salvar sem resolver**.

---

## 11. Geometria científica e smoke seed

O projeto possui dois caminhos rigorosamente separados.

### `published_skeleton()`

Contém apenas dimensões publicadas ou explicitamente desconhecidas. Valores ausentes permanecem como `None`. O build falha até que a especificação esteja completa e auditada.

Esse é o caminho correto para reprodução científica.

### `engineering_smoke_seed()`

Contém valores provisórios derivados ou hipotéticos. É usado exclusivamente para validar:

- conexão com o AEDT;
- criação de variáveis;
- primitivas CAD;
- operações booleanas;
- wave ports;
- regiões abertas;
- setups;
- malhas;
- salvamento;
- encerramento da sessão.

O smoke seed **não reproduz o artigo** e não pode gerar claims científicos.

Uma execução com `--scientific-run` rejeita qualquer dimensão marcada como `HYPOTHESIS` ou `INFERRED`.

---

## 12. Materiais e política do FR4

O FR4 será mantido na reprodução porque faz parte do protótipo publicado e foi utilizado como inclusão dielétrica de casamento. Entretanto, “FR4” não define um material eletromagnético único em 25,87 GHz.

Permanecem desconhecidos no artigo disponível:

- fabricante;
- produto;
- lote;
- permissividade complexa na frequência de operação;
- tangente de perdas;
- anisotropia;
- dispersão;
- dimensões completas da inclusão.

A campanha está dividida em:

| Fase | Objetivo |
|---|---|
| R0 | reproduzir o artigo mantendo FR4 |
| R1 | varrer $\varepsilon_r$, $\tan\delta$ e dimensões |
| R2 | reotimizar com materiais controlados |
| R3 | comparar protótipos medidos |

Materiais candidatos:

- Rogers TMM 4;
- Rogers RO4350B;
- Rogers RO3003;
- Rogers RT/duroid 5880.

Dados típicos em 10 GHz não serão extrapolados silenciosamente para 25,87 GHz. Toda propriedade usada no HFSS deve registrar fabricante, produto, frequência de referência, fonte e classificação de evidência.

A análise detalhada está em [`docs/01a_validacao_fr4_e_materiais_26ghz.md`](docs/01a_validacao_fr4_e_materiais_26ghz.md).

---

## 13. Plano de validação

### AEDT-BUILD-01

- construir M0–M4 sem solve;
- inspecionar histórico CAD;
- verificar nomes e unidades;
- validar portas, fronteiras, malha e setups;
- salvar e reabrir os projetos;
- registrar versão, PID e porta gRPC;
- publicar imagens e manifestos.

### AEDT-EIGENMODE-01

- resolver M0;
- identificar modos;
- confirmar convergência;
- mapear campos;
- calcular participação energética;
- verificar sensibilidade da cavidade.

### AEDT-DRIVEN-01

- resolver M1–M4;
- validar wave port;
- comparar Radiation Boundary e PML;
- exportar S-parameters;
- analisar frequência, banda e perdas;
- extrair campos complexos nas ranhuras.

### AEDT-POST-01

- exportar $E_\theta$ e $E_\phi$ complexos;
- gerar FFD ou antenna data;
- calcular beamwidth, ripple e SLL;
- verificar balanço de potência;
- comparar eficiência, ganho e fase de abertura;
- gerar relatório automatizado.

### EM-VALIDATION-01

- substituir o smoke seed por geometria rastreada;
- reproduzir M0–M4;
- comparar quantitativamente com o artigo;
- documentar discrepâncias;
- executar estudo de malha, fronteiras, materiais e tolerâncias;
- congelar o modelo de referência.

### DUALPORT-CRITICAL-01

Somente depois de G0 validado:

- criar duas portas;
- extrair S2P;
- gerar padrões embarcados;
- calcular TARC e ECC de campo;
- avaliar valores singulares e capacidade;
- comparar com duas antenas independentes.

---

## 14. Artefatos e rastreabilidade

Cada execução gera uma pasta independente:

```text
<run_id>/
├── spec.json
├── geometry_plan.json
├── preflight_offline.json
├── validation_live.json
├── ENZ_G0_Validation.aedt
├── manifest.json
└── inventory.json
```

O inventário registra:

- nome do arquivo;
- tamanho;
- hash SHA-256;
- data de criação;
- versão AEDT;
- configuração de runtime;
- variante geométrica;
- commit Git;
- estado da campanha.

Após a execução licenciada, serão incluídos:

```text
sparameters.sNp
convergence.csv
mesh_statistics.json
power_balance.json
aperture_fields/
embedded_fields/
farfield/
plots/
report.md
```

Nenhum gráfico isolado será aceito como resultado reprodutível sem manifesto, parâmetros, malha e identificação do modelo.

---

## 15. Métricas eletromagnéticas e MIMO

### 15.1 Balanço de potência

```math
P_{\mathrm{inc}}
=
P_{\mathrm{ref}}
+
P_{\mathrm{rad}}
+
P_{\mathrm{loss}}
+
P_{\mathrm{guided,out}}.
```

O erro numérico residual será registrado.

### 15.2 Uniformidade de fase

```math
\sigma_\phi=
\sqrt{
\frac{1}{N}
\sum_{n=1}^{N}
\left(\phi_n-\bar\phi\right)^2
}.
```

### 15.3 Correlação de padrões

```math
\rho_{ij}^{(P)}
=
\frac{
\left|
\int_{4\pi}
P(\Omega)
\mathbf F_i(\Omega)\cdot\mathbf F_j^*(\Omega)
\,d\Omega
\right|^2
}{
\left[
\int_{4\pi}P(\Omega)\|\mathbf F_i\|^2d\Omega
\right]
\left[
\int_{4\pi}P(\Omega)\|\mathbf F_j\|^2d\Omega
\right]
}.
```

### 15.4 Capacidade

```math
C=
\log_2\det
\left[
\mathbf I+
\frac{\rho}{N_t}
\mathbf H\mathbf H^H
\right].
```

Métricas prioritárias:

- frequência de ressonância;
- banda de −10 dB;
- eficiência de radiação;
- eficiência total;
- ganho realizado;
- ripple;
- beamwidth de 1 dB e 3 dB;
- SLL;
- phase center;
- fase e amplitude por ranhura;
- TARC;
- ECC de campo;
- CCL;
- valores singulares;
- rank efetivo;
- capacidade mediana e percentil 5%;
- outage;
- robustez a tolerâncias.

---

## 16. Aplicações de mercado

### Aplicações atuais

- backhaul e fronthaul mmWave;
- enlaces ponto-multiponto;
- cobertura setorial de células densas;
- small cells e redes privadas;
- radar automotivo e industrial;
- sensores de presença e imagem;
- enlaces de alta capacidade em ambientes internos;
- antenas compactas para repetidores;
- sistemas de comunicação e sensoriamento integrados.

### Aplicações futuras

- MIMO passivo codificado geometricamente;
- cavidades como processadores analógicos espaciais;
- terminais sem phase shifter por radiador;
- tiles ENZ para formação de autocanais;
- superfícies reconfiguráveis de baixa perda;
- dispositivos ISAC;
- antenas adaptativas orientadas ao canal;
- sistemas 6G e sub-THz;
- redes holográficas volumétricas;
- módulos compactos para plataformas aéreas e espaciais.

Cada aplicação deverá ser avaliada com benchmark equivalente em abertura, potência, banda, cadeias RF, volume e custo.

---

## 17. Limitações atuais

Este repositório ainda não possui:

- todas as dimensões originais do artigo;
- modelo CAD oficial dos autores;
- propriedades caracterizadas do FR4 em 25,87 GHz;
- execução licenciada publicada de M0–M4;
- convergência HFSS documentada;
- medições próprias;
- cavidade dual-port validada;
- demonstração experimental de autocanais MIMO.

Consequentemente:

- o smoke seed é apenas um modelo de automação;
- nenhuma curva atual deve ser apresentada como reprodução do artigo;
- nenhuma geometria multiporta deve ser chamada de inovação validada antes da revisão de anterioridade e dos experimentos;
- resultados simulados e medidos permanecerão claramente separados.

---

## 18. Roadmap

### Fase 1 — fundação

- [x] documentação teórica em português;
- [x] política de evidências;
- [x] revisão do papel do FR4;
- [x] renderização matemática no GitHub;
- [x] arquitetura AEDT/PyAEDT/gRPC;
- [x] contratos geométricos M0–M4;
- [x] testes offline e fake backend;
- [x] CLI inicial.

### Fase 2 — build licenciado

- [ ] executar M0–M4 no AEDT 2024 R2;
- [ ] auditar assinaturas PyAEDT;
- [ ] salvar e reabrir projetos;
- [ ] validar portas, materiais e fronteiras;
- [ ] publicar imagens CAD e manifestos.

### Fase 3 — reprodução eletromagnética

- [ ] resolver Eigenmode;
- [ ] resolver Driven Modal;
- [ ] estudar convergência;
- [ ] exportar S-parameters;
- [ ] extrair campos de abertura;
- [ ] reproduzir beamwidth, ripple, ganho e SLL;
- [ ] executar campanha de materiais.

### Fase 4 — experimento crítico de duas portas

- [ ] arquiteturas de porta oposta;
- [ ] portas ortogonais;
- [ ] excitações par/ímpar;
- [ ] slots intercalados;
- [ ] dopagem seletiva;
- [ ] padrões embarcados;
- [ ] TARC, ECC, rank e capacidade.

### Fase 5 — quatro portas e aplicação

- [ ] duas polarizações;
- [ ] duas famílias de padrão;
- [ ] otimização orientada ao canal;
- [ ] protótipo;
- [ ] medição multiporta;
- [ ] comparação com phased array e MIMO convencional.

Consulte também [`ROADMAP.md`](ROADMAP.md).

---

## 19. Estrutura do repositório

```text
.
├── README.md
├── ROADMAP.md
├── CREDITOS.md
├── CITATION.cff
├── AGENTS.md
├── CONTRIBUTING.md
├── LICENSE.md
├── pyproject.toml
├── requirements-aedt-2024.2.txt
├── docs/
│   ├── 00_carta_cientifica.md
│   ├── 01_artigo_base_inatel.md
│   ├── 01a_validacao_fr4_e_materiais_26ghz.md
│   ├── 02_fundamentos_maxwellianos.md
│   ├── ...
│   ├── 29_plano_de_publicacoes.md
│   ├── 30_implementacao_aedt_2024r2.md
│   ├── GUIA_RENDERIZACAO_MATEMATICA.md
│   └── INDEX.md
├── modelos/
│   └── especificacoes/
├── referencias/
├── scripts/
│   ├── enz_aedt.py
│   └── normalizar_formulas_markdown.py
├── src/
│   └── enz_eigenchannel_mimo/
├── testes/
└── artefatos/
```

O índice integral da documentação está em [`docs/INDEX.md`](docs/INDEX.md).

---

## 20. Contribuição, créditos e licença

### Contribuição

Contribuições são bem-vindas em:

- eletromagnetismo computacional;
- PyAEDT e automação HFSS;
- teoria modal e quasi-normal modes;
- antenas ranhuradas;
- ENZ e dopagem fotônica;
- caracterização de dielétricos mmWave;
- MIMO e modelos de canal;
- otimização adjunta;
- metrologia de antenas;
- fabricação de protótipos;
- revisão bibliográfica e patentária.

Leia [`CONTRIBUTING.md`](CONTRIBUTING.md) e [`AGENTS.md`](AGENTS.md) antes de alterar código científico.

Toda contribuição deve informar:

- hipótese;
- método;
- origem dos dados;
- versão do software;
- condições de simulação;
- limitações;
- artefatos reproduzíveis.

### Créditos

O projeto reconhece formalmente os autores do artigo-base, o Inatel, seus laboratórios, instituições de pesquisa e agências de fomento. Consulte [`CREDITOS.md`](CREDITOS.md).

A inteligência artificial é tratada como ferramenta auxiliar de pesquisa e engenharia. Não substitui revisão humana, autoria científica, validação eletromagnética ou responsabilidade técnica.

### Licença

- código original: **Apache License 2.0**;
- documentação original: **CC BY 4.0**;
- materiais de terceiros mantêm suas licenças;
- o artigo-base deve ser citado por seus autores e DOI originais.

Consulte [`LICENSE.md`](LICENSE.md).

### Citação

Use o arquivo [`CITATION.cff`](CITATION.cff) para citar este repositório. Ao utilizar resultados derivados do artigo-base, cite também Vilas Boas, Vasconcellos, Sodré Jr. e Figueiredo.

---

## Aviso científico

Este projeto é uma plataforma de pesquisa em evolução. Nenhum arquivo, gráfico, geometria provisória ou resultado de smoke test deve ser usado como especificação industrial, validação regulatória, prova de desempenho ou alegação de novidade sem revisão independente, simulação convergida e medição adequada.
