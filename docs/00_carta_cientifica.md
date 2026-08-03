# 00 — Carta científica

## 1. Objeto da pesquisa

O objeto de estudo não é simplesmente “uma antena ENZ MIMO”. Essa expressão é ampla demais e pode ocultar a questão científica real. O objeto é o conjunto de operadores que transforma excitações terminais em correntes, campos radiados e, por fim, canais de comunicação:

$$
\mathcal T_{\mathrm{porta}\rightarrow\mathrm{corrente}},
\qquad
\mathcal R_{\mathrm{corrente}\rightarrow\mathrm{campo}},
\qquad
\mathcal P_{\mathrm{campo}\rightarrow\mathrm{canal}}.
$$

Para $M$ portas,

$$
\mathbf a_t=
[a_1,\ldots,a_M]^T
$$

define as ondas incidentes nos terminais. A estrutura passiva produz correntes

$$
\mathbf J(\mathbf r)=
\sum_{m=1}^{M}a_m\mathbf J_m(\mathbf r),
$$

e campos embarcados

$$
\mathbf F(\Omega)=
\sum_{m=1}^{M}a_m\mathbf F_m(\Omega).
$$

O ambiente de propagação e o receptor mapeiam esses campos na matriz de canal $\mathbf H$. A pesquisa procura geometrias, portas e perturbações para as quais os dois primeiros operadores formem uma base eficiente e robusta, capaz de melhorar os valores singulares do terceiro operador em um conjunto de ambientes explicitamente definido.

## 2. Perguntas fundamentais

1. Qual é o regime eletromagnético exato que justifica chamar a cavidade de “ENZ inspirada”?
2. A invariância de frequência é global, local ou apenas aproximada?
3. Quais deformações preservam frequência, fase, impedância e eficiência simultaneamente?
4. É possível criar dois estados radiantes de baixa correlação na mesma estrutura e banda?
5. Esses estados resultam de polarização, paridade modal, distribuição de ranhuras, acoplamento ou dopagem?
6. O acoplamento entre portas deve ser minimizado ou projetado?
7. A vantagem sobre subarrays convencionais sobrevive quando abertura, potência e cadeias RF são equalizadas?
8. Qual é o preço em banda, eficiência, sensibilidade de fabricação e complexidade?
9. Em quais canais a arquitetura melhora capacidade e em quais não melhora?
10. Há uma formulação geral por operadores que permita sintetizar diretamente autocanais?

## 3. Hipóteses principais

### H1 — Manifold de invariância geométrica restrita

Existe um conjunto local não trivial de deformações $\mathbf g$ para o qual

$$
\left|\frac{\partial f_r}{\partial \mathbf g}\right|
$$

é pequeno, enquanto a distribuição de amplitude nas ranhuras varia de forma significativa.

### H2 — Síntese seletiva por porta

Uma estrutura compartilhada ou fortemente acoplada pode sustentar duas excitações terminalmente acessíveis com:

- frequências próximas;
- eficiência alta;
- casamento ativo aceitável;
- padrões embarcados vetoriais distintos;
- correlação ponderada pelo canal reduzida.

### H3 — Ótimo orientado a capacidade

A geometria ótima para maximizar

$$
\mathbb E[
\log_2\det(
\mathbf I+\rho\mathbf H\mathbf H^H/N_t
)]
$$

não coincide, em geral, com a geometria ótima para minimizar $S_{11}$, maximizar ganho de boresight ou minimizar ECC isotrópica.

### H4 — Acoplamento útil

A matriz de acoplamento ótima pode conter termos não desprezíveis. O objetivo não é necessariamente $S_{ij}\rightarrow0$, mas obter autovetores de excitação que produzam estados radiantes úteis, com perdas e mismatch ativo controlados.

### H5 — Densidade modal vantajosa

Uma cavidade compartilhada pode produzir maior número de graus de liberdade úteis por volume ou por cadeia RF do que um conjunto convencional de subarrays fixos, mesmo sacrificando ganho máximo.

## 4. Critérios de falsificação

A forma forte da hipótese será considerada refutada se, após exploração razoável e reprodutível:

- todos os estados co-ressonantes convergirem para padrões praticamente iguais;
- a baixa correlação exigir perdas que eliminem o ganho de capacidade;
- as deformações que alteram o padrão deslocarem a ressonância excessivamente;
- o desempenho desaparecer quando as comparações forem equalizadas;
- tolerâncias realistas destruírem a resposta;
- o benefício existir apenas em um cenário cuidadosamente escolhido;
- a estrutura compartilhada for inferior a subarrays simples em volume, eficiência e capacidade.

## 5. Escopo

Incluído:

- teoria de Maxwell e modos;
- guias próximos ao corte;
- materiais ENZ efetivos;
- cavidades abertas e quasi-normal modes;
- dopagem fotônica;
- antenas ranhuradas;
- sistemas multiporta;
- padrões embarcados;
- teoria MIMO;
- projeto inverso;
- HFSS/PyAEDT/gRPC;
- fabricação e metrologia.

Fora do primeiro ciclo:

- circuito integrado mmWave completo;
- PA/LNA monolíticos;
- beamforming digital em silício;
- protocolo 5G NR integral;
- certificação comercial;
- alegações clínicas, militares ou de segurança.

## 6. Filosofia de pesquisa

A beleza da ideia original está em separar duas funções normalmente ligadas:

- a frequência de ressonância;
- a forma espacial da radiação.

Este projeto tenta separar ainda uma terceira:

- a base de canais espaciais.

O objetivo não é substituir a contribuição dos autores do Inatel, mas entender profundamente o mecanismo, reproduzi-lo, delimitar sua validade e investigar uma extensão nova com atribuição explícita.
