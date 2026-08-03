# 30 — Auditoria independente de fórmulas centrais

## 1. Escopo

Esta auditoria verifica consistência algébrica interna, convenções e limites de
validade. Ela não substitui revisão por pares nem validação numérica no HFSS.

## 2. Frequência complexa

**DERIVADO:** sob $e^{j\omega t}$ e
$\tilde\omega=\omega_r+j\gamma$, com $\gamma>0$,

```math
e^{j\tilde\omega t}=e^{j\omega_rt}e^{-\gamma t}.
```

Portanto, a versão anterior $\omega_r-j\gamma$ representava crescimento. O
sinal foi corrigido nos documentos 02 e 07. Sistemas abertos e autovalores
complexos são tratados por Lai et al., DOI `10.1103/PhysRevA.41.5187`.

## 3. Dispersão do guia preenchido

**DERIVADO:** partindo de

```math
\beta^2=k_0^2\varepsilon_r\mu_r-k_c^2
```

e de

```math
f_c=\frac{c k_c}{2\pi\sqrt{\varepsilon_r\mu_r}},
```

obtém-se

```math
\beta=k_0\sqrt{\varepsilon_r\mu_r}
\sqrt{1-(f_c/f)^2}.
```

A versão anterior misturava $f_c$ do guia preenchido com a forma que exige a
frequência de corte no vácuo. O erro desaparecia apenas para
$\varepsilon_r\mu_r=1$. A equivalência ENZ por corte é suportada por
Silveirinha e Engheta, DOI `10.1103/PhysRevLett.97.157403`, e Li et al., DOI
`10.1038/s41467-022-31013-z`.

## 4. Perturbação material

**DERIVADO:** para perturbações volumétricas pequenas em uma cavidade ideal,
os incrementos de permissividade e permeabilidade reduzem a frequência com o
mesmo sinal de primeira ordem. A forma anterior continha sinal relativo
incorreto para $\Delta\mu$ e um fator $1/2$ incompatível com o denominador de
energia total. As correções foram aplicadas nos documentos 01a e 04. O teste
de consistência é uma perturbação uniforme: como $\omega\propto
(\varepsilon\mu)^{-1/2}$, a fórmula deve recuperar
$\Delta\omega/\omega=-½(\Delta\varepsilon/\varepsilon+
\Delta\mu/\mu)$.

**PUBLICADO:** a fonte clássica é Slater, DOI
`10.1103/RevModPhys.18.441`.

## 5. Limitações

**DESCONHECIDO:** a adequação quantitativa das aproximações para a cavidade
aberta, dispersiva, carregada e radiativa somente será conhecida após confronto
com Eigenmode, Driven Modal e balanço de potência.

**HIPÓTESE:** formulações biortogonais ou por modos quase normais serão
necessárias se diferenças finitas de forma não convergirem de modo estável.
