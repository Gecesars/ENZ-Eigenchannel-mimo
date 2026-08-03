# 16 — Funções objetivo orientadas a capacidade

## 1. Limitação de objetivos locais

Minimizar $S_{11}$ ou maximizar ganho em um ângulo não garante bom desempenho MIMO.

## 2. Objetivo log-det

```math
J_C(\mathbf g)
=
-\mathbb E_{\mathcal C}
\left[
\log_2
\det
\left(
\mathbf I+
\frac{\rho}{N_t}
\mathbf H(\mathbf g)\mathbf H^H(\mathbf g)
\right)
\right].
```

## 3. Percentis

Para robustez:

```math
J=
-w_{50}C_{50}
-w_5C_5
+w_oP_{\mathrm{out}}.
```

## 4. Valores singulares

Pode-se maximizar o menor valor singular:

```math
J_{\min}=-\mathbb E[\sigma_{\min}^2].
```

Ou equilibrar:

```math
J_{\mathrm{bal}}
=
\mathbb E
\left[
\sum_i
\left(
\log\sigma_i-\overline{\log\sigma}
\right)^2
\right].
```

## 5. Multiobjetivo EM

```math
J_{\mathrm{EM}}
=
w_1L_{\mathrm{match}}
+w_2L_{\mathrm{ripple}}
+w_3L_{\mathrm{SLL}}
+w_4L_{\mathrm{gain}}
+w_5L_{\mathrm{eff}}
+w_6L_{\mathrm{tol}}.
```

## 6. Função conjunta

```math
J=
J_C+
\lambda_{\mathrm{EM}}J_{\mathrm{EM}}
+\lambda_VV
+\lambda_MM.
```

$M$ pode representar massa, complexidade ou custo.

## 7. Restrições

- $S_{ii}<-10$ dB;
- TARC;
- eficiência;
- banda;
- dimensões mínimas;
- distância entre peças;
- temperatura;
- potência;
- phase error;
- material disponível.

## 8. Ensemble curricular

O objetivo não deve otimizar para um canal específico e falhar nos demais. Usar treino, validação e teste de canais.

## 9. Baselines

- geometria original;
- array convencional;
- pesos aleatórios;
- otimização apenas EM;
- otimização apenas ECC;
- otimização capacity-aware.

## 10. Relato

Publicar frente de Pareto e não apenas um ponto escolhido.
