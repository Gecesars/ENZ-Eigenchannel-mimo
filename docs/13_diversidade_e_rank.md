# 13 — Diversidade de padrão, polarização, posição e rank

## 1. Mecanismos de diversidade

### Polarização

Dois estados ortogonais podem reduzir correlação se o canal preservar diversidade polarimétrica. Em ambientes com forte despolarização, o benefício muda.

### Padrão

Padrões diferentes iluminam clusters distintos.

### Posição

Separação espacial cria fases de caminho diferentes.

### Paridade modal

Modos pares e ímpares podem produzir nulos e máximos complementares.

### Frequência

Em banda larga, diferentes frequências observam canais distintos, mas isso não substitui rank espacial na mesma subportadora.

## 2. Far-field LoS

Em canal LoS distante, elementos co-localizados com padrões idênticos tendem a rank baixo. Para arrays uniformes Tx/Rx, uma condição aproximada de espaçamento para LoS MIMO é

$$
d_Td_R\approx\frac{\lambda R}{N}.
$$

Para $d_T=d_R=d$,

$$
d\approx\sqrt{\frac{\lambda R}{N}}.
$$

Em 25,87 GHz, $\lambda_0\approx11,59$ mm. Para $N=4$:

- $R=5$ m: $d\approx120$ mm;
- $R=10$ m: $d\approx170$ mm;
- $R=20$ m: $d\approx241$ mm;
- $R=30$ m: $d\approx295$ mm.

Uma estrutura compacta não deve prometer rank quatro em LoS puro sem outra fonte de diversidade.

## 3. Multipercurso

Em ambientes ricos, clusters angulares permitem que padrões distintos observem combinações diferentes. A diversidade de padrão pode ser mais valiosa que grande separação.

## 4. Polarização dual

O alvo de duas polarizações pode usar:

- $\pm45^\circ$;
- H/V;
- circular direita/esquerda.

A escolha depende do canal e da montagem. A polarização deve ser avaliada com matriz de acoplamento do caminho.

## 5. Rank adaptativo

O sistema não deve forçar quatro streams. Defina limiar por valores singulares:

$$
r^\star=
\max\left\{
r:
\mathrm{SINR}_i>\gamma_{\min},
i\le r
\right\}.
$$

## 6. Diversidade versus multiplexação

Diversidade envia redundância para reduzir erro. Multiplexação envia streams independentes. A mesma antena pode alternar entre:

- rank 1 beamforming;
- rank 2 robusto;
- rank 4 em canal favorável.

## 7. Indicadores

- ECC;
- diversidade gain;
- MEG;
- CCL;
- TARC;
- singular values;
- effective rank;
- outage capacity;
- BLER;
- throughput.

## 8. Padrões complementares

Um projeto útil pode gerar:

- padrão A com energia no setor esquerdo;
- padrão B com energia no setor direito;
- polarizações cruzadas em cada família.

Mas padrões completamente separados podem causar desigualdade de SNR. O ótimo pode exigir sobreposição controlada.

## 9. Cenários

1. corredor LoS;
2. corredor com reflexão lateral;
3. fábrica com metal;
4. hotspot indoor;
5. bloqueio parcial;
6. usuário móvel;
7. LoS distribuído com painéis afastados.

## 10. Conclusão

Rank é propriedade do sistema antena–canal–receptor. A geometria só pode criar potencial de diversidade, nunca garantir rank universal.
