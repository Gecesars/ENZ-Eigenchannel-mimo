# ENZ Eigenchannel MIMO

**Síntese de autocanais eletromagnéticos por cavidades ressonantes inspiradas em epsilon-near-zero, codificação geométrica de abertura e arquiteturas multiporta em ondas milimétricas.**

> **Estado atual:** fundação teórica, arquitetura científica e preparação da validação eletromagnética.  
> **Próximo marco formal:** reprodução independente do modelo de referência do Inatel no Ansys AEDT/HFSS 2024 R2, seguida de uma experiência crítica de duas portas.  
> **Idioma oficial da documentação:** português do Brasil.

---

## 1. Tese do projeto

Este repositório investiga uma pergunta situada na fronteira entre eletromagnetismo aplicado, teoria modal, antenas multiporta, materiais de índice próximo de zero, projeto inverso e teoria da informação:

> **Uma cavidade metálica operando em regime ENZ estrutural pode funcionar não apenas como radiador de fase quase uniforme, mas como um sintetizador passivo de estados radiantes e autocanais MIMO?**

A observação física de partida é que um guia retangular operando próximo ao corte do modo dominante apresenta constante de propagação longitudinal pequena,

$$
\beta_z =
\sqrt{k_0^2\varepsilon_r\mu_r-k_c^2}
\longrightarrow 0,
$$

e, portanto, comprimento de onda guiado elevado,

$$
\lambda_g=\frac{2\pi}{\beta_z}\longrightarrow\infty.
$$

Em uma faixa finita e sob condições modais específicas, o campo acumula pouca fase ao longo da direção de propagação. Essa característica permite que uma região geometricamente extensa se comporte como uma abertura aproximadamente coerente. O trabalho de referência desenvolvido por pesquisadores do Inatel demonstrou que uma cavidade ranhurada pode ser remodelada mantendo a área transversal, convertendo um feixe estreito em um feixe em leque com topo plano, sem deslocamento relevante da frequência ressonante. O resultado foi obtido com cinco ranhuras, carregamento dielétrico em FR4, pinos metálicos para supressão modal e um perfil externo em degrau para redistribuição de amplitude.

A pesquisa deste repositório parte desse resultado, preserva seus créditos e formula uma extensão mais exigente:

$$
\boxed{
\text{fase coerente interna}
+
\text{geometria}
+
\text{portas}
+
\text{polarização}
+
\text{perturbações}
\longrightarrow
\text{base de estados radiantes úteis}
}
$$

A transformação conceitual é

$$
\mathbf v(f)
\;\xrightarrow{\mathcal T}\;
\mathbf J(\mathbf r,f)
\;\xrightarrow{\mathcal R}\;
\mathbf F(\Omega,f)
\;\xrightarrow{\mathcal P}\;
\mathbf H(f),
$$

onde:

- $\mathbf v$ contém as excitações complexas dos terminais;
- $\mathbf J$ representa as correntes induzidas na estrutura;
- $\mathbf F$ reúne os padrões embarcados complexos;
- $\mathbf H$ é a matriz de canal efetiva, incluindo propagação e polarização.

O projeto não assume que ENZ produz automaticamente multiplexação espacial. Quatro portas podem continuar equivalendo a rank um se os padrões embarcados forem semelhantes ou se o canal não fornecer graus de liberdade. A hipótese é mais precisa: **o regime de baixa progressão de fase pode criar um manifold de projeto no qual alterações geométricas, modais e de excitação sejam usadas para gerar estados radiantes de baixa correlação sob um conjunto declarado de ambientes**.

---

## 2. Artigo científico de referência

A fundação experimental principal é:

> E. C. Vilas Boas, S. B. de Vasconcellos, A. C. Sodré Jr. e F. A. P. de Figueiredo,  
> **“A Millimeter-Wave Flat-Top Fan-Beam Antenna Array Based on a Geometry-Independent Resonant Cavity,”**  
> *IEEE Open Journal of Antennas and Propagation*, 2026.  
> DOI: `10.1109/OJAP.2026.3703713`.

