# 30 — Implementação Python para AEDT/HFSS 2024 R2

## 1. Estado desta entrega

Esta camada prepara a geração paramétrica, o preflight, a validação do design e a execução controlada dos modelos G0/M0–M4 no Ansys Electronics Desktop 2024 R2.

Ela foi estruturada a partir das práticas já consolidadas no repositório `dipole_gen`:

- importação tardia do PyAEDT;
- uma sessão AEDT por worker/processo;
- identidade estrita de versão;
- comunicação gRPC;
- nenhuma chamada AEDT na thread da interface;
- variáveis criadas antes da geometria;
- nomes determinísticos;
- build separado de solve;
- preflight antes de licença/solver;
- manifestos e hashes de artefatos;
- testes offline sem AEDT;
- gates licenciados explicitamente separados.

Nenhum resultado eletromagnético é declarado nesta etapa. Os testes atuais validam contratos, topologia CAD, contagem de peças, rastreabilidade e orquestração offline.

## 2. Estrutura de código

```text
src/enz_eigenchannel_mimo/
├── aedt/
│   ├── runtime.py       identidade estrita AEDT 2024.2
│   ├── session.py       ciclo de vida PyAEDT/gRPC
│   ├── materials.py     FR4 DOE e candidatos de baixa perda
│   ├── builder.py       interpretador do plano CAD no HFSS
│   ├── validation.py    preflight offline e validação live
│   ├── artifacts.py     manifesto, inventário e SHA-256
│   ├── post.py          Touchstone, rede e preparação de campo distante
│   ├── campaign.py      build/validate/solve/export
│   └── cli.py           interface de linha de comando
└── geometry/
    ├── spec.py          contrato científico das dimensões
    ├── plan.py          DTO CAD independente de PyAEDT
    └── g0.py            planos M0, M1, M2, M3 e M4
```

## 3. Modelos preparados

### M0 — cavidade fechada

- shell metálico;
- vazio interno;
- solução Eigenmode;
- sem porta;
- sem região aberta;
- setup preliminar de 18 a 32 GHz, 12 modos.

### M1 — três ranhuras

- cavidade;
- guia WR-28;
- wave port modal;
- três ferramentas de corte;
- Auto-Open Region = Radiation;
- setup Driven Modal em 25,87 GHz;
- sweep de 25,3 a 26,8 GHz.

### M2 — cinco ranhuras

- mesma cadeia de M1;
- cinco ranhuras;
- preservação explícita da área transversal;
- preparação para comparação de fase e amplitude de abertura.

### M3 — perfil em degrau

- M2;
- corpo paramétrico de adição ou remoção de metal;
- largura e altura publicadas preservadas;
- posição e extensão ainda bloqueadas para execução científica enquanto não forem rastreadas.

### M4 — modelo fabricável

- M3;
- inclusão dielétrica;
- pinos metálicos de supressão modal;
- operação de chanfro por índices de aresta explícitos;
- material condutor real;
- preparação para FR4, TMM 4, RO4350B, RO3003 e RT/duroid 5880.

## 4. Regra contra geometria inventada

O código possui dois caminhos distintos.

### Esqueleto publicado

`published_skeleton()` contém apenas grandezas publicadas e mantém valores ausentes como `None`. Ele deve falhar antes do build até que todas as dimensões necessárias sejam recuperadas e classificadas.

### Seed de smoke test

`engineering_smoke_seed()` contém valores provisórios marcados como `HYPOTHESIS` ou `DERIVED`. Serve somente para testar:

- conexão;
- criação de variáveis;
- operações booleanas;
- portas;
- setup;
- salvamento;
- validação do fluxo.

Uma execução com `scientific_run=True` rejeita automaticamente qualquer dimensão hipotética ou inferida.

## 5. Convenção geométrica

```text
X = direção longitudinal/de propagação
Y = dimensão transversal larga da cavidade
Z = dimensão vertical
```

A origem da cavidade está em `X=0`. O guia WR-28 se estende para `X<0`. A parede inferior interna está em `Z=0` e a parede superior interna em `Z=cav_h`.

Todas as dimensões são variáveis AEDT com unidade explícita. O builder não grava números adimensionais em variáveis geométricas.

## 6. Execução

Instalar o ambiente Python no Windows que possui AEDT 2024 R2:

```powershell
py -3.12 -m venv .venv-aedt242
.\.venv-aedt242\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,aedt]"
```

Build gráfico do seed M1, sem solve:

```powershell
enz-aedt M1 --graphical --allow-smoke-seed --output D:\ENZ\runs
```

Build headless M4, sem solve:

```powershell
enz-aedt M4 --allow-smoke-seed --output D:\ENZ\runs
```

Build e solve provisório:

```powershell
enz-aedt M2 --allow-smoke-seed --solve --output D:\ENZ\runs
```

Anexar a uma sessão gRPC conhecida:

```powershell
enz-aedt M1 --graphical --attach-port 50051 --allow-smoke-seed
```

A CLI não procura sessões de forma ambígua. O attach exige porta explícita.

## 7. Artefatos por execução

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

O inventário contém tamanho e SHA-256 de cada arquivo.

Após o solve licenciado, a próxima implementação deve acrescentar:

- Touchstone;
- convergência por passe;
- estatísticas de malha;
- balanço de potência;
- campos complexos nas ranhuras;
- `E_theta` e `E_phi` complexos;
- FFD/antenna data;
- imagens de campo e geometria;
- relatório comparativo com o artigo.

## 8. Materiais

O módulo `materials.py` separa:

- 25 pontos DOE de FR4, todos classificados como hipótese;
- TMM 4;
- RO4350B;
- RO3003;
- RT/duroid 5880.

Os dados de candidatos são identificados pela frequência de referência de 10 GHz e não são tratados como caracterização em 25,87 GHz.

## 9. Validação offline concluída

A suíte inicial cobre:

- normalização de `2024.2`, `2024 R2` e `242`;
- rejeição de fallback de versão;
- attach somente por endpoint explícito;
- construção dos planos M0–M4;
- contagem de 0/3/5/5/5 ranhuras;
- M0 sem porta e sem região aberta;
- M4 com dopante, quatro pinos e chanfro;
- 25 casos FR4 DOE;
- rejeição do smoke seed em execução científica.

O resultado local desta implementação foi:

```text
16 passed
```

Isso não representa validação licenciada do AEDT.

## 10. Gates licenciados seguintes

### AEDT-BUILD-01

- abrir AEDT 2024 R2;
- construir M0–M4 sem solve;
- inspecionar objetos, materiais, históricos e portas;
- salvar e reabrir cada `.aedt`;
- corrigir qualquer diferença de assinatura PyAEDT 1.3.0/AEDT 2024 R2.

### AEDT-SOLVE-01

- resolver M0 Eigenmode;
- registrar modos e convergência;
- resolver M1 Driven Modal;
- exportar S1P;
- validar região aberta e wave port.

### EM-VALIDATION-01

- substituir dimensões provisórias por dados rastreados;
- reproduzir a sequência completa do artigo;
- comparar frequência, banda, ganho, ripple, beamwidth e SLL;
- executar a campanha de materiais;
- emitir matriz de discrepâncias.
