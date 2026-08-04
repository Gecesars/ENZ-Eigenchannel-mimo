# inst.md — Implementação e validação do sistema MIMO 2×2 com quatro radiadores e alimentação por guia de onda

## 0. Identificação da tarefa

Este documento é a instrução operacional completa para o agente responsável por implementar, validar e documentar uma arquitetura eletromagnética composta por:

- quatro estruturas radiantes completas previamente validadas no HFSS;
- duas redes de alimentação em guia de onda;
- duas portas RF externas;
- dois radiadores alimentados por cada rede;
- dois padrões embarcados externos;
- avaliação sistêmica MIMO 2×2;
- automação integral no Ansys Electronics Desktop 2024 R2 por Python/PyAEDT;
- rastreabilidade científica, geométrica, numérica e documental.

A topologia de referência é:

```text
Porta externa P1
      │
      └── Rede em guia WG-A ──┬── Radiador A1
                               └── Radiador A2

Porta externa P2
      │
      └── Rede em guia WG-B ──┬── Radiador B1
                               └── Radiador B2
```

O sistema deve ser tratado como:

```text
2 portas RF externas
4 radiadores físicos
2 super-elementos radiantes
MIMO 2×2 no nível das portas externas
```

Não classificar a arquitetura como MIMO 4×4. Os quatro radiadores não são quatro cadeias RF independentes quando conectados duas a duas às duas redes em guia.

---

## 1. Branch e documentos de referência

Executar o trabalho a partir da branch:

```text
research/mimo-2x2-four-radiators-waveguide
```

Ler integralmente, antes de qualquer alteração:

```text
AGENTS.md
README.md
ROADMAP.md
docs/20_arquitetura_hfss_grpc.md
docs/21_validacao_eletromagnetica.md
docs/23_dados_e_reprodutibilidade.md
docs/25_matriz_de_evidencias.md
docs/26_benchmarks.md
docs/30_implementacao_aedt_2024r2.md
docs/31_planejamento_mimo_2x2_quatro_radiadores_guia.md
docs/GUIA_RENDERIZACAO_MATEMATICA.md
modelos/especificacoes/
src/enz_eigenchannel_mimo/
testes/
```

Também ler e usar como checklist a Issue:

```text
#6 — Q0/Q1 — MIMO 2×2 com quatro radiadores e alimentação por guia
```

Antes de programar:

1. mapear o repositório completo;
2. identificar o que já existe;
3. reutilizar a arquitetura AEDT/PyAEDT existente;
4. registrar quais arquivos serão alterados;
5. declarar dependências novas;
6. criar uma sequência de commits por fase;
7. não iniciar alterações monolíticas sem checkpoints.

---

## 2. Regras inegociáveis

### 2.1 Preservação

- Não remover funcionalidades existentes.
- Não renomear APIs públicas sem camada de compatibilidade.
- Não reescrever módulos maduros sem justificar e testar.
- Não alterar a geometria interna das estruturas radiantes validadas durante o gate Q0.
- Não substituir silenciosamente materiais, fronteiras, portas, malha ou setups já validados.
- Não reconstruir manualmente quatro vezes uma geometria que possa ser importada como componente versionado.
- Não executar fallback silencioso para outra versão do AEDT.
- Não aceitar resultados sem manifesto e identificação de commit.
- Não apresentar smoke tests como validação eletromagnética.
- Não considerar baixo acoplamento isoladamente como prova de MIMO.
- Não otimizar todos os parâmetros simultaneamente no primeiro solve.
- Não usar apenas S-parameters para concluir diversidade espacial.
- Não usar apenas ECC calculada por S-parameters como métrica final em estrutura com perdas e padrões complexos.
- Não afirmar ganho de capacidade sem normalizar potência total, abertura, banda e número de cadeias RF.

### 2.2 Ambiente obrigatório

```text
Ansys Electronics Desktop 2024 R2
HFSS
Python 3.11 ou 3.12
PyAEDT compatível e congelado pelo projeto
Comunicação gRPC
Uma sessão AEDT por worker/processo
```

Versão lógica obrigatória:

```text
2024.2
```

Token esperado:

```text
242
```

Qualquer divergência deve interromper a execução científica.

### 2.3 Integridade científica

Toda informação deve receber uma classificação:

```text
PUBLICADO
DERIVADO
SIMULADO
MEDIDO
INFERIDO
HIPÓTESE
DESCONHECIDO
```

Para geometria e parâmetros, manter também:

```text
PUBLISHED_TEXT
PUBLISHED_FIGURE
DERIVED
INFERRED
OPTIMIZED
HYPOTHESIS
UNKNOWN
```

Nenhuma dimensão desconhecida pode ser promovida a valor publicado.

---

## 3. Resultado final esperado

O agente deve entregar uma suíte capaz de:

