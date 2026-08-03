# Especificações declarativas de geometria

Toda geometria deve ser reproduzível a partir de YAML versionado. Nenhuma dimensão pode existir apenas dentro de um script AEDT.

Cada parâmetro recebe:

- `valor` e `unidade`;
- `classificacao`: uma das sete classes científicas obrigatórias;
- `fonte.referencia`, `fonte.localizacao` e `fonte.tipo`;
- `incerteza` quando aplicável;
- intervalo permitido para DOE;
- observações de fabricação.

A especificação preliminar contém apenas os valores confirmados no texto do artigo. Campos `null` são deliberados e bloqueiam uma alegação de reprodução fiel até serem resolvidos por fonte, comunicação com autores ou otimização identificada como tal.

`g0_artigo_base.preliminar.yaml` permanece preservado como schema v2 legado.
Novos modelos usam `enz-eigenchannel-mimo/geometry-spec/v3`, validado pelo
pacote Python. As versões auditadas v3 e v4 permanecem preservadas; a v4
incorpora as cotas inspecionadas na Figura 2(a). O modelo
`m0_cavidade_retangular_smoke.hipotese.v1.yaml` valida apenas infraestrutura e
não pode ser apresentado como reprodução.

`g0_figura2_reconstrucao_exploratoria.hipotese.v5.yaml` materializa no HFSS a
topologia das Figuras 1 e 2 com WR-28, cinco ranhuras, perfil escalonado,
chanfros, FR4, quatro pinos e uma porta. Valores não cotados são explicitamente
`HIPÓTESE` ou `INFERIDO`; a versão não substitui a auditoria v4 e não constitui
reprodução fiel do artigo.

`g0_figura2_reconstrucao_exploratoria.hipotese.v6.yaml` corrige a seção da
waveport para 3,56 mm em X por 7,11 mm em Z e declara uma linha de integração
modal explícita em Z. Também declara cortes, plots e relatórios auditáveis.

`g0_figura2_reconstrucao_exploratoria.hipotese.v7.yaml` preserva a v6 e
acrescenta `Sweep_Fields_Article`, com pontos discretos em 25,65 GHz,
25,87 GHz e 26,22 GHz. Essa sweep salva campos e campos radiados para os
diagramas co- e cross-polarizados da Figura 4.
