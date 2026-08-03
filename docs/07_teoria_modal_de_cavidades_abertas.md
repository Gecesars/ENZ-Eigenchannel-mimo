# 07 — Teoria modal de cavidades abertas

## 1. Cavidade fechada versus radiador

Uma cavidade PEC fechada suporta modos discretos sem perda de radiação. Ao abrir ranhuras, conectar guia e incluir perdas, os modos tornam-se ressonâncias abertas com frequências complexas.

```math
\tilde\omega_n=\omega_n+j\gamma_n.
```

O sinal corresponde à convenção temporal $e^{j\omega t}$ adotada em
[`02_fundamentos_maxwellianos.md`](02_fundamentos_maxwellianos.md), com
$\gamma_n>0$ representando decaimento. Sob $e^{-j\omega t}$, usa-se
$\tilde\omega_n=\omega_n-j\gamma_n$.

O campo total pode ser decomposto em modos quase normais mais uma contribuição de fundo.

## 2. Fator de qualidade

```math
Q_n=
\frac{\omega_n}{2\gamma_n}.
```

O $Q$ carregado combina:

```math
\frac1{Q_L}
=
\frac1{Q_c}
+
\frac1{Q_d}
+
\frac1{Q_r}
+
\frac1{Q_e},
```

onde os termos representam perdas condutivas, dielétricas, radiativas e acoplamento externo.

## 3. Acoplamento modal

Se dois modos estão próximos,

```math
\mathbf H_{\mathrm{eff}}=
\begin{bmatrix}
\omega_1-j\gamma_1 & \kappa\\
\kappa & \omega_2-j\gamma_2
\end{bmatrix}.
```

Os autovalores híbridos dependem de $\kappa$. Pinos metálicos podem reduzir ou redirecionar esse acoplamento.

## 4. Degenerescência

Estados degenerados têm mesma frequência, mas campos distintos. Em uma cavidade multiporta, degenerescência pode ser útil para produzir padrões diferentes na mesma banda. Contudo, pequenas assimetrias podem dividir as frequências e rotacionar a base modal.

## 5. Modos pares e ímpares

Portas simétricas podem excitar combinações:

```math
\mathbf v_+=
\frac1{\sqrt2}[1,1]^T,
\qquad
\mathbf v_-=
\frac1{\sqrt2}[1,-1]^T.
```

Os estados par e ímpar podem apresentar distribuições de abertura e padrões distintos. Essa é uma rota promissora para a experiência dual-port.

## 6. Participação modal

A participação de um modo $n$ sob porta $m$ pode ser estimada por sobreposição:

```math
c_n^{(m)}
\propto
\frac{
\langle\mathbf e_n,\mathbf J_m\rangle
}{
\omega-\tilde\omega_n
}.
```

No HFSS, a comparação entre Eigenmode e Driven Modal deve identificar quais modos participam da resposta.

## 7. Exceptional points e não hermiticidade

Estruturas abertas podem apresentar coalescência de autovalores e autovetores em pontos excepcionais. Embora cientificamente interessante, esse regime tende a ser sensível a perdas e tolerâncias. Não é prioridade inicial, mas deve ser reconhecido como possibilidade em sistemas fortemente acoplados.

## 8. Teoria de modos acoplados temporal

Para amplitudes modais $\mathbf a$,

```math
\frac{d\mathbf a}{dt}
=
(j\mathbf\Omega-\mathbf\Gamma)\mathbf a
+
\mathbf K^T\mathbf s_+,
```

```math
\mathbf s_-=
\mathbf C\mathbf s_+
+
\mathbf D\mathbf a.
```

No regime estacionário,

```math
\mathbf a=
[j(\omega\mathbf I-\mathbf\Omega)+\mathbf\Gamma]^{-1}
\mathbf K^T\mathbf s_+.
```

Esse modelo liga portas, modos, perdas e espalhamento.

## 9. Meta de validação

- obter eigenfrequências;
- identificar simetria dos modos;
- calcular $Q$;
- comparar campos;
- medir divisão modal com pinos;
- construir modelo reduzido;
- validar contra $S$ e far field.

## 10. Cuidado metodológico

Um modo identificado pelo nome $TE_{10}$ em uma seção de guia pode tornar-se um modo híbrido na cavidade alargada, carregada e aberta. A nomenclatura deve descrever a origem dominante, não afirmar pureza absoluta.