1. localizar e importar as quatro estruturas validadas;
2. congelar hashes e metadados;
3. repetir uma regressão mínima de cada estrutura;
4. construir uma rede em guia 1:2 para cada par;
5. incorporar casamento de impedância;
6. controlar amplitude e fase nas duas saídas;
7. produzir estados par, ímpar e quadratura;
8. conectar cada rede aos dois radiadores correspondentes;
9. montar as quatro estruturas no mesmo domínio eletromagnético;
10. configurar e resolver o sistema de duas portas externas;
11. extrair S-parameters, potência, malha, convergência e campos;
12. extrair padrões embarcados vetoriais complexos;
13. calcular ganho, eficiência, TARC, ECC, CCL, MEG, rank e capacidade;
14. comparar benchmarks com potência e abertura equivalentes;
15. gerar relatórios e artefatos reproduzíveis;
16. impedir claims quando um gate obrigatório não estiver concluído.

---

## 4. Pré-flight obrigatório do repositório

O agente deve executar e registrar:

```bash
git status --short
git branch --show-current
git log -1 --oneline
python --version
python -m pip --version
python -m pip check
python -m pytest -q
python -m compileall -q src scripts testes
python -m ruff check src scripts testes
python scripts/normalizar_formulas_markdown.py --check
```

Criar:

```text
artefatos/preflight/repository_state.json
artefatos/preflight/environment.json
artefatos/preflight/test_baseline.txt
```

O baseline deve conter:

- commit inicial;
- branch;
- arquivos modificados antes da tarefa;
- versão Python;
- versão PyAEDT;
- versão AEDT detectada;
- sistema operacional;
- CPU e memória;
- resultado dos testes;
- data/hora UTC;
- data/hora local;
- diretório de trabalho.

Não modificar arquivos existentes com alterações não relacionadas do usuário.

---

## 5. Gate Q0 — localizar e congelar as quatro estruturas validadas

### 5.1 Busca obrigatória

Procurar no repositório e nos diretórios configurados por:

```text
*.aedt
*.a3dcomp
*.step
*.stp
*.sat
*.x_t
*.s1p
*.s2p
*.s4p
*.ffd
*.json
*.yaml
*.csv
```

Também procurar nomes ou aliases que correspondam às quatro estruturas.

Não presumir que os modelos existem apenas porque o planejamento os menciona.

### 5.2 Condição de bloqueio

Caso os artefatos não sejam encontrados, não inventar caminhos e não reconstruir as estruturas. Criar:

```text
artefatos/q0/missing_validated_models.json
```

e encerrar o gate Q0 com estado:

```text
BLOCKED_MISSING_VALIDATED_ARTIFACTS
```

O relatório deve listar exatamente o que falta.

### 5.3 Identidades obrigatórias

Cada instância deve receber identidade determinística:

```text
RAD_A1
RAD_A2
RAD_B1
RAD_B2
```

Mesmo quando as quatro forem cópias da mesma estrutura, registrar instâncias separadas.

### 5.4 Manifesto de cada estrutura

Criar:

```text
modelos/componentes_validados/RAD_A1/manifest.json
modelos/componentes_validados/RAD_A2/manifest.json
modelos/componentes_validados/RAD_B1/manifest.json
modelos/componentes_validados/RAD_B2/manifest.json
```

Cada manifesto deve conter:

```json
{
  "id": "RAD_A1",
  "source_file": "",
  "source_sha256": "",
  "source_git_commit": "",
  "aedt_version": "2024.2",
  "pyaedt_version": "",
  "design_name": "",
  "solution_type": "",
  "port_name": "",
  "port_mode": "TE10",
  "frequency_center_ghz": null,
  "frequency_band_ghz": [],
  "coordinate_system": "",
  "orientation": {},
  "materials": [],
  "boundaries": [],
  "setups": [],
  "sweeps": [],
  "mesh_summary": {},
  "convergence_artifact": "",
  "touchstone_artifact": "",
  "farfield_artifact": "",
  "validation_report": "",
  "evidence_class": "SIMULADO"
}
```

### 5.5 Regressão individual

Executar um solve mínimo de regressão de cada radiador sem alterar sua geometria interna.

Verificar:

- frequência de ressonância;
- S11;
- banda de −10 dB;
- eficiência de radiação;
- eficiência total;
- ganho realizado máximo;
- direção do ganho máximo;
- beamwidth;
- ripple;
- SLL;
- cross-polarização;
- padrão Eθ e Eφ complexo;
- campos na abertura;
- potência aceita;
- convergência;
- número de elementos de malha.

Gerar uma matriz:

```text
referência validada
versus
regressão atual
```

Critérios de regressão devem ser configuráveis. Como baseline inicial:

```text
|Δf_res| / f_res <= 0,5 %
|ΔS11_min| <= 1 dB
|ΔG_realized|max <= 0,5 dB
|Δeficiência| <= 3 pontos percentuais
|Δbeamwidth| <= 3 graus
```

Esses valores são metas de regressão, não tolerâncias científicas universais.

---

## 6. Importação como 3D Component ou módulo imutável

Preferir, nesta ordem:

1. `3D Component` versionado;
2. importação do projeto/design validado;
3. módulo geométrico imutável com hash;
4. duplicação controlada do grupo de objetos;
5. reconstrução paramétrica somente se existir fonte auditável equivalente.

Criar:

```text
src/enz_eigenchannel_mimo/aedt/component_import.py
```

Responsabilidades:

