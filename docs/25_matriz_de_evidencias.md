# 25 — Matriz de claims e evidências

| Claim | Estado inicial | Evidência necessária |
|---|---|---|
| guia próximo ao corte emula ENZ | PUBLICADO/DERIVADO | dispersão e literatura |
| cavidade do Inatel preserva frequência sob remodelagem | PUBLICADO | artigo e reprodução |
| degrau equaliza amplitudes | PUBLICADO/INFERIDO | campos de abertura |
| pinos suprimem modo indesejado | PUBLICADO | análise modal |
| cavidade compartilhada gera dois padrões úteis | HIPÓTESE | S2P + campos + canal |
| acoplamento pode ser útil | HIPÓTESE | comparação otimizada |
| dopantes seletivos codificam portas | HIPÓTESE | sweep e protótipo |
| arquitetura aumenta capacidade de borda | HIPÓTESE | ensemble equalizado |
| estrutura reduz hardware | HIPÓTESE | BOM e comparação |
| rank 4 é alcançável | HIPÓTESE | canal e medição |
| throughput supera phased array | NÃO SUPORTADO | link completo |

## Regras

1. claim sem evidência permanece hipótese;
2. simulação não prova medição;
3. reprodução não transfere autoria;
4. valor derivado deve declarar hipóteses;
5. resultado de uma frequência não vale para a banda;
6. resultado de um canal não vale universalmente.

## Registro

Cada claim futuro deve incluir:

```yaml
claim_id:
statement:
classification:
sources:
runs:
measurements:
limitations:
reviewer:
date:
```
