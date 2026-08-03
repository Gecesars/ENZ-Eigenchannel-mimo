# 06 — Ranhuras, correntes equivalentes e síntese de abertura

## 1. Ranhura em parede condutora

Uma ranhura em uma parede metálica interrompe a corrente superficial e acopla o campo interno ao espaço livre. Pelo princípio de equivalência, o campo na abertura pode ser representado por corrente magnética equivalente

$$
\mathbf M_s=-2\hat{\mathbf n}\times\mathbf E_a.
$$

A amplitude e a fase de $\mathbf E_a$ determinam a contribuição radiada.

## 2. Array equivalente

Para $N$ ranhuras,

$$
\mathbf F(\Omega)
=
\sum_{n=1}^{N}
a_n
\mathbf f_n(\Omega)
e^{jk_0\hat{\mathbf r}\cdot\mathbf r_n},
$$

onde $a_n$ contém amplitude e fase de acoplamento. Em uma cavidade ENZ inspirada, a fase interna tende a variar pouco, mas:

- a fase de radiação inclui posição;
- cada ranhura pode ter phase center diferente;
- acoplamento mútuo altera $a_n$;
- degraus e paredes alteram $\mathbf f_n$.

## 3. Pencil beam e fan beam

Uma abertura estreita em duas dimensões produz feixe relativamente largo. Uma abertura alongada produz feixe estreito no plano associado ao comprimento e largo no plano ortogonal. Ao redistribuir ranhuras em uma direção mantendo fase coerente, o artigo-base converte pencil beam em fan beam.

## 4. Topo plano

Um padrão flat-top exige distribuição de abertura que compense a tendência natural de máximo central. Em arrays convencionais, isso é feito por pesos de amplitude e fase. No artigo-base, o perfil em degrau altera a impedância espacial e equaliza o acoplamento das ranhuras.

Uma função objetivo pode ser

$$
J_{\mathrm{flat}}
=
\int_{\Omega_s}
\left[
G(\Omega)-G_0
\right]^2d\Omega
+
\lambda_{\mathrm{out}}
\int_{\Omega\notin\Omega_s}
G(\Omega)d\Omega.
$$

## 5. Ripple

No setor $\Omega_s$,

$$
R_{\mathrm{dB}}
=
\max_{\Omega_s}G_{\mathrm{dB}}
-
\min_{\Omega_s}G_{\mathrm{dB}}.
$$

A métrica deve ser calculada por frequência. Um bom ripple na frequência central não garante estabilidade na banda.

## 6. Larguras de feixe

- largura de 1 dB: região em que o ganho permanece a menos de 1 dB do máximo;
- HPBW: largura de 3 dB;
- largura útil pode incluir restrições de ripple, SLL e polarização.

## 7. Sidelobe level

$$
SLL=
G_{\mathrm{lóbulo\ lateral,max}}
-
G_{\mathrm{principal,max}}.
$$

Em flat-top, identificar o fim do lóbulo principal exige critério consistente, pois o topo é largo.

## 8. Extração de excitação por ranhura

No HFSS, criar superfícies de amostragem em cada abertura e calcular:

$$
A_n=
\left|
\int_{S_n}
\mathbf E_t\cdot\hat{\mathbf u}\,dS
\right|,
$$

$$
\phi_n=
\arg
\left[
\int_{S_n}
\mathbf E_t\cdot\hat{\mathbf u}\,dS
\right].
$$

Registrar também potência radiada local e corrente superficial.

## 9. Síntese inversa

Dado um padrão desejado, pode-se calcular uma distribuição de abertura alvo e otimizar a geometria para aproximá-la. A cadeia é:

$$
F_{\mathrm{alvo}}
\rightarrow
a_{n,\mathrm{alvo}}
\rightarrow
\text{geometria da cavidade}.
$$

Essa é uma forma de projeto inverso com restrições físicas e modais.

## 10. Extensão MIMO

Para cada porta $m$,

$$
\mathbf a^{(m)}=
[a_1^{(m)},\ldots,a_N^{(m)}]^T.
$$

A diversidade depende da independência entre esses vetores sob o operador de radiação. Não basta trocar a porta se as distribuições $\mathbf a^{(m)}$ forem proporcionais.
