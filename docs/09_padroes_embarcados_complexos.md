# 09 — Padrões embarcados complexos e correlação

## 1. Definição

O padrão embarcado da porta $m$ é obtido excitando essa porta e terminando as demais. É uma grandeza vetorial complexa:

```math
\mathbf F_m(\theta,\phi,f)
=
E_{\theta,m}\hat{\boldsymbol\theta}
+
E_{\phi,m}\hat{\boldsymbol\phi}.
```

Magnitude normalizada não é suficiente para MIMO. Fase absoluta relativa, polarização e potência precisam ser preservadas.

## 2. Normalização

Possíveis normalizações:

- potência incidente de 1 W;
- potência aceita de 1 W;
- ganho realizado;
- campo a distância de referência.

A comparação entre portas deve usar a mesma convenção.

## 3. Correlação de envelope por campo

Para ambiente isotrópico,

```math
\rho_{ij}
=
\frac{
\left|
\int_{4\pi}
\mathbf F_i\cdot\mathbf F_j^*d\Omega
\right|^2
}{
\left[
\int_{4\pi}\|\mathbf F_i\|^2d\Omega
\right]
\left[
\int_{4\pi}\|\mathbf F_j\|^2d\Omega
\right]
}.
```

## 4. Correlação ponderada

Em ambiente real,

```math
\rho_{ij}^{(P)}
=
\frac{
\left|
\int
\mathbf F_i^H
\mathbf P(\Omega)
\mathbf F_j\,d\Omega
\right|^2
}{
\int\mathbf F_i^H\mathbf P\mathbf F_i\,d\Omega
\int\mathbf F_j^H\mathbf P\mathbf F_j\,d\Omega
}.
```

$\mathbf P$ pode representar espectro angular e acoplamento polarimétrico.

## 5. Matriz de Gram radiante

Defina

```math
G_{ij}
=
\langle\mathbf F_i,\mathbf F_j\rangle_P.
```

Os autovalores de $\mathbf G$ indicam quantas direções radiantes independentes existem sob o ambiente considerado.

## 6. Phase center

Phase centers diferentes alteram a fase do padrão. Para comparar estados internos, deve-se:

- registrar o phase center físico;
- evitar realinhamento arbitrário que artificialmente reduza correlação;
- distinguir decorrelação por posição de decorrelação por forma.

## 7. Polarização

A decomposição deve incluir co- e cross-polarização conforme base definida. Para canais polarimétricos, usar matriz de espalhamento de cada caminho:

```math
\mathbf P_\ell=
\begin{bmatrix}
p_{\theta\theta}&p_{\theta\phi}\\
p_{\phi\theta}&p_{\phi\phi}
\end{bmatrix}.
```

## 8. Discretização

A integração esférica requer pesos:

```math
d\Omega=\sin\theta\,d\theta\,d\phi.
```

Uma grade uniforme em $\theta$ e $\phi$ não deve ser somada sem $\sin\theta$.

## 9. Frequência

A correlação deve ser calculada por frequência. Em banda larga, padrões e phase centers variam. Pode-se usar:

- pior caso;
- média;
- percentis;
- correlação conjunta tempo–frequência.

## 10. Exportação HFSS

Preferir dados de antena embarcados com:

- $E_\theta$ real e imaginário;
- $E_\phi$ real e imaginário;
- frequência;
- porta;
- sistema de coordenadas;
- impedância;
- phase center;
- potência.

## 11. Critério inicial

ECC inferior a 0,3 é um limiar preliminar, não garantia. A decisão final depende de capacidade, eficiência, SNR e distribuição angular do canal.
