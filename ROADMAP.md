# Roadmap científico

## Princípio

O projeto progride por **gates verificáveis**, não por aparência visual de resultados. Nenhuma fase posterior deve ocultar falhas da anterior.

## Fase 0 — Fundação documental

**Estado:** iniciada.

Entregas:

- corpus teórico em português;
- mapa de literatura;
- definição de hipóteses e falsificação;
- contrato de dados;
- matriz de evidências;
- créditos e licenças;
- especificação preliminar do runtime AEDT/HFSS.

Gate:

- todas as afirmações classificadas como publicadas, derivadas, simuladas, medidas, inferidas ou hipóteses.

## Fase 1 — EM-VALIDATION-01: reprodução do artigo-base

Objetivo: reproduzir de forma independente o modelo de uma porta publicado pelo Inatel.

Subetapas:

1. auditoria dimensional da Figura 2 e do texto;
2. modelo M0: cavidade fechada, Eigenmode;
3. modelo M1: três ranhuras;
4. modelo M2: cinco ranhuras sem degrau;
5. modelo M3: perfil em degrau;
6. modelo M4: versão fabricável com paredes, chanfros, pinos e FR4;
7. análise de convergência;
8. comparação com banda, ganho, ripple e larguras de feixe publicadas.

Critério de saída:

- relatório de reprodução com todas as diferenças explicadas;
- projeto AEDT versionado;
- especificação geométrica declarativa;
- campos complexos e Touchstone exportados;
- ausência de parâmetros ocultos.

## Fase 2 — Manifold de invariância

Objetivo: mapear quais deformações preservam a ressonância e a coerência de fase.

Métodos:

- DOE com restrição de área;
- sensitividade por diferenças finitas;
- shape derivatives;
- análise de Hessiana local;
- modelos substitutos;
- Monte Carlo de tolerâncias.

Entregas:

- mapa $f_r(\mathbf g)$;
- mapa de variância de fase;
- mapa de amplitude nas ranhuras;
- identificação de direções quase nulas da frequência;
- limites de validade da expressão “geometry-independent”.

## Fase 3 — Experiência crítica de duas portas

Objetivo: provar ou refutar que uma estrutura ENZ inspirada compartilhada pode produzir dois estados radiantes úteis.

Casos:

- portas opostas;
- portas ortogonais;
- excitação par e ímpar;
- grupos de ranhuras intercalados;
- duas subcavidades acopladas;
- dopantes seletivos;
- polarizações ortogonais.

Gate mínimo:

- $|S_{ii}|<-10$ dB em faixa comum;
- eficiência de radiação superior a 70%;
- ECC ponderada pelo canal inferior a 0,3 em cenários-alvo;
- melhoria de rank efetivo em relação a duas cópias coorientadas;
- estabilidade sob tolerâncias.

## Fase 4 — Arquitetura de quatro portas

Alvo inicial:

$$
2\ \text{padrões}
\times
2\ \text{polarizações}.
$$

Entregas:

- matriz $S_{4\times4}$;
- padrões embarcados complexos por porta;
- TARC;
- matriz de correlação;
- CCL, MEG e eficiência;
- valores singulares por cenário;
- adaptação de rank 1–4.

## Fase 5 — Comparação de arquiteturas

Referências:

1. quatro cavidades ENZ independentes;
2. quatro subarrays convencionais fixos;
3. phased array híbrido;
4. estrutura ENZ compartilhada.

Condições equalizadas:

- abertura;
- banda;
- potência aceita;
- EIRP;
- cadeias RF;
- canal;
- receptor;
- perdas de alimentação.

## Fase 6 — Prototipagem e metrologia

- protótipos repetidos;
- VNA com extensores mmWave;
- medição de padrões embarcados;
- calibração de cabos e phase centers;
- matriz de canal coerente;
- incerteza expandida;
- comparação simulação–medição.

## Fase 7 — Publicações

Possíveis artigos:

1. reprodução e limites da invariância geométrica;
2. cavidade ENZ dual-port com diversidade codificada;
3. otimização orientada a capacidade;
4. sistema 4×4 e comparação de throughput;
5. versão reconfigurável;
6. formulação teórica por operadores e autocanais.

## Critério de honestidade

Um resultado negativo é publicável se delimitar com precisão:

- onde a invariância deixa de existir;
- por que os estados colapsam;
- qual perda ou acoplamento impede rank útil;
- quais condições de canal anulam o benefício.
