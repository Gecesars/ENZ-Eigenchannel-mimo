# 01A — Validação do FR4 e seleção de materiais em 25,87 GHz

## 1. Conclusão executiva

O FR4 deve ser **mantido no modelo de reprodução do artigo**, porque faz parte da estrutura publicada e foi empregado como inclusão dielétrica para casamento de impedância. Substituí-lo antes da reprodução impediria uma comparação limpa com o trabalho de Vilas Boas, Vasconcellos, Sodré Jr. e Figueiredo.

Entretanto, FR4 genérico não deve ser tratado como material eletromagnético precisamente conhecido em 25,87 GHz. O artigo informa que o material foi escolhido por disponibilidade para prototipagem, mas não fornece, no texto disponível, um fabricante, código de laminado, lote, método de caracterização, permissividade complexa ou tangente de perdas na frequência de operação.

A decisão científica é, portanto:

1. **R0 — reprodução:** manter FR4 e declarar suas propriedades como desconhecidas até obter dados dos autores, do fornecedor ou de caracterização;
2. **R1 — análise de incerteza:** varrer permissividade, perdas e dimensões da inclusão sem atribuir esses pontos a um produto específico;
3. **R2 — materiais controlados:** reconstruir e reotimizar a inclusão com materiais de micro-ondas caracterizados;
4. **R3 — comparação experimental:** fabricar pelo menos a versão FR4 e uma versão de baixa perda, medindo ambas.

## 2. Função física do dielétrico no artigo

O dielétrico não é apresentado como substrato convencional de microfita nem como preenchimento integral da cavidade. Ele atua como uma **perturbação dielétrica localizada**, associada ao conceito de *photonic doping*, para melhorar o casamento entre a cavidade ENZ inspirada, as ranhuras e o espaço livre.

A sequência física de trabalho é:

```math
f\gtrsim f_c
\Rightarrow
\beta_z\rightarrow 0
\Rightarrow
\text{fase longitudinal quase uniforme}
\Rightarrow
\text{impedância intrínseca desfavorável}
\Rightarrow
\text{inclusão dielétrica para casamento}.
```

No modelo perturbativo, a alteração de frequência provocada por uma mudança de material pode ser aproximada por:

```math
\frac{\Delta\omega}{\omega_0}
\approx
-\frac{1}{2}
\frac{
\displaystyle\int_{V_d}
\Delta\varepsilon\,|\mathbf E_0|^2\,dV
}{
\displaystyle\int_V
\left(
\varepsilon|\mathbf E_0|^2+
\mu|\mathbf H_0|^2
\right)dV
}.
```

Logo, trocar FR4 por um material de menor permissividade ou menor perda **não é uma substituição direta**. A geometria e a posição da inclusão devem ser reotimizadas para recuperar a condição modal e o casamento.

## 3. Por que FR4 é tecnicamente arriscado em 26 GHz

“FR4” descreve uma classe de laminados epóxi reforçados com fibra de vidro, não uma composição eletromagnética única. Em ondas milimétricas, diferenças de resina, trama de vidro, teor de resina, umidade, orientação e lote podem alterar:

- permissividade efetiva;
- anisotropia;
- tangente de perdas;
- frequência ressonante;
- fator de qualidade;
- acoplamento entre modos;
- amplitude e fase nas ranhuras;
- ganho realizado e aquecimento.

A perda dielétrica média é proporcional a:

```math
P_d
=
\frac{\omega}{2}
\int_{V_d}
\varepsilon'\tan\delta\,
|\mathbf E|^2\,dV.
```

Assim, o impacto do FR4 não depende apenas de sua tangente de perdas. Depende do **fator de preenchimento elétrico**, isto é, de quanto da energia elétrica modal está concentrada no volume dielétrico:

```math
\eta_{E,d}
=
\frac{
\displaystyle\int_{V_d}\varepsilon'|\mathbf E|^2dV
}{
\displaystyle\int_V\varepsilon'|\mathbf E|^2dV
}.
```

