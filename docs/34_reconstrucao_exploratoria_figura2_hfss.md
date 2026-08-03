# 34 — Reconstrução exploratória da Figura 2 no HFSS

## 1. Resultado

**HIPÓTESE:** foi criada a especificação declarativa
`modelos/especificacoes/g0_figura2_reconstrucao_exploratoria.hipotese.v5.yaml`.
Ela materializa no HFSS 2024 R2 uma cavidade alimentada por WR-28 com cinco
ranhuras, perfil escalonado, chanfros, slab de FR4, quatro pinos metálicos,
flange, furos de montagem, região aberta e uma porta modal.

**DERIVADO:** esta versão é uma reconstrução exploratória da topologia das
Figuras 1(a) e 2(a), não uma reprodução fiel. O PDF não fornece o CAD, todas as
coordenadas, o plano de referência eletromagnético, as propriedades complexas
do FR4 nem a liga e a rugosidade usadas no solver.

**PUBLICADO:** a fonte primária é E. C. Vilas Boas et al., *A
Millimeter-Wave Flat-Top Fan-Beam Antenna Array Based on a
Geometry-Independent Resonant Cavity*, DOI
`10.1109/OJAP.2026.3703713`, arquivo validado
`doc/pdfs/VilasBoas_2026_OJAP_FlatTop.pdf`.

## 2. Parâmetros geométricos

| Item | Valor usado | Classe | Observação |
|---|---:|---|---|
| frequência adaptativa | 25,87 GHz | PUBLICADO | Figuras 1–2 e Seção III |
| área plana da cavidade | 108 mm² | PUBLICADO | preservada no artigo |
| envelope principal | 36 × 9 × 11,11 mm | PUBLICADO/INFERIDO | 9 mm tem vínculo CAD ambíguo |
| guia WR-28 interno | 7,11 × 3,56 mm | PUBLICADO | modo dominante TE10 |
| ranhuras | 5,66 × 0,8 mm | PUBLICADO | cinco unidades |
| passo dos centros | 4 mm | HIPÓTESE | coordenadas não publicadas |
| degrau | 9 × 1 mm | PUBLICADO | valores finais da Tabela 2 |
| chanfros | 3 mm | PUBLICADO | dois refinamentos descritos |
| slab de FR4 | 3 × 1,65 mm | PUBLICADO | seção nominal da Figura 2(a) |
| FR4 | εr=4,4; tanδ=0,02 | HIPÓTESE | material genérico do AEDT |
| pinos | 4 × Ø1 mm | PUBLICADO | eixos são HIPÓTESE |
| condutor | PEC | HIPÓTESE | alumínio é publicado; propriedades não |
| cavidade interna | 18 × 6 mm | DERIVADO/INFERIDO | 18 × 6 = 108 mm² |

O YAML contém a classificação e a fonte individual de cada parâmetro. Nenhuma
dessas hipóteses foi ajustada para coincidir com S11, ganho ou padrão do artigo.

## 3. Objetos HFSS e topologia

**DERIVADO:** os 19 objetos primitivos têm nomes determinísticos. Operações
booleanas unem o corpo, a alimentação e a flange; removem cavidade, guia,
ranhuras e furos; e preservam como volumes físicos o ar, o FR4 e os quatro
pinos.

Objetos eletromagnéticos finais principais:

- `Housing_Cavity`: corpo condutor PEC com perfil e chanfros;
- `Cavity_Air`: cavidade e guia de alimentação unidos;
- `FR4_Slab`: inclusão dielétrica;
- `Rod_PEC_NW`, `Rod_PEC_NE`, `Rod_PEC_SW`, `Rod_PEC_SE`: pinos;
- `Port_WR28_Sheet`: plano da porta;
- `Open_Region`: domínio aberto.

Vistas exportadas:

- `artefatos/runs/ENZ-20260803-180323-ae961d5a/plots/geometry_isometric.png`;
- `artefatos/runs/ENZ-20260803-180323-ae961d5a/plots/geometry_top.png`;
- `artefatos/runs/ENZ-20260803-180323-ae961d5a/plots/geometry_front.png`.

