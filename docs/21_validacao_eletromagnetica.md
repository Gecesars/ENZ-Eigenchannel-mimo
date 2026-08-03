# 21 — Plano de validação eletromagnética

## Gate EM-VALIDATION-01

## 1. M0 — Guia e cavidade fechada

Objetivos:

- confirmar corte $TE_{10}$;
- identificar $TM_{11}$;
- obter eigenfrequências;
- mapear campos;
- calcular participação energética.

Configuração:

- Eigenmode;
- 8 a 12 modos;
- busca 18–32 GHz;
- convergência de frequência inferior a 0,1%.

## 2. M1 — Três ranhuras

- Driven Modal;
- WR-28;
- frequência adaptativa 25,87 GHz;
- sweep 25,3–26,8 GHz;
- extrair $S_{11}$;
- padrão pencil beam;
- campos das ranhuras.

## 3. M2 — Cinco ranhuras

- preservar área;
- remover degrau inicialmente;
- verificar frequência;
- comparar fase;
- medir fan beam.

## 4. M3 — Degrau

- variar largura e altura;
- reproduzir $w_{sp}=9$ mm e $h_{sp}=1$ mm;
- calcular ripple e SLL;
- observar redistribuição de amplitude.

## 5. M4 — Modelo fabricável

Adicionar:

- paredes reais;
- chanfros de 3 mm;
- pinos;
- FR4;
- parafusos quando conhecidos;
- gaps;
- condutividade;
- rugosidade.

## 6. Malha

Refinamento em:

- bordas de ranhuras;
- pinos;
- dopante;
- degrau;
- chanfros;
- porta;
- gaps.

Convergência simultânea:

```math
\Delta f_r,
\quad
\Delta S_{11},
\quad
\Delta G,
\quad
\Delta BW_{1dB},
\quad
\Delta\sigma_\phi.
```

## 7. Domínio aberto

Comparar:

- Radiation Boundary;
- PML.

Variar distância do airbox.

## 8. Materiais

Casos:

1. PEC e dielétrico sem perdas;
2. alumínio;
3. FR4 nominal;
4. FR4 caracterizado;
5. rugosidade;
6. gaps.

## 9. Balanço de potência

Verificar:

```math
P_{\mathrm{inc}}
=
P_{\mathrm{ref}}
+
P_{\mathrm{rad}}
+
P_{\mathrm{loss}}
+
P_{\mathrm{guided,out}}.
```

Erro numérico deve ser documentado.

## 10. Critérios de reprodução

A concordância não será binária. Relatar:

- erro de frequência;
- erro de banda;
- erro de ganho;
- erro de ripple;
- erro de beamwidth;
- erro de SLL;
- diferenças de material e medição.

## 11. Multiporta

Somente após validação G0:

- criar duas portas;
- exportar S2P;
- padrões embarcados;
- TARC;
- ECC de campo;
- capacidade.

## 12. Artefatos

Cada modelo terá:

```text
spec.yaml
model.aedt
manifest.json
sparameters.sNp
embedded_fields/
aperture_fields/
convergence.csv
metrics.json
plots/
report.md
```
