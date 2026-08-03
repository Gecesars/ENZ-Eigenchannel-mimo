# 31 — Auditoria dimensional do artigo-base

## 1. Identidade e método

**PUBLICADO:** artigo de Vilas Boas et al., DOI
`10.1109/OJAP.2026.3703713`, documento IEEE `11563493`, licença CC BY 4.0
informada pela fonte.

**DERIVADO:** a auditoria de 3 de agosto de 2026 comparou o texto integral
disponibilizado pelo autor, a descrição da Figura 2 e a especificação v2. Não
foram medidas distâncias em pixels nem inferidas cotas por escala visual.

## 2. Parâmetros confirmados no texto

| Parâmetro | Valor | Classe | Localização |
|---|---:|---|---|
| frequência central | 25,87 GHz | PUBLICADO | Seção III |
| área transversal inicial/final | 108 mm² | PUBLICADO | Seção III |
| dimensões iniciais associadas à área | 14 mm × 7,7143 mm | PUBLICADO | Seção III |
| WR-28 | 7,11 mm × 3,56 mm | PUBLICADO | Seção III |
| corte TE10 | 21,08 GHz | PUBLICADO | Seção III |
| quantidade inicial/final de ranhuras | 3/5 | PUBLICADO | Seções II–III |
| degrau final | 9 mm × 1 mm | PUBLICADO | Seção III/Tabela 2 |
| chanfros | dois de 3 mm | PUBLICADO | Seção III |
| gaps do modelo com tolerâncias | 0,05 mm | PUBLICADO | Seção IV |
| comprimento medido das ranhuras | 5,66–5,68 mm | MEDIDO | Seção IV |
| largura medida das ranhuras | 0,93–0,94 mm | MEDIDO | Seção IV |

Os intervalos medidos das ranhuras descrevem o protótipo e o modelo numérico
com tolerâncias. Eles não foram convertidos em cotas nominais.

## 3. Parâmetros não resolvidos

| Grupo | Classe | Consequência |
|---|---|---|
| comprimento e orientação completa da cavidade | DESCONHECIDO | bloqueia M0 fiel |
| largura/altura finais e espessuras de parede | DESCONHECIDO | bloqueia M2–M4 |
| cota nominal e posições das ranhuras | DESCONHECIDO | bloqueia M1–M4 |
| comprimento da seção WR-28 e plano de referência | DESCONHECIDO | bloqueia porta auditável |
| dimensões/propriedades do FR4 | DESCONHECIDO | bloqueia matching reproduzível |
| quantidade, diâmetro e posições dos pinos | DESCONHECIDO | bloqueia supressão modal fiel |
| parafusos, folgas internas e detalhes do split-block | DESCONHECIDO | bloqueia M4 fabricável |

## 4. Resultado

**DERIVADO:** a auditoria está registrada integralmente em
`modelos/especificacoes/g0_artigo_base.auditado.v3.yaml`. O modelo continua
documentalmente bloqueado; preencher uma cota desconhecida por otimização
produzirá uma nova versão classificada, nunca alteração silenciosa desta.

**DESCONHECIDO:** as cotas presentes somente na Figura 2(a) aguardam obtenção
visual confiável do PDF oficial, CAD dos autores ou comunicação direta.

## 5. Atualização após obtenção do PDF

**DERIVADO:** esta seção preserva o resultado histórico da v3 acima e registra
a evolução sem substituí-la. O PDF foi obtido e a Figura 2(a) foi inspecionada
visualmente. As cotas legíveis foram transcritas na especificação
`g0_artigo_base.auditado.v4.yaml`.

**PUBLICADO:** passaram a ser conhecidas, entre outras, as dimensões nominais
das ranhuras (5,66 mm × 0,8 mm), parede de 1 mm, slab de FR4 de
3 mm × 1,65 mm, quatro pinos de 1 mm, dimensões externas de
11 mm × 27 mm × 36 mm e largura local de 11,11 mm.

**DESCONHECIDO:** a v4 continua bloqueada por ausência das propriedades
complexas do FR4, propriedades do condutor, coordenadas CAD dos elementos,
comprimento interno e plano de porta. A Figura 2 não substitui o CAD nem os
arquivos complexos do solver.

O resultado atualizado e a execução de infraestrutura com 14 cores estão em
`docs/33_validacao_artigo_e_execucao_14_cores.md`.