- importar componente;
- criar coordenada local;
- posicionar;
- rotacionar;
- espelhar;
- validar porta;
- validar materiais;
- registrar hash;
- impedir alteração interna no gate Q0;
- exportar inventário dos objetos;
- detectar colisões geométricas.

Não utilizar cópia cega de objetos sem manter rastreabilidade.

---

## 7. Sistema de coordenadas

Adotar sistema global:

```text
X = longitudinal principal
Y = transversal
Z = vertical
```

Criar coordenadas locais:

```text
CS_RAD_A1
CS_RAD_A2
CS_RAD_B1
CS_RAD_B2
CS_WG_A
CS_WG_B
```

Parâmetros mínimos:

```text
pair_A_spacing
pair_B_spacing
interpair_spacing
pair_A_offset_x
pair_A_offset_y
pair_A_offset_z
pair_B_offset_x
pair_B_offset_y
pair_B_offset_z
pair_A_rotation_x
pair_A_rotation_y
pair_A_rotation_z
pair_B_rotation_x
pair_B_rotation_y
pair_B_rotation_z
mirror_A2
mirror_B2
```

Toda transformação deve aparecer no manifesto.

---

## 8. Gate Q1 — rede em guia de onda

### 8.1 Objetivo

Projetar uma rede em guia de onda de três portas:

```text
P_EXT
  │
  ├── P_RAD_1
  └── P_RAD_2
```

A primeira versão deve usar TE10 monomodo.

### 8.2 Guia de referência

Usar a seção compatível com as portas validadas. Caso seja WR-28:

```text
a ≈ 7,11 mm
b ≈ 3,56 mm
```

Não fixar essas dimensões sem verificar os modelos validados.

Calcular frequências de corte:

```math
f_{c,mn}=
\frac{c}{2\sqrt{\varepsilon_r}}
\sqrt{
\left(\frac{m}{a}\right)^2+
\left(\frac{n}{b}\right)^2
}.
```

Verificar em toda seção:

```text
TE10 propagante
TE20 abaixo ou acima do corte conforme a intenção
TE01 abaixo ou acima do corte conforme a intenção
nenhum modo superior não planejado transportando potência relevante
```

### 8.3 Topologias obrigatórias

Criar e comparar pelo menos:

```text
WG_EPLANE_T
WG_HPLANE_T
WG_SYMMETRIC_Y
WG_MATCHED_STEP
WG_IRIS_MATCHED
WG_POST_MATCHED
```

Não assumir que a junção simétrica simples terá casamento suficiente.

### 8.4 Rede de casamento de impedância

Implementar uma camada parametrizável de matching que possa utilizar:

- degrau de impedância;
- transformador de um quarto de onda guiada;
- múltiplos degraus;
- íris capacitiva;
- íris indutiva;
- poste metálico;
- par de postes;
- janela de acoplamento;
- seção alargada;
- taper;
- combinação otimizada de elementos.

Criar:

```text
src/enz_eigenchannel_mimo/pair_feed/matching.py
```

Contrato sugerido:

```python
@dataclass(frozen=True, slots=True)
class MatchingElementSpec:
    kind: str
    position_mm: float
    length_mm: float | None = None
    width_mm: float | None = None
    height_mm: float | None = None
    diameter_mm: float | None = None
    offset_y_mm: float = 0.0
    offset_z_mm: float = 0.0
    material: str = "pec"
    enabled: bool = True
```

A síntese inicial pode usar:

```math
Z_t \approx \sqrt{Z_{\mathrm{in}}Z_{\mathrm{load}}}
```

e:

```math
L_{\lambda_g/4}=
\frac{\lambda_g(f_0)}{4}.
```

Mas o agente deve deixar explícito que impedância modal de guia, descontinuidade tridimensional e cargas radiantes exigem validação full-wave.

### 8.5 Parâmetros da rede

No mínimo:

```text
wg_input_a
wg_input_b
wg_input_length
junction_type
junction_length
junction_width
branch_a
branch_b
branch_length_1
branch_length_2
branch_spacing
branch_bend_radius
output_rotation_1
output_rotation_2
matching_kind
step_count
step_1_length
step_1_width
step_1_height
step_2_length
step_2_width
step_2_height
iris_width
iris_height
iris_thickness
iris_position
post_diameter
post_height
post_position_x
post_offset_y
post_offset_z
phase_trim_1
phase_trim_2
```

### 8.6 Estados de fase

Implementar:

```text
EVEN       = 0° / 0°
ODD        = 0° / 180°
QUADRATURE = 0° / 90°
```

A diferença de comprimento inicial é:

```math
\Delta L(f_0)=
\frac{\Delta\phi}{\beta_g(f_0)}.
```

Para 180°:

```math
\Delta L_{180}=
\frac{\lambda_g(f_0)}{2}.
```

Para 90°:

```math
\Delta L_{90}=
\frac{\lambda_g(f_0)}{4}.
```

O agente deve calcular:

- fase por frequência;
- erro de fase na banda;
- group delay;
- desequilíbrio de group delay;
- dispersão da rede;
- sensibilidade dimensional.

### 8.7 Portas da rede isolada

Usar três wave ports:

```text
P_EXT
P_OUT_1
P_OUT_2
```

Configurar:

