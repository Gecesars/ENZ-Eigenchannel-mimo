# 05 — Dopagem fotônica em cavidades ENZ

## 1. Conceito

A dopagem fotônica introduz uma inclusão eletricamente pequena em um hospedeiro ENZ para alterar a resposta efetiva, especialmente a permeabilidade e a impedância, preservando a característica de fase estendida do hospedeiro.

Em um hospedeiro ENZ ideal, o campo magnético pode aproximar-se de uma distribuição espacialmente uniforme. Uma inclusão dielétrica modifica o fluxo e a energia local, permitindo ajustar a resposta global.

## 2. Motivação

Próximo ao corte, a impedância TE pode ser elevada:

```math
Z_{TE}=\frac{\omega\mu}{\beta}.
```

Sem matching, a potência é refletida. O dopante oferece um mecanismo de compensação reativa e transformação de impedância sem uma rede externa convencional.

## 3. Modelo efetivo

Em formulações bidimensionais, a cavidade dopada pode ser representada por uma permeabilidade efetiva $\mu_{\mathrm{eff}}$ que depende de:

- permissividade do dopante;
- tamanho;
- forma;
- posição;
- área total do hospedeiro;
- frequência.

O matching requer simultaneamente:

```math
\Re\{Z_{\mathrm{in}}\}=Z_0,
\qquad
\Im\{Z_{\mathrm{in}}\}=0.
```

O dopante pode ajustar a parte reativa e alterar o acoplamento com as aberturas.

## 4. Trabalho do Inatel de 2025

O artigo *Photonic doping of epsilon-near-zero waveguide cavities for high-gain millimeter-wave antenna arrays*, DOI `10.1063/5.0296722`, demonstrou uma cavidade retangular ENZ por dispersão de guia e inclusões dielétricas. Um protótipo de quatro cavidades com refletores apresentou ganho medido de 22,04 dBi e eficiência de abertura superior a 60%.

Esse trabalho fornece uma base importante para:

- dimensionamento de dopantes;
- matching;
- pinos metálicos;
- construção split-block;
- integração WR-28;
- análise de eficiência.

## 5. Generalização multiporta

Neste projeto, dopantes podem ter funções adicionais:

1. matching de cada porta;
2. controle da degenerescência modal;
3. separação de estados pares e ímpares;
4. rotação de polarização;
5. redistribuição seletiva de amplitude;
6. compensação de acoplamento;
7. hibridização de modos.

Defina o conjunto de dopantes

```math
\mathcal D=
\{D_1,\ldots,D_K\},
```

com

```math
D_k=
[
\varepsilon_{r,k},
\tan\delta_k,
x_k,y_k,z_k,
l_k,w_k,h_k
].
```

## 6. Matriz de transformação

A cavidade pode ser vista como operador:

```math
\mathbf a_{\mathrm{apertura}}
=
\mathbf T_{\mathrm{cav}}(f)
\mathbf v_{\mathrm{portas}}.
```

Os dopantes alteram $\mathbf T_{\mathrm{cav}}$. O objetivo é obter colunas da matriz que produzam estados de abertura distintos e eficientes.

## 7. Riscos

- perda dielétrica do FR4 em 26 GHz;
- variação de $\varepsilon_r$ e $\tan\delta$;
- anisotropia;
- tolerância de espessura;
- gaps de montagem;
- modos localizados indesejados;
- redução de banda;
- aquecimento;
- sensibilidade extrema próxima a ressonância.

## 8. Estratégia de materiais

A reprodução deve começar com FR4 por fidelidade. Depois, comparar:

- FR4 caracterizado;
- Rogers de baixa perda;
- cerâmicas;
- PTFE carregado;
- dopante metálico;
- dopantes múltiplos.

A alteração de material deve ser registrada como nova variante, não como correção silenciosa.

## 9. Experimentos numéricos

- sweep de permissividade;
- sweep de dimensões;
- sweep de posição;
- extração de energia no dopante;
- participação modal;
- matching;
- estabilidade térmica;
- Monte Carlo;
- comparação de um e múltiplos dopantes.

## 10. Hipótese original

Uma distribuição de dopantes pode funcionar como uma rede analógica espacial interna, controlando a transformação porta–abertura. Essa hipótese precisa ser comparada a redes de acoplamento convencionais e a estruturas metamateriais programáveis.