O artigo é publicado sob licença **Creative Commons Attribution 4.0**. Todos os resultados, conceitos, autores, laboratórios e instituições de fomento oriundos desse trabalho são creditados em [`CREDITOS.md`](CREDITOS.md) e em [`docs/01_artigo_base_inatel.md`](docs/01_artigo_base_inatel.md).

Resultados publicados que orientam a reprodução:

- frequência central de projeto em torno de **25,87 GHz**;
- cavidade inicial com área transversal de **108 mm²**, formada por $14\text{ mm}\times7{,}7143\text{ mm}$;
- alimentação por seção **WR-28**, aproximadamente $7{,}11\text{ mm}\times3{,}56\text{ mm}$;
- corte do modo $TE_{10}$ informado em **21,08 GHz**;
- transição de três para cinco ranhuras mantendo a área transversal;
- degrau final com $w_{sp}=9\text{ mm}$ e $h_{sp}=1\text{ mm}$;
- dois chanfros de **3 mm** no modelo de fabricação;
- banda medida de $-10$ dB de **1,11 GHz**;
- largura de feixe de 1 dB entre aproximadamente **60° e 70°**, com ripple inferior a **0,71 dB** ao longo da banda;
- largura de 3 dB superior a **80°**;
- ganho realizado máximo medido de **7,84 dBi**;
- níveis de lóbulos laterais inferiores a **−10,02 dB**;
- dimensões globais informadas de $0{,}95\lambda_0\times2{,}33\lambda_0\times3{,}10\lambda_0$.

Esses valores são metas de reprodução, não parâmetros a serem forçados por ajuste oculto. Dimensões não publicadas serão classificadas como **desconhecidas**, **inferidas** ou **otimizadas**, nunca apresentadas como se tivessem sido fornecidas pelos autores.

---

## 3. Questão científica central

A pergunta operacional é:

> Existe uma estrutura ENZ inspirada, compartilhada ou fortemente acoplada, que suporte duas ou mais excitações terminais na mesma banda, cada uma produzindo um padrão embarcado complexo suficientemente distinto para melhorar a distribuição de valores singulares do canal, sem exigir um phase shifter por ranhura?

A primeira experiência decisiva não será uma montagem 4×4 completa. Será:

$$
\boxed{
\text{uma estrutura compartilhada}
+
\text{duas portas}
+
\text{dois estados radiantes úteis}
}
$$

O sucesso mínimo exige simultaneamente:

1. ressonâncias próximas ou sobrepostas;
2. casamento ativo aceitável;
3. eficiência de radiação adequada;
4. controle das perdas e do acoplamento;
5. padrões embarcados complexos distintos;
6. baixa correlação ponderada pelo canal;
7. melhoria mensurável de rank efetivo ou capacidade em cenários declarados.

---

## 4. Princípios de integridade científica

Todo resultado será classificado como:

- **PUBLICADO** — valor ou afirmação diretamente suportado por fonte citada;
- **DERIVADO** — consequência matemática de hipóteses declaradas;
- **SIMULADO** — resultado de modelo numericamente resolvido e versionado;
- **MEDIDO** — resultado de medição calibrada;
- **INFERIDO** — interpretação plausível, mas não observação direta;
- **HIPÓTESE** — proposição ainda não validada;
- **DESCONHECIDO** — informação insuficiente.

É proibido:

- inventar dimensões ausentes;
- ajustar silenciosamente a geometria até reproduzir um gráfico;
- usar somente $S_{21}$ para afirmar diversidade;
- chamar qualquer conjunto de portas de “MIMO” sem análise de canal;
- comparar arquiteturas com abertura, potência ou número de cadeias RF diferentes;
- apresentar capacidade de Shannon como throughput medido;
- selecionar apenas os cenários favoráveis;
- ocultar falhas de convergência, perdas, modos parasitas ou sensibilidade de fabricação.

---

## 5. Arquiteturas candidatas

