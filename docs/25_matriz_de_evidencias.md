# 25 — Matriz de claims e evidências

| Claim | Estado inicial | Evidência necessária |
|---|---|---|
| guia próximo ao corte emula ENZ | PUBLICADO | literatura primária e reprodução modal |
| expressão de dispersão usada no projeto | DERIVADO | derivação algébrica e teste analítico |
| cavidade do Inatel preserva frequência sob remodelagem | PUBLICADO | artigo e reprodução |
| artigo atribui ao degrau a equalização de amplitudes | PUBLICADO | artigo e campos de abertura da reprodução |
| pinos suprimem modo indesejado | PUBLICADO | análise modal |
| cavidade compartilhada gera dois padrões úteis | HIPÓTESE | S2P + campos + canal |
| acoplamento pode ser útil | HIPÓTESE | comparação otimizada |
| dopantes seletivos codificam portas | HIPÓTESE | sweep e protótipo |
| arquitetura aumenta capacidade de borda | HIPÓTESE | ensemble equalizado |
| estrutura reduz hardware | HIPÓTESE | BOM e comparação |
| rank 4 é alcançável | HIPÓTESE | canal e medição |
| throughput supera phased array | HIPÓTESE | modelo de enlace completo ou medição |
| worker M0 sintético conclui no AEDT 2024 R2 | SIMULADO | run `ENZ-20260803-165824-52288067` |
| espectro analítico da cavidade PEC segue $f_{mnp}$ | DERIVADO | derivação e teste unitário |
| M0–M4 reproduzem o artigo-base | DESCONHECIDO | cotas completas + runs convergidos |

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

O schema canônico é
`enz-eigenchannel-mimo/claim-record/v1`, distribuído em
`src/enz_eigenchannel_mimo/schemas/claim-record-v1.schema.json`. Combinações
como `PUBLICADO/DERIVADO` e classes auxiliares como `NÃO SUPORTADO` não são
válidas. Quando houver duas naturezas de evidência, registrar dois claims
relacionados.