- número explícito de modos;
- linha de integração;
- polarização;
- de-embedding;
- renormalização;
- orientação consistente;
- referência de fase comum.

Validar visualmente o campo modal de cada porta.

---

## 9. DOE e otimização da rede

### 9.1 Fase de triagem

Usar DOE limitado para:

- tipo de junção;
- largura e altura de degraus;
- posição de íris;
- diâmetro e posição de poste;
- comprimento de ramos;
- diferença de fase;
- distância das saídas.

Não usar otimização global cara antes de eliminar topologias ruins.

### 9.2 Métricas da rede

Calcular:

```text
S11 da entrada
S22 e S33 das saídas
S21 e S31
isolamento S23
perda de inserção
desequilíbrio de amplitude
diferença de fase
group delay
conversão modal
potência dissipada
potência residual
```

### 9.3 Função objetivo

```math
J_F=
w_1L_{\mathrm{return}}
+w_2L_{\mathrm{amplitude}}
+w_3L_{\mathrm{phase}}
+w_4L_{\mathrm{insertion}}
+w_5L_{\mathrm{isolation}}
+w_6L_{\mathrm{mode\ conversion}}
+w_7L_{\mathrm{group\ delay}}.
```

Os pesos devem ser configuráveis e registrados.

### 9.4 Metas iniciais Q1

```text
S11 da entrada < −15 dB em f0
S11 da entrada < −10 dB na banda
desequilíbrio de amplitude < 0,5 dB
erro de fase < ±5° em f0
erro de fase RMS na banda documentado
perda adicional minimizada
conversão modal não planejada < −25 dB, quando mensurável
```

Não forçar metas impossíveis silenciosamente. Relatar trade-offs.

---

## 10. Gate Q2 — um par completo

### 10.1 Montagem

Conectar:

```text
WG-A + RAD_A1 + RAD_A2
```

e depois:

```text
WG-B + RAD_B1 + RAD_B2
```

### 10.2 Estados

Resolver:

```text
PAIR_A_EVEN
PAIR_A_ODD
PAIR_A_QUADRATURE
PAIR_B_EVEN
PAIR_B_ODD
PAIR_B_QUADRATURE
```

Não manter todos na solução final obrigatoriamente. Selecionar os melhores estados por critérios declarados.

### 10.3 Validações

- casamento na porta externa;
- amplitude entregue a cada radiador;
- fase na interface guia-radiador;
- potência aceita;
- potência refletida;
- perda condutiva;
- perda dielétrica;
- potência radiada;
- potência residual;
- conversão modal;
- eficiência;
- padrão;
- ganho;
- beamwidth;
- ripple;
- SLL;
- cross-polarização;
- phase center;
- campo na abertura;
- sensibilidade a tolerâncias.

### 10.4 Padrão do par

Para o par `k`:

```math
\mathbf F_k(\Omega,f)=
a_{k1}\mathbf F_{k1}(\Omega,f)
+
a_{k2}\mathbf F_{k2}(\Omega,f).
```

Comparar:

- superposição ideal dos radiadores isolados;
- resultado acoplado full-wave;
- diferença de amplitude;
- diferença de fase;
- diferença de ganho;
- diferença de beamwidth;
- diferença de eficiência.

A diferença entre superposição e full-wave deve ser quantificada.

---

## 11. Gate Q3 — quatro radiadores com quatro portas internas

Montar as quatro estruturas sem as redes de alimentação finais.

Portas:

```text
R1 = RAD_A1
R2 = RAD_A2
R3 = RAD_B1
R4 = RAD_B2
```

Extrair:

```math
\mathbf S_R(f)\in\mathbb C^{4\times4}.
```

Calcular:

- acoplamento no mesmo par;
- acoplamento entre pares;
- active S-parameters;
- TARC para estados definidos;
- padrões embarcados individuais;
- matriz de correlação;
- eficiência ativa;
- potência aceita por excitação.

Criar mapas versus:

```text
pair_spacing
interpair_spacing
rotation
polarization
offset_x
offset_y
offset_z
mirror
```

Selecionar arranjo físico antes de integrar as duas redes.

---

## 12. Gate Q4 — sistema completo

### 12.1 Portas externas

O sistema final deve conter:

```text
P1 = entrada da rede WG-A
P2 = entrada da rede WG-B
```

As conexões para os quatro radiadores são internas.

### 12.2 Arquiteturas mínimas

Resolver e comparar:

```text
C0 = EVEN / EVEN
C1 = EVEN / ODD
C2 = polarizações ortogonais
C3 = EVEN / QUADRATURE
C4 = melhor configuração espacial otimizada
```

C1 é prioritária. C2 é a alternativa prioritária.

### 12.3 Matriz de rede externa

```math
\mathbf S_{\mathrm{SYS}}=
\begin{bmatrix}
S_{11} & S_{12}\\
S_{21} & S_{22}
\end{bmatrix}.
```

Extrair:

- S11;
- S22;
- S12;
- S21;
- active reflection coefficient;
- TARC;
- potência aceita por porta;
- eficiência ativa.

---

## 13. Configuração HFSS

### 13.1 Solution type

Usar:

```text
HFSS Driven Modal
```

