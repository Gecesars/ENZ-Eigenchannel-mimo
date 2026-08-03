# 11 — Formulação por operadores e autocanais

## 1. Cadeia de operadores

Defina:

```math
\mathcal T:
\mathbb C^M
\rightarrow
\mathcal J,
```

mapeando portas em correntes;

```math
\mathcal R:
\mathcal J
\rightarrow
\mathcal F,
```

mapeando correntes em campos;

```math
\mathcal P:
\mathcal F
\rightarrow
\mathbb C^{N_r},
```

mapeando campos em tensões recebidas.

O canal terminal é

```math
\mathbf H=
\mathcal P\mathcal R\mathcal T.
```

## 2. Base radiativa

Os padrões embarcados são as imagens da base canônica de portas:

```math
\mathbf F_m=
\mathcal R\mathcal T\mathbf e_m.
```

Uma combinação de portas $\mathbf q$ produz

```math
\mathbf F_{\mathbf q}
=
\sum_mq_m\mathbf F_m.
```

## 3. Matriz de Gram

Sob produto interno ambiental,

```math
G_{ij}
=
\langle\mathbf F_i,\mathbf F_j\rangle_P.
```

A decomposição

```math
\mathbf G=
\mathbf Q\mathbf\Lambda\mathbf Q^H
```

fornece combinações terminais que diagonalizam a potência/correlação radiante para aquele ambiente.

## 4. Autocanais

Se o receptor e o canal forem incluídos,

```math
\mathbf H^H\mathbf H\mathbf v_n
=
\sigma_n^2\mathbf v_n.
```

$\mathbf v_n$ é um autocanal terminal. O problema de projeto é escolher a geometria para tornar os primeiros $\sigma_n$ grandes e equilibrados.

## 5. Operador de radiação

Em discretização de correntes,

```math
\mathbf f=\mathbf R\mathbf j,
```

e a potência radiada é

```math
P_r=
\mathbf j^H\mathbf R_r\mathbf j,
```

onde $\mathbf R_r$ é parte real do operador de impedância radiativa. Modos característicos resolvem, em formulação clássica,

```math
\mathbf X\mathbf J_n
=
\lambda_n\mathbf R\mathbf J_n.
```

## 6. Portas como subespaço

Uma estrutura de $M$ portas acessa no máximo um subespaço de dimensão $M$. Mesmo que a estrutura tenha muitos modos, as portas podem excitar apenas combinações limitadas.

A matriz de acoplamento porta–modo é

```math
\mathbf B_{nm}
=
\langle\mathbf e_n,\mathbf J_m\rangle.
```

Seu rank limita o número de estados acessíveis.

## 7. Objetivo de síntese

Para ensemble de canais $\mathcal C$,

```math
\max_{\mathbf g,\mathbf p}
\;
\mathbb E_{\mathcal C}
\left[
\Phi(
\mathbf H(\mathbf g,\mathbf p;\mathcal C)
)
\right],
```

onde $\Phi$ pode ser capacidade, log-det, percentil ou rank efetivo.

## 8. Regularização física

Restrições:

- passividade;
- reciprocidade;
- eficiência;
- banda;
- volume;
- tolerância;
- isolamento/matching ativo;
- materiais;
- fabricação.

## 9. Novidade potencial

A contribuição mais forte seria demonstrar que uma cavidade de fase quase uniforme implementa um operador passivo de transformação espacial cuja geometria pode ser otimizada para aproximar uma base de autocanais. Isso vai além de “antena MIMO ENZ” e define uma classe de dispositivos analógicos espaciais.

## 10. Prova necessária

- identificar o subespaço modal;
- medir matriz porta–modo;
- extrair matriz de Gram de campos;
- mostrar dois autovalores significativos;
- demonstrar benefício de canal;
- comparar com estrutura convencional;
- validar em hardware.
