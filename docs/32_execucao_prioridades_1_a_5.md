# 32 — Execução das prioridades 1 a 5

## 1. Resultado executivo

Em 3 de agosto de 2026, as prioridades foram executadas até o limite permitido
pelas evidências disponíveis. Nenhuma dimensão ausente foi ajustada para obter
concordância com o artigo.

| Prioridade | Resultado | Estado científico |
|---|---|---|
| 1 — fórmulas | sinais, dispersão, velocidade de grupo e perturbação material corrigidos | DERIVADO |
| 2 — ontologia | sete classes únicas, schemas e validação condicional | DERIVADO |
| 3 — cotas do artigo | texto auditado; cotas exclusivas da Figura 2 permanecem ausentes | DERIVADO |
| 4 — M0/runtime | worker real e M0 sintético concluídos no AEDT 2024 R2 | SIMULADO |
| 5 — M1–M4/MIMO | infraestrutura e métricas implementadas; geometria fiel bloqueada | DERIVADO |

## 2. Auditoria de fórmulas

**DERIVADO:** sob a convenção $e^{j\omega t}$, uma frequência quase normal
decrescente tem $\tilde\omega=\omega_r+j\gamma$, com $\gamma>0$. A forma
anterior com sinal negativo crescia no tempo.

**DERIVADO:** a dispersão do guia preenchido exige o fator
$\sqrt{\varepsilon_r\mu_r}$ quando $f_c$ é a frequência de corte no meio. A
permissividade efetiva, a velocidade de grupo e as formas equivalentes foram
normalizadas para uma única definição de $f_c$.

**DERIVADO:** na perturbação de cavidade normalizada pela soma das parcelas
elétrica e magnética, $\Delta\varepsilon$ e $\Delta\mu$ entram com o mesmo
sinal e não há fator $1/2$ adicional diante da razão. O limite uniforme recupera
$\omega\propto(\varepsilon\mu)^{-1/2}$.

As fontes primárias e as limitações estão em
[`30_auditoria_independente_de_formulas.md`](30_auditoria_independente_de_formulas.md).

## 3. Evidências e dimensões

**PUBLICADO:** o texto acessível confirmou 25,87 GHz, área transversal de
108 mm², seção inicial 14 mm × 7,7143 mm, WR-28 7,11 mm × 3,56 mm, degrau
9 mm × 1 mm, chanfros de 3 mm, gaps de 0,05 mm e intervalos medidos das
ranhuras.

**DESCONHECIDO:** comprimento/orientação completa da cavidade, espessuras,
cotas nominais e posições das ranhuras, plano de referência da porta, FR4 e
pinos ainda dependem da Figura 2, CAD ou informação dos autores. A especificação
`g0_artigo_base.auditado.v3.yaml` bloqueia M0–M4 por construção.

## 4. M0 sintético no AEDT

**HIPÓTESE:** as dimensões 20 mm × 14 mm × 7,7143 mm pertencem exclusivamente
ao smoke test declarativo. Elas não constituem reconstrução do artigo.

**SIMULADO:** o run local `ENZ-20260803-165824-52288067` concluiu no AEDT
2024.2.0, PyAEDT 1.3.0, PID 72656 e porta gRPC 65137. O setup convergiu em três
passes, com 3268 tetraedros e máximo $\Delta f=0{,}00091896\%$ para alvo de
0,5%. Após o encerramento, `orphan_after_close=false`.

| modo | frequência HFSS (GHz) | frequência analítica (GHz) | erro relativo |
|---:|---:|---:|---:|
| 1 | 18,421496 | 18,420802 — índices (2,1,0) | 0,00377% |
| 2 | 20,827054 | 20,826288 — índices (1,0,1) | 0,00368% |
| 3 | 22,186815 | 22,185563 — índices (0,1,1) | 0,00564% |
| 4 | 22,688994 | 22,687458 — índices (1,2,0) | 0,00677% |

**DERIVADO:** a referência analítica usa

```math
f_{mnp}=\frac{c}{2}
\sqrt{\left(\frac{m}{a}\right)^2+
\left(\frac{n}{b}\right)^2+
\left(\frac{p}{d}\right)^2}.
```

O maior erro entre HFSS e a referência analítica foi 0,00677%. O teste unitário
repete essa comparação com tolerância de $7\times10^{-5}$ em erro relativo.

**SIMULADO:** o AEDT retornou `Q=0` para os quatro modos da cavidade PEC sem
perdas. Esse valor bruto está preservado, mas não é interpretado como fator de
qualidade físico finito; balanço de potência não se aplica a esta solução
Eigenmode fechada.

## 5. Multiporta e M1–M4

**DERIVADO:** foram implementados TARC, potência aceita, matriz de Gram de
padrões vetoriais complexos, ECC por campo, rank efetivo, capacidade de Shannon
e resíduo de balanço de potência. A fase e a polarização complexas são mantidas.
Capacidade não é chamada de throughput.

**DERIVADO:** o exportador Driven Modal gera Touchstone com extensão determinada
pelo número real de excitações e solicita metadados, potência e padrões
embarcados complexos por elemento. Essa rota passou por teste unitário, não por
simulação licenciada de M1–M4.

**DESCONHECIDO:** nenhuma métrica multiporta, campo complexo, balanço de potência
ou diversidade foi promovido a SIMULADO, pois não existe geometria G0 fiel e
executável. Isolamento, sozinho, não será usado para inferir diversidade MIMO.

## 6. Rastreabilidade de falhas

Runs intermediários foram conservados como `FAILED`: interrupção do launcher,
ausência de CSV modal e duas interpretações incorretas dos eixos `Freq`/`X`.
Essas tentativas não foram ocultadas nem promovidas. O exportador final consulta
as categorias `Eigen Modes` e `Eigen Q` expostas pelo próprio AEDT.
