# 14 — Limites fundamentais de banda, eficiência e graus de liberdade

## 1. Limites de pequenas antenas

Para radiador eletricamente pequeno, limites de Chu–Harrington relacionam $Q$ a $ka$. Embora a cavidade do projeto não seja necessariamente pequena em todas as dimensões, a ideia de compromisso permanece:

- banda;
- eficiência;
- volume;
- diretividade;
- número de modos.

## 2. Fator de qualidade e banda

Uma aproximação comum:

$$
B_f\propto\frac1Q.
$$

Matching de múltiplas ressonâncias pode ampliar banda, mas adiciona modos e sensibilidade.

## 3. Limite de Bode–Fano

Redes passivas de matching enfrentam limites integrais entre reflexão e banda. Uma cavidade altamente reativa não pode ser perfeitamente casada em banda arbitrária sem custo.

## 4. Graus de liberdade espaciais

O número de modos radiantes significativos de uma região finita é limitado por seu tamanho elétrico e ambiente. Aumentar portas além desse limite cria redundância.

Uma estimativa assintótica para uma abertura plana envolve área em comprimentos de onda:

$$
N_{\mathrm{DoF}}\sim\frac{2A}{\lambda^2}
$$

para certas polarizações e regiões angulares, mas o coeficiente depende da geometria e do domínio.

## 5. Matriz de radiação

Os autovalores da matriz de resistência radiativa indicam modos eficientes. Modos com autovalores pequenos podem exigir correntes elevadas e apresentar perdas.

## 6. Eficiência

$$
\eta=
\frac{P_r}{P_r+P_c+P_d}.
$$

Em mmWave:

- rugosidade;
- condutividade;
- contatos;
- dielétrico;
- vazamento;
- transições

podem dominar.

## 7. Limite polarimétrico

Em uma direção plana, existem duas polarizações transversais independentes. Mais estados co-localizados exigem diversidade angular, espacial ou modal.

## 8. Capacidade por volume

Uma métrica exploratória:

$$
\mathcal D_{EM}
=
\frac{
r_{\mathrm{eff}}\eta B_f
}{
V/\lambda^3
}.
$$

Não é métrica padronizada e deve ser rotulada como proposta.

## 9. Capacidade por hardware

$$
\mathcal D_C
=
\frac{
C_{5\%}
}{
N_{\mathrm{RF}}P_{DC}V
}.
$$

Útil para comparar solução passiva e phased array.

## 10. Implicação

A pesquisa não busca violar limites. Busca usar melhor os graus de liberdade disponíveis por meio de codificação geométrica e modal.
