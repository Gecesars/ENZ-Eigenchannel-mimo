# 10 — MIMO e teoria da informação eletromagnética

## 1. Canal discreto

O modelo MIMO base é

$$
\mathbf y=
\mathbf H\mathbf x+\mathbf n,
$$

com:

- $\mathbf x\in\mathbb C^{N_t}$;
- $\mathbf y\in\mathbb C^{N_r}$;
- $\mathbf H\in\mathbb C^{N_r\times N_t}$;
- $\mathbf n\sim\mathcal{CN}(0,\mathbf R_n)$.

A antena não é separável do canal: ela determina como os modos eletromagnéticos são excitados e observados.

## 2. Capacidade

Para ruído branco e potência igualmente distribuída,

$$
C=
B\log_2\det
\left[
\mathbf I+
\frac{\rho}{N_t}
\mathbf H\mathbf H^H
\right].
$$

Se houver CSI no transmissor e water filling,

$$
C=
B\sum_i
\log_2
\left(
1+\frac{p_i\sigma_i^2}{N_0B}
\right),
$$

onde $\sigma_i$ são valores singulares de $\mathbf H$.

## 3. SVD

$$
\mathbf H=
\mathbf U\mathbf\Sigma\mathbf V^H.
$$

As colunas de $\mathbf V$ são precoders espaciais; as colunas de $\mathbf U$ são combinadores; os valores de $\mathbf\Sigma$ definem os subcanais.

## 4. Rank efetivo

Uma métrica contínua é

$$
\mathbf R=
\mathbf H\mathbf H^H,
$$

$$
p_i=
\frac{\lambda_i}{\sum_j\lambda_j},
$$

$$
r_{\mathrm{eff}}
=
\exp
\left(
-\sum_ip_i\ln p_i
\right).
$$

Rank algébrico pode ser quatro e rank efetivo próximo de um.

## 5. Condição

$$
\kappa(\mathbf H)
=
\frac{\sigma_{\max}}{\sigma_{\min}}.
$$

Valores elevados indicam streams fracos e sensibilidade a ruído e erros de estimação.

## 6. Inclusão da antena

A matriz de canal pode ser escrita como integral de modos angulares:

$$
H_{ij}(f)
=
\int
\mathbf F_{R,i}^H(\Omega_R,f)
\mathbf K(\Omega_R,\Omega_T,f)
\mathbf F_{T,j}(\Omega_T,f)
\,d\Omega_Rd\Omega_T.
$$

Em canal discreto de $L$ caminhos,

$$
H_{ij}(f)
=
\sum_{\ell=1}^{L}
\alpha_\ell
\mathbf F_{R,i}^H(\Omega_{\ell,R},f)
\mathbf P_\ell
\mathbf F_{T,j}(\Omega_{\ell,T},f)
e^{-j2\pi f\tau_\ell}.
$$

## 7. EIT — Electromagnetic Information Theory

A teoria da informação eletromagnética busca formular capacidade diretamente em termos de fontes, campos, operadores de Green, ruído e regiões físicas. Em vez de assumir antenas pontuais, considera operadores contínuos.

Um operador de canal $\mathcal H$ pode ser decomposto:

$$
\mathcal H\psi_n
=
\sigma_n\phi_n.
$$

Os $\psi_n$ são modos de transmissão ótimos no domínio das correntes; $\phi_n$ são modos de recepção. Uma antena física implementa uma subbase desses modos.

## 8. Hipótese do projeto

A cavidade ENZ multiporta seria um aproximador passivo de uma base $\{\psi_n\}$ adequada ao canal-alvo. A geometria e os dopantes atuariam como restrições físicas na síntese da base.

## 9. Throughput

Capacidade de Shannon é limite teórico. Throughput requer:

- modulação e codificação;
- EVM;
- BLER;
- pilotos;
- overhead;
- retransmissão;
- estimação de canal;
- mobilidade;
- latência;
- potência.

A documentação deve separar:

- `capacity_bps`;
- `estimated_phy_throughput_bps`;
- `measured_goodput_bps`.

## 10. Comparações justas

Igualar:

- largura de banda;
- potência aceita total;
- EIRP quando regulatório;
- ruído;
- abertura;
- número de RF chains;
- quantização;
- perdas;
- canal;
- treinamento.

Sem essa equalização, a comparação não é científica.
