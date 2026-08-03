# 15 — Modelos de canal em ondas milimétricas

## 1. Necessidade de ensemble

Uma antena orientada a capacidade deve ser avaliada em conjunto de canais, não em um único cenário.

## 2. Modelo geométrico

Para $L$ caminhos,

$$
\mathbf H(f)=
\sum_{\ell=1}^{L}
\alpha_\ell
\mathbf a_R(\Omega_{\ell,R},f)
\mathbf a_T^H(\Omega_{\ell,T},f)
e^{-j2\pi f\tau_\ell}.
$$

Com padrões reais, os vetores de steering são substituídos por campos embarcados polarimétricos.

## 3. Clusters

Cada cluster pode ter:

- ângulo médio;
- spread azimutal;
- spread de elevação;
- atraso;
- potência;
- Doppler;
- matriz polarimétrica;
- visibilidade.

## 4. LoS

O caminho LoS pode dominar em mmWave. O fator $K$ de Rician deve ser variado. Uma antena de fan beam pode melhorar robustez angular, mas reduzir ganho de pico.

## 5. Bloqueio

Modelos:

- atenuação de caminho;
- remoção de cluster;
- difração;
- corpo humano;
- máquina metálica;
- dinâmica temporal.

## 6. Mobilidade

$$
f_{D,\ell}
=
\frac{v}{\lambda}
\cos\psi_\ell.
$$

Padrões largos podem reduzir necessidade de tracking, mas aumentar interferência e diminuir SNR.

## 7. Cenários iniciais

### C0 — LoS puro

Serve como caso adverso para rank compacto.

### C1 — LoS mais reflexão dominante

Verifica padrão complementar.

### C2 — corredor

Clusters nas paredes e teto.

### C3 — fábrica

Espalhamento metálico e bloqueios.

### C4 — hotspot indoor

Usuários distribuídos em setor.

### C5 — canal dinâmico

Movimento e mudança de visibilidade.

## 8. Calibração do modelo

O ensemble deve ser baseado em:

- medições próprias;
- modelos 3GPP quando aplicáveis;
- literatura de channel sounding;
- ray tracing;
- parâmetros declarados.

## 9. Métricas

- capacity CDF;
- outage;
- singular value CDF;
- condition number;
- rank efetivo;
- angular coverage;
- robustez a bloqueio;
- overhead.

## 10. Reprodutibilidade

Cada realização deve possuir seed. O conjunto de canais deve ser congelado para comparação entre antenas.