Uma inclusão pequena pode produzir o casamento desejado com penalidade aceitável mesmo usando um material relativamente dissipativo. Isso é plausível e coerente com a escolha de prototipagem do artigo. Porém, essa hipótese deve ser quantificada por balanço de potência no HFSS.

## 4. O que o artigo efetivamente estabelece

**PUBLICADO:**

- a cavidade é carregada com uma placa ou inclusão de FR4;
- a função declarada é melhorar o casamento;
- a escolha de FR4 é associada à disponibilidade para prototipagem;
- pinos metálicos são usados para reduzir o acoplamento modal indesejado;
- o protótipo medido demonstra que a solução completa funciona.

**NÃO PUBLICADO OU AINDA NÃO RECUPERADO:**

- fabricante e código do FR4;
- permissividade em 25,87 GHz;
- tangente de perdas em 25,87 GHz;
- anisotropia;
- dispersão;
- espessura e todas as dimensões da inclusão;
- método de caracterização do material.

Consequentemente, o primeiro modelo será denominado **reconstrução auditável**, e não réplica exata, enquanto esses dados permanecerem ausentes.

## 5. Materiais candidatos

Os valores abaixo são dados típicos publicados pelos fabricantes em 10 GHz. Eles servem para seleção inicial, mas **não substituem dados em 25,87 GHz nem medição do lote real**.

| Material | Dk típica publicada | Df típica publicada | Papel recomendado |
|---|---:|---:|---|
| FR4 do artigo | desconhecida | desconhecida | referência obrigatória R0 |
| Rogers TMM 4 | 4,50 de processo; 4,70 de projeto | 0,0020 | alternativa próxima em permissividade, reduzindo a mudança geométrica inicial |
| Rogers RO4350B | 3,48 de processo; 3,66 de projeto | 0,0037 | compromisso de fabricação, custo e perda |
| Rogers RO3003 | 3,00 ± 0,04 | 0,0010 | baixa perda e boa estabilidade para mmWave; exige reotimização maior |
| Rogers RT/duroid 5880 | 2,20 ± 0,02 | 0,0009 | referência de perda muito baixa; mudança modal e mecânica significativa |

### 5.1 Candidato preferencial para a primeira substituição

O **TMM 4** é o primeiro candidato de engenharia porque sua permissividade nominal está mais próxima da faixa comumente associada a FR4, enquanto a perda publicada é muito menor. Isso tende a reduzir a amplitude da reotimização geométrica em comparação com materiais de Dk próxima de 2 a 3.

Essa preferência é **HIPÓTESE DE PROJETO**, não conclusão. A decisão final depende de:

- disponibilidade de espessura compatível;
- usinabilidade da inclusão;
- tolerância dimensional;
- propriedades em 26 GHz;
- reconstrução do campo dentro da cavidade;
- resultado do DOE eletromagnético.

### 5.2 Candidato preferencial para eficiência máxima

RO3003 ou RT/duroid 5880 podem fornecer perdas menores, mas a redução de permissividade altera fortemente a polarizabilidade da inclusão. A geometria deve ser redimensionada e poderá deixar de caber na região disponível ou excitar outro comportamento modal.

## 6. Modelos de material no HFSS

Cada material deve ser definido explicitamente; não se deve depender silenciosamente do nome genérico da biblioteca AEDT.

O manifesto deve registrar:

```yaml
material:
  fabricante: null
  produto: null
  lote: null
  epsilon_r_complexa:
    modelo: constant|debye|multipole_debye|measured_table
    epsilon_prime: null
    tan_delta: null
    frequencia_referencia_ghz: null
  anisotropia: isotropico|uniaxial|biaxial|desconhecida
  densidade: null
  fonte: null
  classificacao: PUBLICADO|MEDIDO|INFERIDO|DESCONHECIDO
```

Quando houver tabela medida, o modelo deve preservar dispersão. Um único par `epsilon_r/tan_delta` só será aceito como aproximação de banda estreita e deverá ser identificado no manifesto.

