# 22 — Plano experimental e metrologia

## 1. Objetivo

Validar:

- matching;
- eficiência;
- ganho;
- padrões;
- polarização;
- fase;
- matriz multiporta;
- canal MIMO.

## 2. Protótipos

Fabricar ao menos três unidades por versão crítica para separar erro sistemático e variação de fabricação.

## 3. Processo mecânico

- split-block de alumínio;
- pinos de alinhamento;
- faces críticas em uma única fixação;
- torque documentado;
- metrologia CMM;
- rugosidade medida;
- gaps controlados;
- dopante removível.

## 4. VNA

- extensores mmWave ou transições WR-28;
- calibração TRL/LRL/SOLT apropriada;
- de-embedding;
- cabos estabilizados;
- repetição térmica;
- S1P/S2P/S4P completo.

## 5. Câmara anecoica

Medir padrões embarcados por porta:

- demais portas em cargas;
- co- e cross-pol;
- fase coerente;
- 3D quando possível;
- frequências na banda.

## 6. Phase center

Determinar por ajuste de fase esférica ou método equivalente. Registrar incerteza.

## 7. Eficiência

Métodos:

- integração de padrão;
- Wheeler cap quando aplicável;
- reverberation chamber;
- ganho–diretividade.

## 8. Canal 4×4

Plataforma coerente:

- LO comum;
- referência de 10 MHz;
- sincronização;
- quatro cadeias Tx e Rx;
- calibração complexa;
- OFDM experimental.

## 9. Cenários

- anecoico LoS;
- corredor;
- laboratório;
- ambiente industrial;
- bloqueio;
- usuário móvel.

## 10. Orçamento de incerteza

Incluir:

- calibração VNA;
- ganho da antena padrão;
- distância;
- alinhamento;
- reflexões;
- repetibilidade;
- temperatura;
- cabo;
- posicionador;
- potência.

Incerteza expandida:

```math
U=k u_c,
```

tipicamente com $k=2$ quando apropriado.

## 11. Comparação

Mesma sessão e configuração para antena ENZ e referências, reduzindo drift.

## 12. Honestidade

Medições internas fora de câmara devem ser identificadas. O artigo-base realizou medições de padrão em ambiente indoor; a reprodução deve registrar diferenças de setup.
