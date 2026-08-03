# 01 — Artigo-base do Inatel

## 1. Referência bibliográfica

**Autores:** Evandro C. Vilas Boas, Sofia B. de Vasconcellos, Arismar Cerqueira Sodré Jr. e Felipe Augusto Pereira de Figueiredo.

**Título:** *A Millimeter-Wave Flat-Top Fan-Beam Antenna Array Based on a Geometry-Independent Resonant Cavity*.

**Periódico:** IEEE Open Journal of Antennas and Propagation.

**Ano:** 2026.

**DOI:** `10.1109/OJAP.2026.3703713`.

**Licença:** Creative Commons Attribution 4.0.

O artigo foi recebido em 24 de maio de 2026 e aceito em 10 de junho de 2026. As afiliações incluem o WAI Laboratory e o WOCA Laboratory do Instituto Nacional de Telecomunicações — Inatel, em Santa Rita do Sapucaí, Minas Gerais.

## 2. Contribuição original

O trabalho apresenta uma antena ranhurada alimentada por guia de onda, operando em ondas milimétricas, na qual a cavidade ressonante é remodelada mantendo a área transversal. A transformação permite:

1. partir de uma cavidade com três ranhuras e feixe do tipo pencil beam;
2. alargar geometricamente a cavidade;
3. inserir duas ranhuras adicionais;
4. manter aproximadamente a frequência de ressonância;
5. redistribuir a radiação em um feixe em leque;
6. usar um perfil em degrau para equilibrar as amplitudes das ranhuras;
7. obter um topo plano com ripple reduzido.

A novidade não está em uma ranhura isolada, no FR4 ou no degrau separadamente. Está na combinação de uma cavidade em regime ENZ inspirado, coerência de fase, deformação geometricamente restrita e redistribuição espacial da abertura sem rede externa de amplitude e fase por elemento.

## 3. Dados publicados relevantes

### 3.1 Modelo inicial

- área transversal: $A_c=108\text{ mm}^2$;
- dimensões declaradas: $14\text{ mm}\times7{,}7143\text{ mm}$;
- três ranhuras iguais e igualmente espaçadas;
- frequência de ressonância: aproximadamente $25{,}87$ GHz;
- banda simulada inicial: cerca de 600 MHz;
- guia de entrada WR-28: $a=7{,}11$ mm e $b=3{,}56$ mm;
- corte $TE_{10}$ declarado: $f_c=21{,}08$ GHz.

### 3.2 Transformação para cinco ranhuras

A parede larga é aumentada, a outra dimensão é ajustada para preservar $108\text{ mm}^2$, e duas ranhuras são acrescentadas. O artigo relata preservação aproximada da resposta em frequência e transição para fan beam.

### 3.3 Carregamento e supressão modal

- placa de FR4 para ajuste de impedância;
- pinos metálicos ao redor da placa;
- função dos pinos: reduzir o acoplamento indesejado do modo $TM_{11}$ ou outros modos introduzidos pela cavidade alargada.

### 3.4 Perfil em degrau

O modelo final utiliza:

```math
w_{sp}=9\text{ mm},
\qquad
h_{sp}=1\text{ mm}.
```

Dois chanfros de 3 mm foram introduzidos para reduzir excitação de ondas de superfície e recuperar ripple.

### 3.5 Resultados medidos

- banda $-10$ dB: 1,11 GHz;
- feixe de 1 dB: 60°–70° ao longo da banda;
- ripple menor que 0,71 dB na banda;
- ripple central relatado abaixo de aproximadamente 0,63 dB;
- feixe de 3 dB: superior a 80°;
- ganho realizado máximo: 7,84 dBi;
- SLL: abaixo de −10,02 dB;
- dimensões: $0{,}95\lambda_0\times2{,}33\lambda_0\times3{,}10\lambda_0$;
- eficiência simulada do modelo final: aproximadamente 0,875 a 0,982 na banda.

