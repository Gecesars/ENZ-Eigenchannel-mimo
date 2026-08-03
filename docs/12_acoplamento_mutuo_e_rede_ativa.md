# 12 — Acoplamento mútuo, rede ativa e estados coletivos

## 1. Acoplamento não é apenas erro

Em arrays convencionais, reduzir $S_{ij}$ é uma meta comum. Entretanto, acoplamento também cria estados coletivos. O problema correto é separar:

- acoplamento dissipativo;
- acoplamento reativo;
- acoplamento radiativo;
- correlação de padrões;
- mismatch ativo.

## 2. Matriz de impedância

$$
\mathbf V=\mathbf Z\mathbf I.
$$

Escreva

$$
\mathbf Z=
\mathbf R_r+
\mathbf R_\ell+
j\mathbf X.
$$

- $\mathbf R_r$: radiação;
- $\mathbf R_\ell$: perdas;
- $\mathbf X$: energia reativa.

## 3. Potência

$$
P_{\mathrm{acc}}
=
\frac12
\mathbf I^H
(\mathbf R_r+\mathbf R_\ell)
\mathbf I.
$$

$$
P_r=
\frac12
\mathbf I^H\mathbf R_r\mathbf I.
$$

Eficiência para estado $\mathbf I$:

$$
\eta(\mathbf I)
=
\frac{
\mathbf I^H\mathbf R_r\mathbf I
}{
\mathbf I^H(\mathbf R_r+\mathbf R_\ell)\mathbf I
}.
$$

## 4. Estados próprios

Resolver

$$
\mathbf Z\mathbf q_n
=
z_n\mathbf q_n
$$

ou uma formulação generalizada pode revelar estados naturais. A excitação terminal necessária deve ser realizável.

## 5. Superdiretividade

Correntes fortemente anticorrelacionadas podem produzir feixes estreitos em abertura pequena, mas com:

- alto $Q$;
- baixa eficiência;
- sensibilidade;
- correntes elevadas;
- banda estreita.

O projeto não deve perseguir superdiretividade sem contabilizar esses custos.

## 6. Acoplamento útil para MIMO

Um acoplamento controlado pode:

- formar modos par/ímpar;
- separar padrões;
- gerar nulos;
- rotacionar polarização;
- dividir phase centers;
- ajustar degenerescência.

Mas pode também tornar portas redundantes.

## 7. TARC e varredura de fases

Para duas portas iguais,

$$
\mathbf a=
\frac1{\sqrt2}
[1,e^{j\phi}]^T.
$$

Avaliar $\mathrm{TARC}(\phi)$ para $0\le\phi<2\pi$. Para quatro portas, usar amostragem de hiperesfera de fases ou estados de precoding.

## 8. Redes de matching

Comparar:

1. matching individual;
2. matching multiporta desacoplador;
3. matching modal;
4. matching integrado à cavidade;
5. dopagem fotônica.

Uma rede externa pode melhorar matching, mas adiciona perda e complexidade. O mérito da cavidade é incorporar parte da transformação.

## 9. Métrica conjunta

Uma função de custo pode incluir

$$
J=
w_1\mathrm{TARC}
+w_2(1-\eta)
+w_3\rho
+w_4\kappa(\mathbf H)
+w_5Q
+w_6\sigma_{\mathrm{tol}}.
$$

## 10. Regra

Não existe meta universal de $S_{21}<-20$ dB. Esse valor pode ser especificação de engenharia, mas o critério científico é desempenho conjunto.
