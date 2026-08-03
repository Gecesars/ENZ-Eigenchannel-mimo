# 08 — Modelagem multiporta e matriz de espalhamento

## 1. Ondas de potência

Para $M$ portas,

```math
\mathbf b=\mathbf S\mathbf a,
```

onde $\mathbf a$ são ondas incidentes e $\mathbf b$ ondas refletidas.

A matriz

```math
\mathbf S(f)\in\mathbb C^{M\times M}
```

deve ser extraída com referência de impedância e plano de referência declarados.

## 2. Reciprocidade e passividade

Para estrutura recíproca ideal,

```math
S_{ij}=S_{ji}.
```

Para passividade,

```math
\mathbf S^H\mathbf S\preceq\mathbf I
```

quando as portas representam todos os canais guiados e as perdas/radiação removem potência.

## 3. Matching ativo

Com excitação simultânea $\mathbf a$,

```math
\Gamma_{m,\mathrm{ativa}}
=
\frac{b_m}{a_m}
=
\frac{\sum_nS_{mn}a_n}{a_m}.
```

Uma porta bem casada isoladamente pode ficar mal casada sob combinação de fases.

## 4. TARC

O Total Active Reflection Coefficient é

```math
\mathrm{TARC}
=
\sqrt{
\frac{\mathbf b^H\mathbf b}
{\mathbf a^H\mathbf a}
}.
```

Deve ser avaliado para combinações relevantes de amplitude e fase, não apenas uma combinação.

## 5. Matriz de impedância

```math
\mathbf Z=
Z_0
(\mathbf I+\mathbf S)
(\mathbf I-\mathbf S)^{-1}.
```

Autovetores de $\mathbf Z$ ou $\mathbf S$ podem revelar combinações naturais de portas.

## 6. Modos de espalhamento

```math
\mathbf S\mathbf q_m
=
\lambda_m\mathbf q_m.
```

Excitar $\mathbf q_m$ pode produzir um estado coletivo. Entretanto, ortogonalidade terminal não garante ortogonalidade de radiação.

## 7. Potência aceita

```math
P_{\mathrm{acc}}
=
\mathbf a^H\mathbf a-
\mathbf b^H\mathbf b.
```

A comparação de ganho e capacidade deve normalizar por potência aceita, e não apenas potência incidente.

## 8. Embedding e terminações

Ao extrair padrão embarcado da porta $m$:

- porta $m$ excitada;
- demais portas terminadas em impedância definida;
- potência incidente e aceita registradas;
- phase center definido;
- referência de fase preservada.

## 9. CCL e eficiência

Métricas baseadas em $S$ podem estimar perdas de capacidade, mas não substituem correlação de far field quando há perdas ou padrões complexos. CCL deve ser rotulado como estimador baseado em rede ou cálculo completo de campo.

## 10. Dados obrigatórios

- Touchstone completo;
- impedância de referência;
- frequência;
- port mapping;
- orientação de cada porta;
- de-embedding;
- calibração;
- potência;
- terminação;
- versão do modelo.

## 11. Experiência dual-port

Casos iniciais:

1. duas portas opostas;
2. duas portas ortogonais;
3. portas em subcavidades;
4. porta elétrica e porta magnética;
5. excitação de grupos de ranhuras;
6. paridade modal.

A seleção não deve ser baseada apenas no menor $S_{21}$, mas no conjunto matching–eficiência–padrão–canal.
