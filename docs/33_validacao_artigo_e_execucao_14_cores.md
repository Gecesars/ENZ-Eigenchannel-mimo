# 33 — Validação do artigo e execução AEDT com 14 cores

## Resultado executivo

**PUBLICADO:** o PDF principal foi obtido, verificado e identificado pelo DOI
`10.1109/OJAP.2026.3703713`, com SHA-256
`57f4627b41767a8edc07eca437fb62c192fe277d3d891df39ce4bf53d101a40a`.

**DERIVADO:** sete relações numéricas verificáveis diretamente no documento
foram recalculadas e são consistentes dentro da precisão publicada: área
transversal, corte TE10 do WR-28, três larguras de banda, FBW medido e dimensões
normalizadas. O registro calculável está em
`doc/pdfs/validacao_numerica_artigo.json`.

**SIMULADO:** o smoke test M0 foi executado no AEDT 2024 R2 com 14 cores, uma
task e nenhuma GPU. Ele convergiu em três passes, com 3268 tetraedros e
variação final de frequência de 0,00091896%. O PID do AEDT foi encerrado e o
teste de processo órfão retornou `false`.

**HIPÓTESE:** M0 é uma cavidade PEC sintética de 20 mm × 14 mm × 7,7143 mm.
Esse run valida a infraestrutura e não é uma reprodução da antena.

**DESCONHECIDO:** nenhuma execução fiel M0–M4 do artigo foi autorizada pela
evidência disponível, porque faltam propriedades e coordenadas necessárias.

## Cotas auditadas na Figura 2(a)

**PUBLICADO:** a inspeção visual do PDF confirma:

- dimensões externas associadas ao tamanho normalizado: 11 mm × 27 mm × 36 mm;
- largura local de 11,11 mm e flange/base de 22,5 mm;
- ranhuras nominais de 5,66 mm × 0,8 mm;
- parede nominal de 1 mm;
- seção WR-28 de 7,11 mm × 3,56 mm;
- degrau final de 9 mm × 1 mm;
- dois chanfros de 3 mm;
- seção do slab de FR4 de 3 mm × 1,65 mm;
- quatro pinos metálicos de 1 mm de diâmetro;
- demais cotas brutas visíveis de 11 mm, 12,50 mm, 14 mm, 5 mm, 9 mm e 6 mm.

**DERIVADO:** as últimas seis cotas foram preservadas como observações brutas,
sem convertê-las em coordenadas CAD, pois a figura não declara origem nem
referencial paramétrico.

## Verificações aritméticas

| Relação | Publicado | Recalculado | Resultado |
|---|---:|---:|---|
| área inicial | 108 mm² | 14 × 7,7143 = 108,0002 mm² | consistente |
| corte TE10, `a=7,11 mm` | 21,08 GHz | 21,08245 GHz | consistente |
| banda Modelo I | 600 MHz | 26,23 − 25,63 = 600 MHz | consistente |
| banda final, um dos trechos | 600 MHz | 26,24 − 25,64 = 600 MHz | consistente |
| banda medida | 1,11 GHz | 26,71 − 25,60 = 1,11 GHz | consistente |
| FBW medida | 4,24% | 4,2439% | consistente |
| tamanho em `λ0`, 25,87 GHz | 0,95 × 2,33 × 3,10 | 0,949 × 2,330 × 3,106 | consistente |

## Características publicadas sem dados suficientes para reprodução

**PUBLICADO:** o artigo divulga S11, ressonância, ganho, eficiência, campos,
beamwidth, ripple, SLL, polarização cruzada e coerência aproximada de fase.

**DESCONHECIDO:** o PDF não fornece:

- Touchstone complexo;
- campos E/H complexos ou fase complexa por ranhura;
- arquivos de padrão embarcado;
- malha, setup completo ou CAD;
- `εr(f)` e `tanδ(f)` do FR4;
- liga/condutividade usada para o alumínio no solver;
- coordenadas dos centros das cinco ranhuras e dos quatro pinos;
- comprimento interno inequívoco da cavidade e plano de referência da porta.

**DERIVADO:** sem esses itens, ajustar uma geometria até coincidir com S11,
ganho ou padrão seria ajuste silencioso, não validação. Por isso M1–M4 continuam
`documental_bloqueado` em `g0_artigo_base.auditado.v4.yaml`.

## Divergências internas do documento

**PUBLICADO:** foram preservadas quatro divergências/ambiguidades:

1. A banda simulada final aparece como 25,64–26,24 GHz em um trecho e
   25,64–26,25 GHz em outros.
2. A frequência superior do padrão aparece como 26,25 GHz na Tabela 3 e
   26,22 GHz na Figura 4.
3. O cabeçalho da página 1 contém o placeholder
   `10.1109/OJAP.2020.1234567`, enquanto rodapé e metadados usam o DOI correto.
4. O SLL aparece como nível abaixo de −10,02 dB no resumo e como magnitude de
   supressão `>10,02 dB` nas tabelas.

## Run aceito

| Campo | Valor |
|---|---|
| run | `ENZ-20260803-173105-52288067` |
| classificação do resultado | SIMULADO |
| classificação da geometria | HIPÓTESE |
| AEDT | 2024.2.0, seleção estrita |
| PyAEDT | 1.3.0 |
| transporte | gRPC nativo |
| licença | disponível, valor registrado no manifesto |
| recursos | 14 cores, 1 task, 0 GPU |
| PID/porta | 165372 / 52412 |
| convergência | 3 passes, 0,00091896% ≤ 0,5% |
| malha | 3268 tetraedros |
| órfão após fechar | `false` |
| erros AEDT | zero |

**DERIVADO:** as quatro autofrequências simuladas foram comparadas à solução
analítica da cavidade retangular PEC. Os erros relativos ficaram entre
0,00377% e 0,00677%, abaixo do gate de 0,01%.

**DERIVADO:** balanço de potência é não aplicável a M0: trata-se de uma
cavidade PEC fechada em Eigenmode, sem portas, perdas ou potência incidente.

O pacote aprovado está em `poros_aedt/`. Seu manifesto inventaria 60 arquivos
com SHA-256; os hashes foram rechecados após a cópia.

## Tentativa excluída

**SIMULADO:** o run `ENZ-20260803-173034-52288067` foi interrompido durante a
inicialização por um timeout externo curto. O PID criado por essa tentativa foi
encerrado explicitamente e o run não foi copiado para `poros_aedt`.
