# ENZ Eigenchannel MIMO

**Síntese de autocanais eletromagnéticos por cavidades ressonantes inspiradas em epsilon-near-zero, codificação geométrica de abertura e arquiteturas multiporta em ondas milimétricas.**

> **Estado atual:** fórmulas e evidências auditadas; worker AEDT 2024 R2 validado; reconstrução exploratória G0 v7 aberta, solucionada e instrumentada com cortes e relatórios. A reprodução fiel permanece bloqueada por cotas/CAD ausentes, divergência de S11 e reprovação do gate estrito de passividade.
>
> **Próximo marco formal:** obter o CAD/coordenadas dos Modelos I–IX e fechar passividade antes de promover qualquer reconstrução a reprodução.
> **Idioma oficial da documentação:** português do Brasil.

> **Renderização matemática:** o GitHub suporta LaTeX em Markdown via MathJax. Este repositório padroniza equações de bloco com cercas `math`; consulte [`docs/GUIA_RENDERIZACAO_MATEMATICA.md`](docs/GUIA_RENDERIZACAO_MATEMATICA.md).

**SIMULADO:** o smoke test sintético M0 concluiu build, validação, convergência,
exportação e encerramento sem processo órfão. Ele valida a infraestrutura, não
reproduz o artigo. O relatório está em
[`docs/32_execucao_prioridades_1_a_5.md`](docs/32_execucao_prioridades_1_a_5.md).

**DERIVADO:** o dossiê consolidado v2, com 106 páginas, teoria, dimensões,
waveport em Z, cortes, campos, relatórios, diagramas de radiação e gates de
validação — incluindo a auditoria Q0 da arquitetura MIMO 2×2 — está em
[`doc/pdfs/Relatorio_Tecnico_ENZ_Cavidade_VilasBoas_v2.pdf`](doc/pdfs/Relatorio_Tecnico_ENZ_Cavidade_VilasBoas_v2.pdf).
Seu manifesto registra 27.781 palavras extraíveis, 19 figuras, 24 tabelas e os
hashes de todas as fontes. **DESCONHECIDO:** Q0 permanece bloqueado porque
nenhum dos quatro radiadores requeridos possui pacote de validação completo.

---

## 1. Tese do projeto

Este repositório investiga uma pergunta situada na fronteira entre eletromagnetismo aplicado, teoria modal, antenas multiporta, materiais de índice próximo de zero, projeto inverso e teoria da informação:

> **Uma cavidade metálica operando em regime ENZ estrutural pode funcionar não apenas como radiador de fase quase uniforme, mas como um sintetizador passivo de estados radiantes e autocanais MIMO?**

A observação física de partida é que um guia retangular operando próximo ao corte do modo dominante apresenta constante de propagação longitudinal pequena,

```math
\beta_z =
\sqrt{k_0^2\varepsilon_r\mu_r-k_c^2}
\longrightarrow 0,
```

e, portanto, comprimento de onda guiado elevado,

```math
\lambda_g=\frac{2\pi}{\beta_z}\longrightarrow\infty.
```

Em uma faixa finita e sob condições modais específicas, o campo acumula pouca fase ao longo da direção de propagação. Essa característica permite que uma região geometricamente extensa se comporte como uma abertura aproximadamente coerente. O trabalho de referência desenvolvido por pesquisadores do Inatel demonstrou que uma cavidade ranhurada pode ser remodelada mantendo a área transversal, convertendo um feixe estreito em um feixe em leque com topo plano, sem deslocamento relevante da frequência ressonante. O resultado foi obtido com cinco ranhuras, carregamento dielétrico em FR4, pinos metálicos para supressão modal e um perfil externo em degrau para redistribuição de amplitude.

A pesquisa deste repositório parte desse resultado, preserva seus créditos e formula uma extensão mais exigente:

```math
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
```

A transformação conceitual é

```math
\mathbf v(f)
\;\xrightarrow{\mathcal T}\;
\mathbf J(\mathbf r,f)
\;\xrightarrow{\mathcal R}\;
\mathbf F(\Omega,f)
\;\xrightarrow{\mathcal P}\;
\mathbf H(f),
```

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

### 2.1 FR4 no modelo de referência

O FR4 será mantido na reprodução porque foi usado pelos autores como inclusão dielétrica de casamento e escolhido por disponibilidade de prototipagem. Contudo, FR4 genérico não será tratado como material precisamente caracterizado em 25,87 GHz. O fabricante, a permissividade complexa, a tangente de perdas e as dimensões completas da inclusão permanecem desconhecidos.

A estratégia é separar:

- **R0:** FR4 como referência obrigatória do artigo;
- **R1:** análise de sensibilidade de $\varepsilon_r$, $\tan\delta$ e dimensões;
- **R2:** reotimização com materiais de micro-ondas controlados;
- **R3:** comparação experimental entre FR4 e alternativa de baixa perda.

A análise completa está em [`docs/01a_validacao_fr4_e_materiais_26ghz.md`](docs/01a_validacao_fr4_e_materiais_26ghz.md).

---

## 3. Questão científica central

A pergunta operacional é:

> Existe uma estrutura ENZ inspirada, compartilhada ou fortemente acoplada, que suporte duas ou mais excitações terminais na mesma banda, cada uma produzindo um padrão embarcado complexo suficientemente distinto para melhorar a distribuição de valores singulares do canal, sem exigir um phase shifter por ranhura?

A primeira experiência decisiva não será uma montagem 4×4 completa. Será:

```math
\boxed{
\text{uma estrutura compartilhada}
+
\text{duas portas}
+
\text{dois estados radiantes úteis}
}
```

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

