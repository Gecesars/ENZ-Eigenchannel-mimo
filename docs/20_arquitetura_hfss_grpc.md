# 20 — Arquitetura AEDT/HFSS 2024 R2, PyAEDT e gRPC

## 1. Objetivo

Construir uma camada científica estrita para:

- iniciar ou anexar ao AEDT 2024 R2;
- controlar HFSS por PyAEDT;
- isolar objetos vivos em processo worker;
- gerar geometrias paramétricas;
- resolver Eigenmode e Driven Modal;
- exportar rede, campos e metadados;
- recuperar falhas sem corromper o projeto.

## 2. Comunicação

A aplicação usa:

```text
orquestrador Python
        ↓ IPC
worker AEDT
        ↓ PyAEDT
gRPC nativo do AEDT
        ↓
Ansys Electronics Desktop 2024 R2
```

Não é necessário criar inicialmente um protocolo gRPC próprio. PyAEDT utiliza a interface gRPC do AEDT.

## 3. Modos de execução

### local_launch

O worker inicia uma instância dedicada.

Uso recomendado para campanhas reprodutíveis.

### local_attach

Anexa a uma instância gráfica existente.

Uso recomendado para inspeção e depuração.

### remote_direct

Conecta a máquina e porta remotas quando infraestrutura e licenciamento permitirem.

## 4. Configuração científica

```python
@dataclass(frozen=True)
class AedtRuntimeSpec:
    version: str = "2024.2"
    strict_version: bool = True
    non_graphical: bool = True
    new_desktop: bool = True
    close_on_exit: bool = True
    machine: str = ""
    port: int = 0
    process_id: int | None = None
    startup_timeout_s: int = 180
    solve_timeout_s: int = 21600
```

A versão não deve sofrer fallback silencioso.

## 5. Worker

Somente o worker pode possuir:

- `Desktop`;
- `Hfss`;
- `modeler`;
- `post`;
- `variable_manager`;
- objetos de setup;
- referências gRPC.

A interface e o otimizador recebem apenas DTOs serializáveis.

## 6. Estado da tarefa

```text
CREATED
PREFLIGHT
CONNECTING
BUILDING
VALIDATING_GEOMETRY
MESHING
SOLVING
POSTPROCESSING
EXPORTING
COMPLETED
FAILED
CANCELLED
```

## 7. Preflight

Antes de resolver:

1. verificar versão;
2. verificar licença;
3. verificar pasta gravável;
4. verificar lock;
5. salvar projeto;
6. validar design;
7. validar portas;
8. validar fronteiras;
9. validar setup;
10. registrar hash.

## 8. Nomes determinísticos

Exemplos:

```text
Project: ENZ_REF_001
Design: HFSS_ENZ_G0
Setup: Setup_Driven_25p87
Sweep: Sweep_25p3_26p8
Sphere: FF_Sphere_1deg
Port: P1_WR28
```

## 9. Exportações

- `.aedt`;
- `.s1p`, `.s2p`, `.s4p`;
- FFD ou antenna data;
- CSV de campos;
- imagens;
- convergência;
- mesh statistics;
- JSON de manifesto;
- log PyAEDT;
- log AEDT.

## 10. Recuperação

- timeout controlado;
- tentativa de salvar;
- desconexão sem matar sessão alheia;
- detecção de processo órfão;
- limpeza de lock somente com autorização;
- checkpoint entre fases.

## 11. Testes

- mock sem AEDT;
- smoke test real;
- build sem solve;
- solve curto;
- export Touchstone;
- export far field;
- reconnect;
- cancelamento;
- encerramento limpo.

## 12. Integração futura

A infraestrutura madura do repositório `dipole_gen` é referência de implementação para seleção de runtime, workers independentes, gRPC, extração MIMO, persistência e comparação. O código deve ser reutilizado por adaptação explícita ou módulo compartilhado, evitando cópia cega.

## 13. Implementação auditada em 2026-08-03

**SIMULADO:** o worker `enz-aedt-worker` executou um M0 sintético Eigenmode no
AEDT 2024.2.0 por gRPC nativo com PyAEDT 1.3.0. O run concluído registrou PID,
porta, build, licença, commit Git, hashes, convergência, malha, perfil do solver,
mensagens AEDT e teste de processo órfão.

**DERIVADO:** a extração modal não usa nomes inventados nem o eixo gráfico
`Freq`/`X`. Ela consulta as categorias que o próprio AEDT expõe como
`Eigen Modes` e `Eigen Q`, seguindo o exemplo oficial do PyAEDT, e grava valores
SI em CSV.

**HIPÓTESE:** o arquivo
`m0_cavidade_retangular_smoke.hipotese.v1.yaml` contém dimensões sintéticas
declaradas apenas para testar a infraestrutura.

**DESCONHECIDO:** `local_attach`, execução remota, cancelamento cooperativo e
timeout externo ainda não foram validados. O CLI atual implementa somente
`local_launch` isolado. Operações de solução devem ser iniciadas em processo
worker, nunca na thread da interface.
