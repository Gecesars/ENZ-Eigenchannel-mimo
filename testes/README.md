# Testes

A suíte começa por propriedades matemáticas independentes do AEDT. Testes licenciados do HFSS serão adicionados em `testes/integracao_aedt/` e marcados para não executar em CI sem licença.

Gates mínimos:

- métricas analíticas verificadas;
- schemas e YAML validados;
- nenhum resultado não finito aceito;
- smoke test AEDT 2024 R2 em estação licenciada;
- regressão contra artefatos golden somente após EM-VALIDATION-01.
