# 02 — Fundamentos maxwellianos e formulação modal

## 1. Equações no domínio da frequência

Assumindo convenção temporal $e^{j\omega t}$,

```math
\nabla\times\mathbf E=-j\omega\mathbf B,
```

```math
\nabla\times\mathbf H=\mathbf J+j\omega\mathbf D,
```

```math
\nabla\cdot\mathbf D=\rho,
\qquad
\nabla\cdot\mathbf B=0.
```

Em meios lineares locais,

```math
\mathbf D=\bar{\bar\varepsilon}\mathbf E,
\qquad
\mathbf B=\bar{\bar\mu}\mathbf H,
\qquad
\mathbf J=\bar{\bar\sigma}\mathbf E+\mathbf J_s.
```

A estrutura real inclui condutores, dielétricos dispersivos, perdas e fronteiras abertas. Portanto, o operador eletromagnético é, em geral, não hermitiano quando há radiação ou dissipação.

## 2. Equação vetorial de onda

Eliminando $\mathbf H$,

```math
\nabla\times
\left(
\bar{\bar\mu}^{-1}
\nabla\times\mathbf E
\right)
-
\omega^2\bar{\bar\varepsilon}\mathbf E
=
-j\omega\mathbf J_s.
```

No problema de autovalor sem fonte,

```math
\nabla\times
\left(
\bar{\bar\mu}^{-1}
\nabla\times\mathbf E_n
\right)
=
\tilde\omega_n^2
\bar{\bar\varepsilon}\mathbf E_n.
```

Em cavidade fechada ideal, $\tilde\omega_n$ pode ser real. Em cavidade aberta ou com perdas,

```math
\tilde\omega_n=\omega_n+j\gamma_n,
```

com $\gamma_n>0$ para um modo temporalmente decrescente sob a convenção
$e^{j\omega t}$ adotada neste documento, pois
$e^{j\tilde\omega_n t}=e^{j\omega_nt}e^{-\gamma_nt}$. Se a convenção
$e^{-j\omega t}$ for usada, o sinal da parte imaginária deve ser invertido. O
fator de qualidade é aproximadamente

```math
Q_n=\frac{\omega_n}{2\gamma_n}.
```

**DERIVADO:** o sinal acima decorre diretamente da convenção temporal declarada.
Modos quase normais de sistemas abertos e a perturbação de suas frequências
complexas são tratados, por exemplo, por Lai et al., DOI
`10.1103/PhysRevA.41.5187`.

## 3. Energia e potência

A densidade média de potência é dada pelo vetor de Poynting complexo,

```math
\mathbf S_c=\frac12\mathbf E\times\mathbf H^*.
```

A potência média atravessando uma superfície é

```math
P=\Re\left\{
\int_S \mathbf S_c\cdot d\mathbf S
\right\}.
```

Para meios dispersivos, as expressões de energia devem incluir derivadas das constitutivas. Uma forma aproximada, em meio isotrópico com perdas pequenas, é

```math
W_e=
\frac14
\int_V
\frac{\partial(\omega\varepsilon')}{\partial\omega}
|\mathbf E|^2\,dV,
```

```math
W_m=
\frac14
\int_V
\frac{\partial(\omega\mu')}{\partial\omega}
|\mathbf H|^2\,dV.
```

Próximo ao corte, a velocidade de grupo reduzida e o armazenamento de energia podem tornar a estrutura sensível a perdas e tolerâncias.

## 4. Expansão modal

O campo pode ser expandido em modos:

```math
\mathbf E(\mathbf r,\omega)
\approx
\sum_n c_n(\omega)\mathbf e_n(\mathbf r).
```

Os coeficientes dependem de:

- sobreposição entre fonte e modo;
- frequência;
- perdas;
- acoplamento com o exterior;
- perturbações geométricas;
- material;
- portas.

Para uma estrutura multiporta, cada porta produz um vetor distinto de coeficientes modais:

```math
\mathbf c^{(m)}=
[c_1^{(m)},c_2^{(m)},\ldots]^T.
```

A diversidade de padrões pode surgir se diferentes portas excitarem combinações modais suficientemente diferentes.

## 5. Ortogonalidade e biortogonalidade

Em operadores hermitianos, modos distintos são ortogonais sob um produto interno energético. Em estruturas abertas e dissipativas, pode ser necessário usar modos direitos e esquerdos:

```math
\mathcal L\mathbf e_n^R
=
\lambda_n\mathbf e_n^R,
```

```math
\mathcal L^\dagger\mathbf e_n^L
=
\lambda_n^*\mathbf e_n^L,
```

com relação biortogonal

```math
\langle\mathbf e_m^L,\mathbf e_n^R\rangle
\propto\delta_{mn}.
```

Esse formalismo é importante para perturbação de forma e sensibilidade de modos quase degenerados.

## 6. Teorema de reciprocidade

Para estruturas lineares, passivas e recíprocas sem polarização magnética não recíproca, a matriz de espalhamento satisfaz idealmente

```math
\mathbf S=\mathbf S^T.
```

No domínio de campos, a reciprocidade relaciona fontes e observações. Ela permite interpretar o padrão de transmissão de uma porta como sensibilidade de recepção da mesma porta.

## 7. Equivalência de abertura

Uma abertura em parede PEC pode ser substituída por corrente magnética equivalente

```math
\mathbf M_s=-2\hat{\mathbf n}\times\mathbf E_a
```

em formulação de equivalência apropriada. O campo distante é uma transformação integral da distribuição complexa de abertura. Portanto, controlar amplitude e fase nas ranhuras equivale a controlar os coeficientes de radiação.

## 8. Implicação para o projeto

A fase quase uniforme não elimina a necessidade de teoria modal. Ela apenas indica que um modo dominante apresenta pequena variação longitudinal. O projeto deve verificar:

- pureza modal;
- proximidade de modos parasitas;
- participação modal por porta;
- energia armazenada;
- perdas;
- estabilidade do phase center;
- distribuição complexa de abertura.

Uma estrutura aparentemente “uniforme” em um corte pode esconder modos adicionais ou variação tridimensional relevante.
