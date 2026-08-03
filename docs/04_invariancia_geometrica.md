# 04 — Invariância geométrica, perturbação de forma e manifold de projeto

## 1. Invariância não é arbitrariedade

A expressão “independente de geometria” deve ser interpretada com precisão. Uma cavidade real possui portas, ranhuras, perdas, pinos, dielétricos e fronteiras abertas. Logo, a frequência e o campo não podem ser invariantes a qualquer deformação.

A afirmação correta é que existe um conjunto de transformações sob as quais certas grandezas variam pouco.

## 2. Espaço de parâmetros

Defina

$$
\mathbf g=
[g_1,g_2,\ldots,g_N]^T,
$$

incluindo:

- largura e altura;
- comprimentos parciais;
- perfil lateral;
- posição e dimensões das ranhuras;
- degraus e chanfros;
- pinos;
- dopantes;
- portas.

A resposta é um vetor

$$
\mathbf y(\mathbf g)=
[
f_r,
Q,
S_{11},
\eta,
\sigma_\phi,
\mathbf a_{\mathrm{slot}},
\mathbf F
].
$$

## 3. Restrição de área

No artigo-base, a principal transformação preserva

$$
A_c=W_cH_c=108\text{ mm}^2.
$$

Assim,

$$
H_c=\frac{A_c}{W_c}.
$$

Essa restrição define uma curva em espaço bidimensional, mas a estrutura completa possui mais dimensões. Preservar área não garante automaticamente preservação de volume, impedância, modo ou abertura.

## 4. Sensitividade de primeira ordem

Para pequena perturbação $\delta\mathbf g$,

$$
\delta f_r
\approx
\nabla_{\mathbf g}f_r
\cdot
\delta\mathbf g.
$$

Uma direção quase invariante $\mathbf v$ satisfaz

$$
\nabla_{\mathbf g}f_r\cdot\mathbf v\approx0.
$$

O conjunto dessas direções forma um subespaço tangente local.

## 5. Segunda ordem

Se a derivada de primeira ordem for pequena, a curvatura importa:

$$
\delta f_r
\approx
\frac12
\delta\mathbf g^T
\mathbf H_f
\delta\mathbf g,
$$

onde

$$
\mathbf H_f=
\nabla_{\mathbf g}^2f_r.
$$

Uma direção pode parecer invariante em pequenas variações e falhar em deformações maiores.

## 6. Perturbação eletromagnética

Para perturbações materiais pequenas, a variação de frequência pode ser aproximada por

$$
\frac{\Delta\omega}{\omega}
\approx
-\frac12
\frac{
\int_V
\left(
\Delta\varepsilon|\mathbf E|^2
-
\Delta\mu|\mathbf H|^2
\right)dV
}{
\int_V
\left(
\varepsilon|\mathbf E|^2+
\mu|\mathbf H|^2
\right)dV
}.
$$

Para deformações de fronteira, surgem integrais de superfície envolvendo componentes tangenciais e normais. Em cavidades abertas, deve-se usar formulações não hermitianas ou diferenças finitas validadas.

## 7. Manifold de invariância

Defina um conjunto

$$
\mathcal M_\delta=
\left\{
\mathbf g:
\frac{|f_r(\mathbf g)-f_0|}{f_0}<\delta_f,
\;
\sigma_\phi<\delta_\phi,
\;
\eta>\eta_{\min}
\right\}.
$$

A pesquisa procura regiões de $\mathcal M_\delta$ onde o padrão varie fortemente:

$$
\left\|
\frac{\partial\mathbf F}{\partial\mathbf g}
\right\|
\text{ grande},
\qquad
\left|
\frac{\partial f_r}{\partial\mathbf g}
\right|
\text{ pequeno}.
$$

Essa é a liberdade útil para codificação geométrica.

## 8. Métricas

- desvio relativo de frequência;
- variação de banda;
- variância de fase interna;
- desbalanceamento de amplitude nas ranhuras;
- distância entre padrões;
- deslocamento do phase center;
- eficiência;
- proximidade modal;
- robustez a tolerâncias.

## 9. Plano numérico

1. DOE inicial com área constante;
2. sweep de largura;
3. otimização do perfil em degrau;
4. sensitividade de pinos e FR4;
5. SVD da matriz jacobiana de respostas;
6. identificação de direções quase nulas;
7. validação por pontos fora da amostra;
8. Monte Carlo de fabricação.

## 10. Resultado esperado

O produto científico não deve ser “a frequência não muda”. Deve ser um mapa quantitativo que indique:

- quanto muda;
- em qual região;
- por qual mecanismo;
- com qual custo;
- quando a aproximação deixa de valer.