## 7. Campanha numérica obrigatória

### 7.1 Etapa M0 — material sem perdas

- PEC nas paredes;
- inclusão com `tan_delta = 0`;
- objetivo: separar o efeito reativo da inclusão do efeito dissipativo;
- extrair frequência, modos, energia elétrica na inclusão e campos nas ranhuras.

### 7.2 Etapa M1 — FR4 parametrizado

Como os parâmetros são desconhecidos, executar DOE exploratório, sem atribuir os pontos a um FR4 comercial:

```text
Dk:       3,6; 3,9; 4,2; 4,5; 4,8
Tanδ:     0,002; 0,005; 0,010; 0,020; 0,030
Escala da inclusão: 0,85; 0,925; 1,00; 1,075; 1,15
```

Esses valores são **pontos numéricos de sensibilidade**, não especificações de produto.

### 7.3 Etapa M2 — candidatos comerciais

Para cada material:

1. importar propriedades do datasheet;
2. reotimizar as dimensões da inclusão;
3. manter a geometria metálica inicialmente congelada;
4. recuperar `S11`, banda e fase de abertura;
5. liberar posição e dimensões apenas depois;
6. calcular perdas dielétrica, condutora e radiada separadamente.

### 7.4 Etapa M3 — robustez

Aplicar Monte Carlo ou amostragem Latin Hypercube sobre:

- Dk;
- Df;
- dimensões da inclusão;
- posição da inclusão;
- diâmetro e posição dos pinos;
- rugosidade e condutividade;
- folgas de montagem.

## 8. Métricas de comparação

A decisão de material não pode ser baseada somente em `S11`. Devem ser comparados:

- frequência de ressonância;
- banda de −10 dB;
- eficiência de radiação;
- eficiência total;
- ganho realizado;
- potência dissipada no dielétrico;
- fator de qualidade;
- separação entre modos;
- desvio de fase entre ranhuras;
- desbalanceamento de amplitude;
- largura de 1 dB e de 3 dB;
- ripple do flat-top;
- SLL;
- sensibilidade a tolerâncias.

Uma função de mérito inicial pode ser:

```math
J_m
=
w_1\,\overline{|S_{11}|}_{\mathcal B}
+w_2\,\sigma_{\phi,\mathrm{slots}}
+w_3\,\sigma_{A,\mathrm{slots}}
+w_4\,(1-\eta_{\mathrm{rad}})
+w_5\,R_{\mathrm{ripple}}
+w_6\,P_{d,\mathrm{norm}}.
```

Os pesos deverão ser declarados e submetidos a análise de sensibilidade.

## 9. Critério de decisão

O FR4 será mantido na versão de referência independentemente de ser o material de melhor eficiência, porque o objetivo de R0 é reproduzir o artigo.

Para a versão de engenharia, um material alternativo somente substitui o FR4 quando:

1. recuperar a banda e o padrão da referência;
2. aumentar eficiência ou robustez de modo estatisticamente significativo;
3. não introduzir modo parasita crítico;
4. possuir dados rastreáveis em frequência compatível;
5. ser mecanicamente fabricável;
6. ter custo e disponibilidade coerentes com a aplicação;
7. passar por medição do protótipo.

## 10. Referências primárias para propriedades

- Vilas Boas, E. C. et al., “A Millimeter-Wave Flat-Top Fan-Beam Antenna Array Based on a Geometry-Independent Resonant Cavity,” IEEE OJAP, 2026, DOI `10.1109/OJAP.2026.3703713`.
- Rogers Corporation, *High Frequency Electronics Product Selector Guide*.
- Rogers Corporation, ficha técnica RO3003.
- Rogers Corporation, ficha técnica RO4350B.
- Rogers Corporation, ficha técnica RT/duroid 5880.

A revisão deve registrar a data de acesso e arquivar localmente as fichas permitidas pela licença. Dados em 10 GHz não serão extrapolados silenciosamente para 25,87 GHz.
