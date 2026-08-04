# poros_aedt — artefatos aprovados

**SIMULADO:** este pacote contem um smoke test M0 de cavidade PEC fechada, executado no AEDT 2024 R2 com 14 cores.

**HIPÓTESE:** a geometria M0 e sintetica e valida a infraestrutura; ela nao reproduz a antena do artigo.

**DESCONHECIDO:** a reproducao fiel permanece bloqueada pelos parametros listados em `especificacoes/g0_artigo_base.auditado.v4.yaml`.

O PDF principal e sua validacao numerica estao em `evidencias/`. O projeto AEDT solucionado, resultados, metricas e logs estao em `runs/`.

## Reconstrução exploratória G0 Figura 2 v7

**DERIVADO:** esta é a versão corrente para inspeção no HFSS. A pasta
`reconstrucoes_exploratorias/G0_figura2_v5/` permanece apenas como histórico
versionado e não deve ser usada para auditar a orientação da waveport.

**HIPÓTESE:** `reconstrucoes_exploratorias/G0_figura2_v7/` contém a versão
auditada com waveport orientada em Z, projeto HFSS configurado, resultados
complexos, oito cortes, oito plots de campo e oito relatórios do artigo.

**SIMULADO:** o run limpo foi concluído no AEDT 2024 R2 com 14 cores e teve
todos os arquivos verificados por tamanho e SHA-256. O gate estrito de
passividade falhou porque a potência radiada excedeu a aceita em 2,16235%; por
isso, este pacote não deve ser apresentado como reprodução validada do artigo.

## Relatório técnico

**DERIVADO:** `relatorios/Relatorio_Tecnico_ENZ_Cavidade_VilasBoas_v3.pdf`
é a cópia corrente do dossiê consolidado; v1 e v2 permanecem preservadas. O
manifesto adjacente valida
estrutura, conteúdo extraível, densidade editorial, DOI, fontes e SHA-256.

**HIPÓTESE:** o gate Q0 MIMO 2×2 permanece em 0/4 radiadores validados. A v8
Q4-C0 foi solucionada como extensão exploratória e não promove a v7 a
componente validado.

**DERIVADO:** `manifest.json` inventaria todos os arquivos publicáveis de
`poros_aedt`. Locks e semáforos de sessão AEDT são explicitamente excluídos.
