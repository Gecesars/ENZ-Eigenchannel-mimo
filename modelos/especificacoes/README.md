# Especificações declarativas de geometria

Toda geometria deve ser reproduzível a partir de YAML versionado. Nenhuma dimensão pode existir apenas dentro de um script AEDT.

Cada parâmetro recebe:

- `valor` e `unidade`;
- `origem`: `publicado`, `derivado`, `inferido`, `otimizado` ou `desconhecido`;
- `fonte`: página, figura, equação ou justificativa;
- `incerteza` quando aplicável;
- intervalo permitido para DOE;
- observações de fabricação.

A especificação preliminar contém apenas os valores confirmados no texto do artigo. Campos `null` são deliberados e bloqueiam uma alegação de reprodução fiel até serem resolvidos por fonte, comunicação com autores ou otimização identificada como tal.
