# 03 — Guia retangular e ENZ estrutural

## 1. Modo dominante

Para guia retangular preenchido por meio homogêneo, as frequências de corte são

```math
f_{c,mn}
=
\frac{c}{2\sqrt{\varepsilon_r\mu_r}}
\sqrt{
\left(\frac{m}{a}\right)^2+
\left(\frac{n}{b}\right)^2
}.
```

O modo dominante usual é $TE_{10}$:

```math
f_c=\frac{c}{2a\sqrt{\varepsilon_r\mu_r}}.
```

Acima do corte,

```math
\beta=
k_0\sqrt{
\varepsilon_r\mu_r-
\left(\frac{f_c}{f}\right)^2
}.
```

## 2. Permissividade efetiva

Para o modo $TE_{10}$ em guia com $\mu_r\approx1$, é possível escrever uma analogia:

```math
\varepsilon_{\mathrm{eff}}(f)
=
\varepsilon_r
-
\left(\frac{f_c}{f}\right)^2.
```

Quando $f\rightarrow f_c^+$,

```math
\varepsilon_{\mathrm{eff}}\rightarrow0^+,
\qquad
\beta\rightarrow0.
```

Isso é uma emulação modal de ENZ, não significa que o ar adquiriu permissividade material nula. O efeito depende da dispersão estrutural e do modo.

## 3. Velocidades e impedância

A velocidade de fase é

```math
v_p=\frac{\omega}{\beta},
```

e cresce próximo ao corte. A velocidade de grupo, para guia ideal,

```math
v_g=c\sqrt{1-\left(\frac{f_c}{f}\right)^2},
```

tende a zero. Não há violação de causalidade: energia e informação seguem a velocidade de grupo e a resposta dispersiva.

A impedância modal TE é

```math
Z_{TE}=\frac{\omega\mu}{\beta},
```

que cresce próximo ao corte. Essa incompatibilidade de impedância explica por que estruturas ENZ podem apresentar forte reflexão sem mecanismo de matching.

## 4. Fase acumulada

Ao longo de comprimento $L$,

```math
\Delta\phi=\beta L.
```

Uma condição prática de quase uniformidade pode ser

```math
|\beta L|<\phi_{\max},
```

por exemplo 10° ou 20°, mas o limiar deve ser associado à métrica de desempenho, não escolhido arbitrariamente.

## 5. Perdas e dispersão

Em guia real,

```math
\beta_c=\beta-j\alpha,
```

onde $\alpha$ inclui perdas condutivas, dielétricas e de radiação. Próximo ao corte, a relação entre energia armazenada e fluxo de potência aumenta, podendo amplificar perdas. Rugosidade e condutividade do alumínio tornam-se importantes em 26 GHz.

## 6. ENZ ponto versus operação além do ponto

O artigo-base descreve operação em regime ENZ inspirado e comportamento independente de geometria além do ponto ENZ, mantendo permissividade efetiva abaixo da unidade. Isso exige distinguir:

- frequência exata de corte;
- frequência de ressonância da cavidade aberta;
- frequência de matching;
- frequência de máxima eficiência;
- frequência do melhor flat-top.

Essas frequências podem não coincidir.

## 7. Superacoplamento

Em canais ENZ, a transmissão pode tornar-se pouco sensível ao comprimento e a curvas, sob condições de matching. Entretanto, isso não implica invariância universal a qualquer forma, área, abertura, perda ou modo. O superacoplamento depende de:

- continuidade de campos;
- geometria transversal;
- condições de contorno;
- excitação modal;
- impedância efetiva;
- ausência de modos concorrentes.

## 8. Métricas a extrair no HFSS

- $\beta(f)$ por análise modal de guia;
- $Z_{TE}(f)$;
- $\varepsilon_{\mathrm{eff}}(f)$;
- atraso de grupo;
- fase entre planos internos;
- energia armazenada;
- fator de qualidade;
- participação dos modos;
- sensitividade a $a$, $b$, comprimento e área.

## 9. Definição operacional

Neste repositório, “regime ENZ estrutural” significa:

1. modo guiado identificado;
2. $\Re\{\varepsilon_{\mathrm{eff}}\}$ próximo de zero e positivo;
3. pequena progressão de fase na região de interesse;
4. resposta dominada pelo modo declarado;
5. métricas de matching e perda explicitadas.

Sem esses itens, o termo ENZ não deve ser usado apenas por semelhança visual.