Usar Eigenmode adicionalmente em:

- junção alargada;
- cavidade de distribuição;
- seção suspeita de ressonância;
- estruturas multimodo futuras.

### 13.2 Setup

Nomes determinísticos:

```text
Setup_Q1_Feed
Setup_Q2_Pair
Setup_Q3_FourPort
Setup_Q4_MIMO2x2
```

A frequência adaptativa deve vir do manifesto do radiador validado.

### 13.3 Sweeps

Criar:

- sweep discreto em pontos críticos;
- sweep interpolante somente depois da validação discreta;
- pontos adicionais em ressonâncias;
- pontos para campo distante;
- pontos para fase da rede;
- pontos para group delay.

### 13.4 Open region

Comparar:

```text
Radiation Boundary
PML
```

Executar estudo de distância do airbox.

### 13.5 Malha

Refinar em:

- ranhuras;
- interfaces guia-radiador;
- junções;
- íris;
- postes;
- degraus;
- bends;
- gaps;
- bordas metálicas;
- regiões de alta corrente;
- dielétricos;
- descontinuidades modais.

### 13.6 Convergência

Não aceitar apenas `MaxDeltaS`.

Convergir simultaneamente:

```text
ΔS
Δganho
Δeficiência
Δbeamwidth
Δripple
ΔSLL
Δfase relativa
ΔECC
Δrank efetivo
```

Registrar por passe:

```text
convergence.csv
mesh_statistics.json
```

---

## 14. Extração de ganho e eficiência

### 14.1 Por porta externa

Para P1 e P2, extrair:

- directivity;
- gain;
- realized gain;
- peak realized gain;
- direção do máximo;
- eficiência de radiação;
- eficiência total;
- accepted power;
- incident power;
- reflected power.

### 14.2 Normalização

Toda comparação deve usar uma das normalizações explicitamente declaradas:

```text
1 W incidente por porta ativa
1 W aceito por porta ativa
potência total incidente fixa
potência total aceita fixa
```

Não comparar um caso com 2 W totais contra outro com 1 W sem correção.

### 14.3 Ganho do conjunto

Calcular:

```text
ganho por porta externa
ganho do super-elemento A
ganho do super-elemento B
ganho máximo de cada arquitetura
ganho no setor de interesse
ganho médio no setor
ganho mínimo no setor
cobertura conjunta
ganho de multiplexação versus ganho de array
```

Separar:

- ganho coerente de arranjo;
- ganho de diversidade;
- ganho de multiplexação;
- ganho de capacidade.

Não somar ganhos em dBi diretamente.

### 14.4 Excitação simultânea

Para vetores de excitação definidos:

```math
\mathbf v=
\begin{bmatrix}
v_1\\
v_2
\end{bmatrix},
```

calcular:

```math
\mathbf F(\Omega,f;\mathbf v)
=
v_1\mathbf F_1(\Omega,f)
+
v_2\mathbf F_2(\Omega,f).
```

Avaliar ao menos:

```text
[1, 0]
[0, 1]
[1, 1]/sqrt(2)
[1, -1]/sqrt(2)
[1, j]/sqrt(2)
```

Esses estados não substituem a avaliação MIMO com streams independentes; são testes de padrão e TARC.

---

## 15. Padrões embarcados complexos

Para cada porta externa:

```math
\mathbf F_m(\Omega,f)=
\begin{bmatrix}
E_{\theta,m}(\Omega,f)\\
E_{\phi,m}(\Omega,f)
\end{bmatrix}.
```

Exportar:

```text
magnitude
fase
real
imag
Etheta
Ephi
co-pol
cross-pol
grade theta/phi
frequência
normalização de potência
```

Usar uma grade consistente, preferencialmente:

```text
theta = 0° a 180°
phi = 0° a 360°
resolução inicial = 1°
```

Para otimização rápida, permitir grade mais grossa, mas a validação final deve usar grade fina e documentada.

---

## 16. Parâmetros MIMO obrigatórios

### 16.1 ECC de campo isotrópica

```math
\rho_{ij}=
\frac{
\left|
\int_{4\pi}
\mathbf F_i(\Omega)\cdot
\mathbf F_j^*(\Omega)
\,d\Omega
\right|^2
}{
\left[
\int_{4\pi}\|\mathbf F_i(\Omega)\|^2d\Omega
\right]
\left[
\int_{4\pi}\|\mathbf F_j(\Omega)\|^2d\Omega
\right]
}.
```

### 16.2 ECC ponderada pelo canal