## 4. Cadeia física proposta pelos autores

A cadeia causal pode ser resumida como:

```math
f\gtrsim f_c
\Rightarrow
\beta_z\ \text{pequeno}
\Rightarrow
\Delta\phi\ \text{pequena}
\Rightarrow
\text{ranhuras coerentes}
\Rightarrow
\text{geometria controla a distribuição espacial}.
```

O FR4 atua na impedância efetiva; os pinos controlam modos parasitas; o degrau altera a impedância espacial local e a amplitude de acoplamento das ranhuras.

## 5. O que o artigo não demonstra

O artigo não apresenta:

- estrutura multiporta;
- matriz $S$ de ordem superior;
- padrões embarcados por porta;
- ECC;
- TARC;
- CCL;
- valores singulares de canal;
- throughput MIMO;
- otimização orientada a capacidade;
- reconfiguração dinâmica;
- prova de invariância para deformações arbitrárias.

Portanto, qualquer extensão MIMO deste repositório é uma nova hipótese e deve ser validada.

## 6. Dimensões desconhecidas

Mesmo com a Figura 2, algumas dimensões podem exigir leitura gráfica, CAD original ou contato com os autores. Toda dimensão deve receber uma origem:

- classificação científica dentre `PUBLICADO`, `DERIVADO`, `SIMULADO`,
  `MEDIDO`, `INFERIDO`, `HIPÓTESE` e `DESCONHECIDO`;
- tipo de fonte dentre `TEXTO`, `FIGURA`, `TABELA`, `EQUAÇÃO`, `DERIVAÇÃO`,
  `SIMULAÇÃO`, `MEDIÇÃO`, `AUDITORIA` e `HIPÓTESE`;
- referência e localização exata na fonte.

Por exemplo, a antiga categoria `PUBLISHED_FIGURE` corresponde agora a
`classificacao: PUBLICADO` e `fonte.tipo: FIGURA`. Essa separação evita criar
classes compostas fora da ontologia obrigatória.

Um modelo que reproduza o gráfico após ajustar dimensões desconhecidas será chamado de **reconstrução otimizada**, não de réplica exata.

## 7. Protocolo de reprodução

1. obter a versão integral do artigo;
2. transcrever todas as cotas;
3. montar uma tabela de rastreabilidade;
4. reproduzir a sequência Model I → Model II → Model III → modelo fabricável;
5. usar materiais com parâmetros declarados;
6. testar PEC e condutividade real separadamente;
7. registrar malha, fronteiras e de-embedding;
8. comparar curvas, não apenas valores isolados;
9. documentar diferenças;
10. solicitar esclarecimento aos autores quando necessário.

## 8. Atribuição

O PDF integral não é reproduzido textualmente neste arquivo. O DOI oficial e as fontes de acesso estão em `referencias/artigo_base/README.md`. Qualquer figura adaptada deverá indicar “adaptado de Vilas Boas et al., 2026, CC BY 4.0”.

## 9. FR4: reprodução versus evolução de engenharia

O artigo declara que o FR4 foi escolhido por disponibilidade para prototipagem. Essa justificativa é importante: o resultado medido comprova que a inclusão funcionou dentro da estrutura completa, mas não transforma FR4 genérico em material preferencial para todas as implementações em 25,87 GHz.

Para preservar integridade científica:

- o primeiro modelo deve manter FR4;
- o fabricante, a composição e as propriedades complexas não podem ser inventados;
- a biblioteca genérica do HFSS não deve ser tratada como dado publicado;
- a influência de $\varepsilon_r$, $\tan\delta$, anisotropia e dispersão deve ser quantificada;
- materiais de baixa perda somente serão comparados após reotimização da inclusão;
- a versão alternativa não será chamada de reprodução do artigo.

A campanha completa está definida em [`01a_validacao_fr4_e_materiais_26ghz.md`](01a_validacao_fr4_e_materiais_26ghz.md).
