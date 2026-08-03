# 17 — Projeto inverso, adjunto e otimização robusta

## 1. Variáveis

- dimensões contínuas;
- posição de ranhuras;
- número de ranhuras;
- perfil em degrau;
- pinos;
- dopantes;
- portas;
- orientação;
- material.

## 2. Otimização direta

Cada avaliação exige HFSS. Métodos:

- DOE;
- Nelder–Mead;
- CMA-ES;
- Bayesian optimization;
- NSGA-II;
- surrogate models.

## 3. Método adjunto

Para objetivo $J(\mathbf E,\mathbf g)$, o gradiente pode ser obtido com problema adjunto, reduzindo custo para muitas variáveis:

```math
\frac{dJ}{dg_i}
=
\frac{\partial J}{\partial g_i}
-
\Re
\left\{
\boldsymbol\lambda^H
\frac{\partial\mathbf A}{\partial g_i}
\mathbf e
\right\}.
```

Implementação completa no HFSS pode exigir APIs de sensitividade ou exportação para solver próprio.

## 4. Parametrização de forma

Evitar geometria inválida. Usar:

- splines;
- perfis por segmentos;
- level sets;
- variáveis dimensionais com restrições;
- simetria controlada.

## 5. Otimização discreta

Número de pinos, ranhuras e topologia exigem busca combinatória ou relaxamento.

## 6. Modelos substitutos

Treinar regressão para:

- frequência;
- matching;
- ripple;
- ECC;
- capacidade.

Validar incerteza do surrogate.

## 7. Robustez

Se $\boldsymbol\xi$ representa tolerâncias,

```math
\min_{\mathbf g}
\mathbb E_\xi[J(\mathbf g,\xi)]
+
\lambda
\mathrm{Std}_\xi[J].
```

Ou chance constraints:

```math
P(g_k(\mathbf g,\xi)\le0)\ge1-\epsilon.
```

## 8. Monte Carlo

Tolerâncias preliminares:

- ranhuras: ±0,03–0,05 mm;
- gaps: 0–0,05 mm;
- dopante: ±0,05 mm;
- pinos: ±0,03 mm;
- ângulo de módulo: ±0,5°.

Devem ser ajustadas ao processo real.

## 9. Evitar overfitting numérico

- malha congelada quando possível;
- revalidação com malha mais rigorosa;
- pontos fora da amostra;
- solver alternativo em casos selecionados;
- protótipos repetidos.

## 10. Otimização hierárquica

1. matching e modo;
2. flat-top;
3. dual-port;
4. robustez;
5. capacidade;
6. integração 4 portas.
