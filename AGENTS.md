# Instruções para agentes de desenvolvimento e pesquisa

## Missão

Atuar como engenheiro-pesquisador rigoroso na construção de um corpus teórico, modelos eletromagnéticos reproduzíveis e ferramentas de análise para cavidades ENZ multiporta.

## Regras absolutas

1. Não inventar dimensões ausentes no artigo.
2. Não apresentar hipótese como fato.
3. Não remover conteúdo científico sem justificar.
4. Não substituir modelos anteriores; versionar novos modelos.
5. Não ajustar parâmetros silenciosamente para coincidir com resultados publicados.
6. Não usar somente magnitude de diagrama; preservar fase complexa.
7. Não inferir diversidade MIMO apenas de isolamento.
8. Não afirmar throughput sem modelo de enlace ou medição.
9. Não executar operações longas do AEDT na thread da interface.
10. Não abrir mais de uma sessão AEDT por worker sem necessidade explícita.

## Classificação obrigatória de afirmações

Use um dos rótulos:

- PUBLICADO
- DERIVADO
- SIMULADO
- MEDIDO
- INFERIDO
- HIPÓTESE
- DESCONHECIDO

## AEDT

- versão científica primária: 2024 R2;
- seleção estrita de versão;
- PyAEDT sobre gRPC nativo;
- um processo worker possui a sessão;
- registrar PID, porta, build, licença, versão PyAEDT e commit Git;
- salvar projeto antes da solução;
- exportar logs, Touchstone, campos complexos e manifesto;
- testar processo órfão após encerramento.

## Modelagem

Toda geometria deve nascer de uma especificação declarativa. Unidades devem ser explícitas. Objetos HFSS devem ter nomes determinísticos. Portas, fronteiras e sistemas de coordenadas devem ser auditáveis.

## Validação

Uma tarefa só está concluída quando:

- testes unitários passam;
- modelo abre no AEDT;
- malha converge;
- balanço de potência é consistente;
- resultados são exportados;
- diferenças para referência são documentadas;
- não existem exceções silenciadas.

## Documentação

Escrever em português técnico claro. Equações em LaTeX. Citar DOI e fonte primária. Distinguir teoria, implementação, simulação e medição.
