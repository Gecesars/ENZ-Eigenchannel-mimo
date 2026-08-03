# 26 — Benchmarks e critérios de aceitação

## 1. Referências

### B0 — artigo-base

Uma porta, cinco ranhuras, flat-top.

### B1 — duas cópias coorientadas

Mostra redundância.

### B2 — duas cavidades orientadas

Diversidade de padrão por orientação.

### B3 — dual-pol convencional

Referência polarimétrica.

### B4 — quatro subarrays fixos

Mesmo número de RF chains.

### B5 — phased array híbrido

Referência de pico e steering.

## 2. Equalização

- área de abertura;
- volume quando aplicável;
- banda;
- potência aceita;
- número de portas;
- RF chains;
- perdas;
- canal;
- receptor.

## 3. Metas preliminares EM

| Métrica | Meta | Limite |
|---|---:|---:|
| $S_{ii}$ | < −15 dB | < −10 dB |
| isolamento | < −20 dB | < −15 dB |
| eficiência | > 80% | > 70% |
| ripple | < 1 dB | < 1,5 dB |
| XPD | > 20 dB | > 15 dB |
| ECC isotrópica | < 0,1 | < 0,3 |
| TARC | < −10 dB | < −8 dB |

Metas são requisitos de projeto, não resultados.

## 4. Metas MIMO preliminares

- rank efetivo mediano > 3 em cenários ricos para 4 portas;
- capacidade de pico ≥ 80% do híbrido;
- capacidade média ≥ referência fixa;
- percentil 5% ≥ 1,3× referência fixa;
- treinamento ≤ 0,5× híbrido.

Essas metas podem ser revisadas após baseline.

## 5. Métricas de custo

- volume;
- massa;
- peças;
- parafusos;
- tempo de usinagem;
- transições;
- phase shifters;
- calibração;
- consumo.

## 6. Aceitação científica

Uma arquitetura avança quando melhora a função objetivo com intervalo de confiança e sem violar restrições.
