# Guia de renderização matemática

## 1. Decisão técnica

Arquivos Markdown do GitHub **suportam matemática em sintaxe LaTeX** por meio do MathJax. O problema observado não exige abandonar o formato `.md`; exige padronizar os delimitadores e validar o corpus.

A política deste repositório é:

- matemática inline: `$a^2+b^2=c^2$`;
- matemática em bloco: cerca de código com linguagem `math`;
- não usar `\[` e `\]`;
- não deixar ambientes `equation`, `align` ou `aligned` fora de um bloco matemático;
- não usar imagens como fonte primária da equação;
- preservar o LaTeX como texto pesquisável, versionável e acessível.

Exemplo normativo:

```text
```math
\beta_z=\sqrt{k_0^2\varepsilon_r\mu_r-k_c^2}
```
```

A renderização esperada é:

```math
\beta_z=\sqrt{k_0^2\varepsilon_r\mu_r-k_c^2}
```

## 2. Por que usar cercas `math`

O GitHub aceita tanto `$$...$$` quanto blocos cercados por `math`. A cerca explícita é adotada porque:

1. reduz conflitos com cifrões usados em texto, scripts e valores monetários;
2. evita ambiguidades de quebra de linha em Markdown;
3. torna o início e o fim de cada expressão inequívocos;
4. facilita validação automática;
5. continua sendo renderizada pelo MathJax do GitHub;
6. mantém o arquivo legível em editores sem MathJax.

## 3. Validação automática

O script abaixo varre todos os arquivos Markdown:

```bash
python scripts/normalizar_formulas_markdown.py --check
```

Para converter delimitadores de bloco antigos de forma determinística:

```bash
python scripts/normalizar_formulas_markdown.py --apply
```

O normalizador:

- converte linhas isoladas `$$` em cercas `math`;
- converte `\[` e `\]` em cercas `math`;
- converte expressões `$$...$$` de uma linha em blocos;
- ignora exemplos que já estão dentro de blocos de código;
- falha diante de delimitadores não fechados;
- não altera matemática inline.

## 4. Limites e macros

A documentação deve preferir comandos MathJax amplamente suportados:

- `\frac`, `\sqrt`, `\sum`, `\int`, `\det`, `\log`, `\exp`;
- `\mathbf`, `\mathcal`, `\mathrm`, `\text`;
- `\begin{bmatrix}...\end{bmatrix}`;
- `\begin{aligned}...\end{aligned}` dentro de um bloco `math`;
- letras gregas e operadores padrão.

Macros personalizadas devem ser evitadas no README. Quando indispensáveis, devem ser definidas localmente na própria expressão ou no futuro portal de documentação.

## 5. Alternativa para publicação científica

O Markdown continuará sendo a fonte canônica. Para artigos, relatórios regulatórios ou documentação congelada, o mesmo conteúdo poderá ser convertido para:

- PDF via Pandoc/LaTeX;
- site estático com MkDocs e MathJax;
- HTML autocontido com MathJax;
- Jupyter Book, caso os capítulos passem a incluir notebooks executáveis.

SVGs de equações serão usados apenas quando houver uma limitação comprovada do renderizador, sempre acompanhados do LaTeX original e de texto alternativo. Não se deve substituir em massa matemática textual por imagens.

## 6. Critério de aceite

Uma alteração documental que contenha matemática somente é aceita quando:

1. o script de validação retorna código zero;
2. todos os blocos estão fechados;
3. a expressão renderiza na interface web do GitHub;
4. a versão textual continua semanticamente compreensível;
5. símbolos, índices, vetores e unidades estão definidos no capítulo ou no glossário.