```math
\rho_{ij}^{(P)}=
\frac{
\left|
\int_{4\pi}
P(\Omega)
\mathbf F_i(\Omega)\cdot
\mathbf F_j^*(\Omega)
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

### 16.3 TARC

Para vetor de excitação `a`:

```math
\Gamma_{\mathrm{TARC}}=
\sqrt{
\frac{
\|\mathbf S\mathbf a\|_2^2
}{
\|\mathbf a\|_2^2
}
}.
```

### 16.4 Active reflection coefficient

Para a porta `m`:

```math
\Gamma_m^{\mathrm{active}}=
\frac{
\sum_n S_{mn}a_n
}{
a_m
}.
```

### 16.5 Matriz de Gram dos padrões

```math
G_{ij}=
\langle \mathbf F_i,\mathbf F_j\rangle_P.
```

Calcular autovalores, condição e ortogonalidade.

### 16.6 Rank efetivo

Usar valores singulares ou autovalores normalizados:

```math
p_i=
\frac{\sigma_i^2}{
\sum_k \sigma_k^2
}.
```

```math
r_{\mathrm{eff}}=
\exp\left(
-\sum_i p_i\ln p_i
\right).
```

### 16.7 Capacidade

```math
C=
\log_2\det
\left[
\mathbf I+
\frac{\rho}{N_t}
\mathbf H\mathbf H^H
\right].
```

Calcular:

- capacidade instantânea;
- média;
- mediana;
- percentil 5%;
- percentil 95%;
- outage;
- distribuição de singular values;
- condição;
- rank efetivo.

### 16.8 Outras métricas

Implementar:

```text
Diversity Gain
MEG
MEG imbalance
CCL
Total Active Reflection Coefficient
Active efficiency
Envelope correlation
Multiplexing efficiency
```

Documentar a convenção e as unidades.

---

## 17. Modelos de canal

Implementar em:

```text
src/enz_eigenchannel_mimo/mimo2x2/channel_models.py
```

Cenários mínimos:

```text
H0_ISOTROPIC
H1_LAPLACIAN_NARROW
H2_LAPLACIAN_MEDIUM
H3_DOMINANT_LOS
H4_POLARIMETRIC
H5_MEASURED
```

Parâmetros configuráveis:

```text
azimuth_mean
azimuth_spread
elevation_mean
elevation_spread
cluster_count
K_factor
XPR
polarization_rotation
path_count
path_gains
path_phases
```

Usar seeds explícitos em Monte Carlo.

Salvar:

```text
channel_manifest.json
channel_ensemble.npz
channel_metrics.json
```

---

## 18. Benchmarks obrigatórios

Comparar com potência, banda e abertura equivalentes:

```text
B0 = um radiador
B1 = dois radiadores independentes, um por porta
B2 = quatro radiadores em dois pares EVEN/EVEN
B3 = quatro radiadores em EVEN/ODD
B4 = quatro radiadores com polarização ortogonal
B5 = quatro radiadores idealmente alimentados por quatro portas
B6 = sistema proposto com redes reais e perdas
```

A comparação B5 é limite superior, não arquitetura de custo equivalente.

Para cada benchmark, registrar:

- potência total incidente;
- potência total aceita;
- abertura;
- volume;
- massa estimada;
- número de portas;
- número de cadeias RF;
- eficiência;
- ganho;
- ECC;
- rank;
- capacidade;
- complexidade de fabricação.

---

## 19. Estrutura de código a criar

```text
src/enz_eigenchannel_mimo/
├── pair_feed/
│   ├── __init__.py
│   ├── spec.py
│   ├── modes.py
│   ├── waveguide.py
│   ├── junctions.py
│   ├── matching.py
│   ├── phase_network.py
│   ├── objectives.py
│   └── validation.py
├── four_radiator/
│   ├── __init__.py
│   ├── spec.py
│   ├── placement.py
│   ├── assembly.py
│   ├── coupling.py
│   └── campaign.py
├── mimo2x2/
│   ├── __init__.py
│   ├── embedded_patterns.py
│   ├── active_network.py
│   ├── channel_models.py
│   ├── eigenchannels.py
│   ├── metrics.py
│   └── reports.py
└── aedt/
    ├── component_import.py
    ├── modal_export.py
    ├── geometry_capture.py
    └── full_system_post.py