| Geração | Arquitetura | Objetivo científico |
|---|---|---|
| G0 | cavidade única, uma porta | reprodução do artigo e controle de incerteza |
| G1 | duas cavidades independentes | validar extração multiporta e simulador de canal |
| G2 | cavidade dual-port ou duas cavidades acopladas | prova crítica de diversidade codificada |
| G3 | quatro super-elementos independentes | benchmark de baixo risco |
| G4 | duas cavidades dual-polarizadas | reduzir volume e número de peças |
| G5 | cavidade única de quatro portas | sintetizador de autocanais compartilhado |
| G6 | dopantes ou perturbações reconfiguráveis | adaptação ao canal em tempo real |

O alvo inicial de quatro portas, somente após G2, é:

$$
4\ \text{portas}
=
2\ \text{famílias de padrão}
\times
2\ \text{polarizações}.
$$

---

## 6. Métrica de ortogonalidade física

Para padrões embarcados vetoriais,

$$
\mathbf F_m(\Omega,f)=
\begin{bmatrix}
E_{\theta,m}(\Omega,f)\\
E_{\phi,m}(\Omega,f)
\end{bmatrix},
$$

a correlação relevante deve considerar o espectro angular e polarimétrico do ambiente:

$$
\rho_{ij}^{(P)}
=
\frac{
\left|
\int_{4\pi}
P(\Omega)
\mathbf F_i(\Omega)\cdot\mathbf F_j^*(\Omega)
\,d\Omega
\right|^2
}{
\left[
\int_{4\pi}P(\Omega)\|\mathbf F_i\|^2\,d\Omega
\right]
\left[
\int_{4\pi}P(\Omega)\|\mathbf F_j\|^2\,d\Omega
\right]
}.
$$

A ECC isotrópica continuará sendo calculada, porém não será tratada como prova universal de diversidade.

---

## 7. Métrica sistêmica

A capacidade instantânea para um canal estreito é

$$
C=
\log_2\det
\left[
\mathbf I+
\frac{\rho}{N_t}
\mathbf H\mathbf H^H
\right].
$$

Para banda larga e OFDM, a análise será feita por frequência, subportadora ou bloco de coerência. O projeto priorizará:

- mediana e percentil 5% de capacidade;
- outage;
- rank efetivo;
- estabilidade sob bloqueio e movimento;
- treinamento necessário;
- eficiência energética;
- densidade de graus de liberdade por volume.

A capacidade depende da matriz de canal. A antena não “gera throughput” isoladamente; ela modifica acoplamento, eficiência, padrões, polarização, SNR, correlação e overhead.

---

## 8. Estrutura documental

O índice integral está em [`docs/INDEX.md`](docs/INDEX.md). O corpus inclui fundamentos maxwellianos, guia de onda e ENZ estrutural, invariância geométrica, dopagem fotônica, síntese de abertura, teoria modal, multiportas, padrões embarcados, teoria da informação eletromagnética, operadores e autocanais, limites físicos, modelos de canal, otimização inversa, hipóteses originais, arquitetura HFSS/gRPC, validação numérica e experimental, revisão patentária e plano de publicações.

---

## 9. Próximos passos formais

O roadmap completo está em [`ROADMAP.md`](ROADMAP.md). Os três primeiros gates são:

1. **EM-VALIDATION-01** — reproduzir independentemente o modelo de uma porta do artigo-base;
2. **INVARIANCE-MANIFOLD-01** — mapear deformações que preservam ressonância e coerência de fase;
3. **DUALPORT-CRITICAL-01** — provar ou refutar dois estados radiantes úteis em uma estrutura compartilhada.

Nenhuma alegação de novidade multiporta será promovida antes da conclusão do primeiro gate.

---

## 10. Licenciamento

- documentação original: **CC BY 4.0**;
- código original: **Apache License 2.0**;
- conteúdo de terceiros: permanece sob a licença da fonte.

Consulte [`LICENSE.md`](LICENSE.md), [`CREDITOS.md`](CREDITOS.md) e [`CONTRIBUTING.md`](CONTRIBUTING.md).
