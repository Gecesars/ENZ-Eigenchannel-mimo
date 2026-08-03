# 19 — Matriz de arquiteturas candidatas

## A — Quatro cavidades independentes

**Risco:** baixo.  
**Originalidade:** moderada.  
**Uso:** benchmark, extração e sistema 4×4.

Vantagens:

- isolamento mecânico;
- portas claras;
- fácil calibração;
- falha localizada.

Desvantagens:

- volume;
- redundância;
- não prova cavidade compartilhada.

## B — Duas cavidades dual-polarizadas

Cada cavidade produz duas polarizações.

Vantagens:

- integração;
- separação por polarização;
- arquitetura prática.

Riscos:

- polarizações podem ter padrões diferentes;
- acoplamento entre feeds;
- complexidade interna.

## C — Duas subcavidades acopladas por região ENZ

Vantagens:

- controle de estados par/ímpar;
- acoplamento ajustável;
- boa plataforma científica.

Riscos:

- split modal;
- banda estreita;
- sensibilidade.

## D — Cavidade única, portas opostas

Pode excitar paridade diferente.

Risco de ambas as portas excitarem o mesmo modo e produzirem padrões proporcionais.

## E — Cavidade única com grupos de ranhuras

Portas acoplam a regiões ou grupos de ranhuras distintos.

Vantagens:

- padrões controláveis.

Riscos:

- quebra de coerência;
- perda de matching;
- acoplamento forte.

## F — Cavidade com dopantes seletivos

Dopantes localizados alteram o acoplamento porta–modo.

Alta originalidade, maior espaço de projeto.

## G — Cavidade Fano–ENZ

Dois modos acoplados produzem linhas espectrais e padrões distintos.

Risco elevado de sensibilidade e perda.

## H — Estrutura reconfigurável

MEMS, PIN, material variável ou elemento mecânico.

Somente após versão passiva validada.

## Critérios de seleção

| Critério | Peso inicial |
|---|---:|
| prova de dois estados | 25% |
| eficiência | 15% |
| banda comum | 10% |
| correlação de canal | 20% |
| tolerância | 10% |
| volume | 5% |
| originalidade | 10% |
| fabricabilidade | 5% |

## Recomendação

1. reproduzir G0;
2. construir benchmark com cavidades independentes;
3. priorizar duas subcavidades acopladas e cavidade dual-port;
4. somente depois buscar cavidade única de quatro portas.