```

Manter compatibilidade com a arquitetura AEDT já existente.

---

## 20. Especificações YAML

Criar:

```text
modelos/especificacoes/
├── q0_validated_radiators.yaml
├── q1_feed_even.yaml
├── q1_feed_odd.yaml
├── q1_feed_quadrature.yaml
├── q2_pair_even.yaml
├── q2_pair_odd.yaml
├── q3_four_radiators_open_ports.yaml
├── q4_mimo2x2_c0_even_even.yaml
├── q4_mimo2x2_c1_even_odd.yaml
├── q4_mimo2x2_c2_crosspolar.yaml
├── q4_mimo2x2_c3_even_quadrature.yaml
└── q5_tolerance_campaign.yaml
```

Cada YAML deve possuir:

```text
schema
identifier
evidence_class
source_commit
radiator_components
runtime
frequency
geometry
placement
waveguide
junction
matching
phase_state
materials
boundaries
mesh
setup
sweep
farfield
optimization
acceptance
exports
```

---

## 21. CLI

Estender a CLI sem quebrar `enz-aedt`.

Comandos sugeridos:

```bash
enz-aedt q0-import --spec modelos/especificacoes/q0_validated_radiators.yaml
enz-aedt q1-feed --state even --build-only
enz-aedt q1-feed --state odd --solve
enz-aedt q1-feed --state quadrature --solve
enz-aedt q2-pair --state even --solve
enz-aedt q3-coupling --solve
enz-aedt q4-mimo --architecture c1 --solve
enz-aedt q4-mimo --architecture c1 --post-only
enz-aedt q5-tolerance --architecture c1 --samples 100
```

Adicionar:

```text
--graphical
--non-graphical
--attach-port
--build-only
--solve
--post-only
--resume
--force-new-run
--scientific-run
--output
--seed
--workers
--cores
```

Não permitir `--scientific-run` com componentes sem manifesto validado.

---

## 22. Capturas e artefatos visuais

Criar capturas automáticas:

```text
top
front
right
isometric
waveguide_only
pair_A
pair_B
full_system
mesh
E-field junction
H-field junction
surface current
aperture field
far-field 3D
far-field cuts
```

Exportar em PNG com resolução suficiente para relatório.

Criar diagramas:

- topologia das portas;
- fluxo de potência;
- rede equivalente;
- sistema de coordenadas;
- arranjo dos quatro radiadores;
- estados EVEN/ODD/QUADRATURE;
- pipeline de validação;
- matriz de gates.

Não apresentar render conceitual como resultado HFSS.

---

## 23. Artefatos por execução

```text
artefatos/runs/<run_id>/
├── run_manifest.json
├── source_components.json
├── spec.yaml
├── geometry_plan.json
├── geometry_manifest.json
├── network_topology.json
├── runtime.json
├── preflight.json
├── validation_live.json
├── modes.json
├── model.aedt
├── feed_A.s3p
├── feed_B.s3p
├── radiators_open.s4p
├── system.s2p
├── convergence.csv
├── mesh_statistics.json
├── power_balance.json
├── active_network.json
├── embedded_patterns/
├── aperture_fields/
├── farfield/
├── channel_ensemble/
├── mimo_metrics.json
├── benchmark_metrics.json
├── plots/
├── screenshots/
├── inventory.json
└── report.md
```

O `inventory.json` deve conter SHA-256 de todos os arquivos.

---

## 24. Balanço de potência

Verificar:

```math
P_{\mathrm{inc}}=
P_{\mathrm{ref}}+
P_{\mathrm{rad}}+
P_{\mathrm{cond}}+
P_{\mathrm{diel}}+
P_{\mathrm{guided,out}}+
P_{\mathrm{residual}}.
```

Gerar por:

- frequência;
- porta;
- estado de excitação;
- arquitetura.

Meta inicial de resíduo:

```text
|P_residual| / P_inc < 2 %
```

Caso não seja atingida, não ocultar; investigar malha, portas, fronteiras e pós-processamento.

---

## 25. Robustez Q5

Executar sensibilidade para:

```text
largura e altura do guia
comprimento de ramo
diferença de fase
posição da íris
dimensão dos degraus
diâmetro e posição de postes
gap de flange
desalinhamento lateral
desalinhamento angular
rugosidade
condutividade
permissividade
tangente de perdas
separação entre radiadores
separação entre pares
```

Usar:

- sweep local;
- Morris;
- Latin Hypercube;
- Monte Carlo, conforme custo.

Relatar:

- yield;
- piores variáveis;
- distribuição de S11;
- distribuição de ganho;
- distribuição de ECC;
- distribuição de rank;
- distribuição de capacidade.

---

## 26. Testes automatizados

### 26.1 Offline

Criar testes sem AEDT:

```text
test_pair_feed_spec.py
test_modes.py
test_matching.py
test_phase_network.py
test_four_radiator_placement.py
test_active_network.py
test_embedded_patterns.py
test_ecc.py
test_tarc.py
test_effective_rank.py
test_capacity.py
test_channel_models.py
test_manifests.py
```

Cobrir:

- unidades;
- nomes determinísticos;
- dimensões inválidas;
- modos de corte;
- fase;
- normalização de potência;
- matrizes complexas;
- integração angular;
- singular values;
- seeds reproduzíveis;
- leitura/escrita de artefatos.

### 26.2 Backend AEDT falso

Criar fakes para:

- modeler;
- objects;
- wave ports;
- mesh;
- setup;
- sweep;
- post;
- far field;
- save/reopen;
- 3D components.

### 26.3 Smoke licenciado

Executar em ordem:

```text
SMOKE-Q0
SMOKE-Q1-BUILD
SMOKE-Q1-SOLVE
SMOKE-Q2
SMOKE-Q3
SMOKE-Q4
SMOKE-Q4-POST
```

Cada gate deve salvar e reabrir o `.aedt`.

---

## 27. Critérios de aceite

### 27.1 Q0

- quatro componentes encontrados;
- hashes registrados;
- regressão individual aprovada;
- portas confirmadas;
- padrões complexos exportados;
- nenhuma dimensão interna alterada.

### 27.2 Q1

- entrada melhor que −15 dB em f0;
- entrada melhor que −10 dB na banda alvo;
- desequilíbrio menor que 0,5 dB;
- erro de fase menor que ±5° em f0;
- perda documentada;
- pureza modal demonstrada;
- matching robusto e parametrizado.

### 27.3 Q2

- par conectado sem colisões;
- fase e amplitude entregues dentro da meta;
- eficiência quantificada;
- padrão do estado confirmado;
- diferença ideal versus full-wave documentada;
- balanço de potência fechado.

### 27.4 Q3

- S4P exportado;
- acoplamentos mapeados;
- melhor espaçamento selecionado;
- padrões individuais exportados;
- configuração física congelada.

### 27.5 Q4

Metas iniciais:

```text
S11 < −10 dB
S22 < −10 dB
isolamento externo < −15 dB
meta estendida de isolamento < −20 dB
ECC de campo < 0,10 no cenário de referência
eficiência total preferencial > 75 %
rank efetivo próximo de 2 em canais relevantes
ganho de capacidade contra C0 demonstrado
```

Nenhuma meta deve ser forçada por exclusão de frequências ou cenários desfavoráveis.

---

## 28. Relatório final

Gerar:

```text
docs/32_relatorio_implementacao_mimo_2x2.md
```

O relatório deve conter:

1. commit e branch;
2. ambiente;
3. artefatos de entrada;
4. geometria;
5. rede em guia;
6. matching;
7. estados modais;
8. S-parameters;
9. malha;
10. convergência;
11. balanço de potência;
12. ganho e eficiência;
13. padrões;
14. MIMO;
15. benchmarks;
16. sensibilidade;
17. falhas;
18. limitações;
19. decisões;
20. próximos passos.

Gerar tabela de evidências:

```text
claim
valor
unidade
frequência
modelo
evidência
artefato
hash
```

---

## 29. Estratégia de commits

Usar commits pequenos e auditáveis:

```text
chore: registra baseline e artefatos validados Q0
feat: importa componentes HFSS validados
feat: adiciona contratos da rede em guia
feat: implementa junções e matching
feat: implementa estados even odd quadrature
test: valida rede em guia offline
feat: monta pares completos Q2
feat: monta arranjo de quatro radiadores Q3
feat: integra sistema MIMO 2x2 Q4
feat: adiciona pós-processamento MIMO
test: adiciona regressões e smoke gates
docs: publica relatório e matriz de evidências
```

Não misturar correções não relacionadas.

---

## 30. Condições de parada

O agente deve parar e reportar, sem improvisar, quando ocorrer:

- ausência dos quatro modelos validados;
- versão AEDT diferente;
- falta de licença;
- porta desconhecida;
- componente corrompido;
- geometria não reprodutível;
- diferença de regressão acima da tolerância;
- falha de convergência;
- potência residual elevada;
- modo superior não planejado dominante;
- erro de fase não controlável;
- ganho obtido apenas por aumento de potência;
- cálculo MIMO sem padrões complexos;
- artefatos incompletos;
- alteração interna não autorizada no radiador.

O relatório de bloqueio deve indicar:

```text
gate
erro
causa provável
evidência
arquivos
ação recomendada
risco
```

---

## 31. Ordem exata de execução

O agente deve seguir esta sequência:

```text
01. Ler documentação e AGENTS.md
02. Registrar baseline Git e Python
03. Executar testes existentes
04. Localizar quatro modelos validados
05. Criar manifestos e hashes
06. Regressão individual Q0
07. Importação por 3D Component
08. Implementar contratos Python
09. Construir guia TE10 isolado
10. Construir junções E-plane e H-plane
11. Implementar matching
12. Implementar EVEN
13. Implementar ODD
14. Implementar QUADRATURE
15. DOE de rede Q1
16. Selecionar duas redes
17. Montar um par Q2
18. Validar ganho, fase, eficiência e padrão
19. Montar quatro radiadores Q3
20. Otimizar posicionamento
21. Montar sistema completo Q4
22. Extrair S2P e padrões externos
23. Calcular TARC e active S
24. Calcular ECC de campo
25. Construir canais
26. Calcular singular values, rank e capacidade
27. Comparar benchmarks
28. Executar robustez Q5
29. Gerar relatório
30. Executar bateria completa
31. Salvar e reabrir projetos
32. Publicar artefatos e hashes
```

Nenhuma fase posterior pode mascarar falha de uma fase anterior.

---

## 32. Definição de conclusão

A tarefa somente será considerada concluída quando:

- o arquivo de instrução estiver aplicado;
- as quatro estruturas validadas estiverem rastreadas;
- os dois guias tiverem rede de casamento;
- EVEN, ODD e QUADRATURE tiverem sido validados;
- o melhor par estiver congelado;
- as quatro estruturas estiverem integradas;
- o sistema tiver duas portas externas;
- S-parameters, ganho e eficiência estiverem convergidos;
- os padrões embarcados complexos estiverem exportados;
- ECC, TARC, CCL, MEG, rank e capacidade estiverem calculados;
- benchmarks equivalentes estiverem documentados;
- artefatos, manifests e hashes estiverem completos;
- todos os testes estiverem aprovados;
- nenhum claim exceder a evidência disponível.

---

## 33. Resumo obrigatório a apresentar ao final de cada fase

O agente deve responder no formato:

```text
FASE:
STATUS:
COMMIT:
ARQUIVOS ALTERADOS:
TESTES:
ARTEFATOS:
RESULTADOS:
LIMITAÇÕES:
RISCOS:
PRÓXIMO GATE:
```

Não apresentar apenas “implementado com sucesso”. Demonstrar o que foi criado, validado, medido, simulado e o que permanece desconhecido.