```math
4\ \text{portas}
=
2\ \text{famílias de padrão}
\times
2\ \text{polarizações}.
```

---

## 6. Métrica de ortogonalidade física

Para padrões embarcados vetoriais,

```math
\mathbf F_m(\Omega,f)=
\begin{bmatrix}
E_{\theta,m}(\Omega,f)\\
E_{\phi,m}(\Omega,f)
\end{bmatrix},
```

a correlação relevante deve considerar o espectro angular e polarimétrico do ambiente:

```math
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
```

A ECC isotrópica continuará sendo calculada, porém não será tratada como prova universal de diversidade.

---

## 7. Métrica sistêmica

A capacidade instantânea para um canal estreito é

```math
C=
\log_2\det
\left[
\mathbf I+
\frac{\rho}{N_t}
\mathbf H\mathbf H^H
\right].
```

Para banda larga e OFDM, a análise será feita por frequência, subportadora ou bloco de coerência. O projeto priorizará:

- mediana e percentil 5% de capacidade;
- outage;
- rank efetivo;
- condição numérica;
- distribuição dos valores singulares;
- custo de treinamento;
- potência aceita;
- eficiência;
- volume e complexidade.

---

## 8. Estrutura documental

```text
.
├── README.md
├── ROADMAP.md
├── CREDITOS.md
├── CITATION.cff
├── AGENTS.md
├── CONTRIBUTING.md
├── LICENSE.md
├── docs/
│   ├── 00_carta_cientifica.md
│   ├── 01_artigo_base_inatel.md
│   ├── 01a_validacao_fr4_e_materiais_26ghz.md
│   ├── 02_fundamentos_maxwellianos.md
│   ├── 03_guia_retangular_e_enz_estrutural.md
│   ├── 04_invariancia_geometrica.md
│   ├── 05_dopagem_fotonica.md
│   ├── 06_ranhuras_e_sintese_de_abertura.md
│   ├── 07_teoria_modal_de_cavidades_abertas.md
│   ├── 08_modelagem_multiporta.md
│   ├── 09_padroes_embarcados_complexos.md
│   ├── 10_teoria_da_informacao_eletromagnetica.md
│   ├── 11_operadores_e_autocanais.md
│   ├── 12_acoplamento_mutuo_e_rede_ativa.md
│   ├── 13_diversidade_e_rank.md
│   ├── 14_limites_fundamentais.md
│   ├── 15_modelos_de_canal_mmwave.md
│   ├── 16_objetivos_orientados_a_capacidade.md
│   ├── 17_projeto_inverso_e_otimizacao.md
│   ├── 18_hipoteses_originais.md
│   ├── 19_arquiteturas_candidatas.md
│   ├── 20_arquitetura_hfss_grpc.md
│   ├── 21_validacao_eletromagnetica.md
│   ├── 22_validacao_experimental.md
│   ├── 23_dados_e_reprodutibilidade.md
│   ├── 24_revisao_bibliografica_e_patentes.md
│   ├── 25_matriz_de_evidencias.md
│   ├── 26_benchmarks.md
│   ├── 27_notacao_e_glossario.md
│   ├── 28_perguntas_abertas.md
│   ├── 29_plano_de_publicacoes.md
│   └── GUIA_RENDERIZACAO_MATEMATICA.md
├── referencias/
├── modelos/
├── scripts/
├── src/
├── testes/
└── artefatos/
```

---

## 9. Próximo marco: EM-VALIDATION-01

**SIMULADO:** o smoke test da infraestrutura foi concluído no AEDT 2024 R2 com
14 cores e publicado em `poros_aedt/`.

**DESCONHECIDO:** a reprodução fiel continua bloqueada pelos parâmetros
materiais e coordenadas CAD não publicados, conforme
`docs/33_validacao_artigo_e_execucao_14_cores.md`.

A primeira etapa executável consiste em:

1. congelar uma especificação auditável do modelo do artigo;
2. reproduzir a cavidade fechada em Eigenmode;
3. reproduzir a antena em Driven Modal;
4. verificar modos $TE_{10}$, $TM_{11}$ e parasitas;
5. extrair $S_{11}$ complexo, impedância, campos internos e campos de abertura;
6. exportar $E_\theta$ e $E_\phi$ complexos;
7. realizar convergência de malha, fronteiras e domínio aberto;
8. comparar quantitativamente com o artigo;
9. executar a campanha FR4 versus materiais controlados;
10. registrar discrepâncias sem ajuste oculto;
11. publicar o pacote de artefatos e o manifesto da execução.

O runtime científico primário será **Ansys AEDT/HFSS 2024 R2**, controlado por **PyAEDT sobre a interface gRPC nativa do AEDT**.

---

## 10. Licenciamento

- documentação original deste repositório: **CC BY 4.0**;
- código-fonte original: **Apache License 2.0**;
- artigos e materiais de terceiros mantêm suas próprias licenças;
- o artigo-base do Inatel é CC BY 4.0 e deve ser citado pelos autores e DOI originais.

Consulte [`LICENSE.md`](LICENSE.md).

---

## 11. Contribuição

Este é um projeto de pesquisa aberto. São especialmente valiosas contribuições em:

- eletromagnetismo computacional;
- teoria de modos e quasi-normal modes;
- antenas ranhuradas;
- ENZ e índice próximo de zero;
- dopagem fotônica;
- caracterização dielétrica em ondas milimétricas;
- sistemas multiporta;
- MIMO e modelos de canal mmWave;
- otimização adjunta;
- metrologia de antenas;
- reprodução independente do artigo-base.

Toda contribuição científica deve incluir hipótese, método, dados, limitações e rastreabilidade.