## 4. Porta, fronteiras e setup

**PUBLICADO:** o artigo informa alimentação WR-28, HFSS/FEM, frequência
central de 25,87 GHz e gráficos no intervalo de 25 a 27 GHz.

**HIPÓTESE:** o PDF não divulga o setup numérico completo. A implementação usa:

```text
Solution type: Driven Modal
Port: P1_WR28_TE10, uma porta física, 1 modo solicitado, 50 ohm
Adaptive frequency: 25.87 GHz
MaxDeltaS: 0.02
Minimum passes: 2
Minimum converged passes: 2
Maximum passes: 15
Refinement per pass: 20%
Sweep: interpolating, 25–27 GHz, 201 pontos
Radiation boundary: cinco faces; a face y_min contém a porta
Far-field sphere declarada: passo angular de 2 graus
HPC: 14 cores, 1 task, 0 GPU
```

**SIMULADO:** o solver advertiu que a seção da porta suporta um modo adicional
associado a um grupo degenerado com o modo 2. A advertência foi preservada. Ela
não foi interpretada como uma segunda porta física ou como evidência MIMO.

## 5. Validação executada

### Build aceito

**SIMULADO:** o run `ENZ-20260803-180323-ae961d5a` terminou como `BUILT`:

- AEDT 2024.2.0 e PyAEDT 1.3.0 sobre gRPC nativo;
- validação do design sem mensagens;
- projeto salvo antes da solução;
- PID encerrado e `orphan_after_close=false`;
- 14 cores registrados no manifesto.

### Solve exploratório não promovido

**SIMULADO:** o run `ENZ-20260803-180417-ae961d5a` convergiu em três passes,
com `Max Mag. Delta S = 0,0017822`, 25.284 elementos solucionados e 29.491
tetraedros na estatística final. O sweep interpolante convergiu e foi declarado
passivo pelo HFSS; Touchstone S1P, convergência, malha e perfil foram gravados.

**SIMULADO:** o mesmo run permaneceu `FAILED` porque o PyAEDT 1.3.0 lançou uma
exceção ao receber `variations=None` na exportação de metadados de antena. O
exportador foi corrigido para passar `{}` explicitamente e um teste de
regressão foi adicionado.

**SIMULADO:** a repetição `ENZ-20260803-180655-ae961d5a` foi interrompida
durante uma exportação de campo distante sem progresso observável. O PID
encerrou, a porta gRPC fechou, o lock foi removido e
`orphan_after_close=false`. O run foi marcado `FAILED` e não foi promovido.

## 6. Campo elétrico da página 3

**PUBLICADO:** a Figura 1(a) mostra distribuições de magnitude do campo elétrico
em 25,87 GHz para as etapas geométricas do artigo.

**DESCONHECIDO:** os arquivos de campo complexo, a escala espacial do corte e a
malha originais não são publicados.

**SIMULADO:** a solução exploratória preserva o campo fasorial no banco de
resultados do run solucionado. A tentativa de criar o plot de corte na sessão
gráfica excedeu o limite operacional e não foi salva. Não se apresenta uma
imagem de magnitude como substituta de fase complexa nem como reprodução da
Figura 1(a).

## 7. Estado da sessão gráfica

**SIMULADO:** o projeto de build está aberto no AEDT 2024 R2, design
`HFSS_ENZ_G0_figura2_reconstrucao_exploratoria_M4`, em uma sessão dedicada. A
sessão gráfica preexistente do usuário permaneceu aberta e não foi encerrada.

## 8. Bloqueios para reprodução fiel

**DESCONHECIDO:** ainda são necessários:

- CAD ou coordenadas dos cinco centros de ranhura e quatro eixos de pino;
- contorno interno completo e espessuras locais;
- plano de referência da porta e geometria do adaptador;
- εr(f), tanδ(f), fabricante e orientação do FR4;
- liga, condutividade e rugosidade do alumínio;
- malha, critérios adaptativos e dados complexos originais;
- balanço de potência e exportação complexa completa sem falhas.

Até que esses itens sejam resolvidos, a classificação global permanece
`HIPÓTESE`.
