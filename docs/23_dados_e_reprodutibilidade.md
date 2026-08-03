# 23 — Contrato de dados, artefatos e reprodutibilidade

## 1. Identidade da execução

Cada run recebe:

```text
ENZ-YYYYMMDD-HHMMSS-<hash>
```

## 2. Manifesto

Campos obrigatórios:

- commit;
- dirty state;
- AEDT version/build;
- PyAEDT;
- Python;
- SO;
- hostname;
- CPU/RAM;
- licença;
- porta gRPC;
- PID;
- geometria;
- solver;
- material;
- malha;
- duração;
- status.

## 3. Hash

Hash SHA-256 de:

- especificação;
- projeto;
- Touchstone;
- far fields;
- resultados;
- scripts.

## 4. Esquema de diretório

```text
artefatos/runs/<run_id>/
├── manifest.json
├── input/
├── aedt/
├── network/
├── fields/
├── farfield/
├── metrics/
├── plots/
└── logs/
```

## 5. Grandezas complexas

Nunca armazenar apenas magnitude quando fase for relevante. Formatos:

```json
{"real": 0.1, "imag": -0.2}
```

ou pares de colunas.

## 6. Coordenadas

Registrar:

- origem;
- eixos;
- convenção $\theta,\phi$;
- base polarimétrica;
- phase center;
- unidades.

## 7. Metadados de porta

- nome;
- posição;
- orientação;
- modo;
- impedância;
- de-embedding;
- terminação.

## 8. Dados de canal

- seed;
- caminhos;
- ângulos;
- atrasos;
- Doppler;
- polarização;
- potência;
- cenário.

## 9. Resultados imutáveis

Execuções concluídas não são sobrescritas. Nova configuração gera novo run.

## 10. Dados negativos

Falhas de convergência, geometrias inválidas e resultados ruins devem ser preservados em índice de falhas para evitar repetição e viés de publicação.

## 11. Licença de dados

Dados próprios: CC BY 4.0, salvo indicação. Dados de terceiros: licença original.
