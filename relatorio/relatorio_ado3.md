# ADO-3 — Colisões, Impulso e Conservação do Momento Linear

**Física: Práticas Extensivas** · Prof. Ettore Baldini-Neto

**Grupo:** Cauã Carvalho de Oliveira, Pedro Henrique Patrício, João Pedro Moz
**Opção escolhida:** B (colisão perfeitamente inelástica)

**Situação padrão:** m₁ = 2,0 kg, m₂ = 3,0 kg, v₁ = 5,0 m/s, v₂ = 0, Δt = 10 ms. Sentido positivo para a direita. Todas as fórmulas são as da Seção 2 do enunciado, em unidades do SI.

## Q1 — Velocidade final

Na colisão perfeitamente inelástica os blocos seguem juntos (u₁ = u₂ = V):

> V = (m₁v₁ + m₂v₂) / (m₁ + m₂)
> V = (2,0 · 5,0 + 3,0 · 0) / (2,0 + 3,0) = 10,0 / 5,0 = **2,0 m/s**

O conjunto segue para a direita a 2,0 m/s. O painel do programa mostra u₁ = u₂ = V = 2,00 m/s, igual à conta feita à mão.

## Q2 — Conservação do momento linear

> p antes = m₁v₁ + m₂v₂ = 2,0 · 5,0 + 3,0 · 0 = **10,0 kg·m/s**
> p depois = (m₁ + m₂) · V = 5,0 · 2,0 = **10,0 kg·m/s**

Logo p antes = p depois = 10,0 kg·m/s. No programa, as duas barras de p têm a mesma altura.

**Por que se conserva mesmo sendo inelástica?** O momento total só muda se houver força externa resultante. Na horizontal o sistema é isolado: peso e normal são verticais e o atrito é desprezado. As forças do choque são de contato entre os próprios blocos, ou seja, internas. Pela 3ª lei de Newton, a força que um bloco faz no outro é igual e oposta em cada instante do contato. Por isso os impulsos são opostos (J₁ = −J₂) e a variação total é Δp = J₁ + J₂ = 0. A perda de energia cinética não interfere nisso: as forças internas fazem trabalho ao deformar os blocos, mas continuam aos pares e se cancelam no momento total.

## Q3 — Energia cinética e fração dissipada

> K antes = ½ m₁v₁² + ½ m₂v₂² = ½ · 2,0 · 5,0² + 0 = **25,0 J**
> K depois = ½ (m₁ + m₂) V² = ½ · 5,0 · 2,0² = **10,0 J**
> ΔK = K depois − K antes = 10,0 − 25,0 = **−15,0 J**
> Fração dissipada = |ΔK| / K antes = 15,0 / 25,0 = **60 %**

**Conferência pela fórmula com a massa reduzida:**

> μ = m₁m₂ / (m₁ + m₂) = (2,0 · 3,0) / 5,0 = 1,2 kg
> ΔK = −½ μ (v₁ − v₂)² = −½ · 1,2 · (5,0 − 0)² = **−15,0 J**

O resultado é o mesmo do cálculo direto, e o painel mostra os dois valores iguais a −15,00 J.

**Para onde vão os 15 J?** Eles não somem: deixam de ser energia cinética. Uma parte vira **deformação permanente** dos blocos (o trabalho de amassar e grudar), outra vira **calor** (um pequeno aumento de temperatura na região do contato) e outra vira **som** e vibração. A energia total se conserva; só a cinética não.

## Q4 — Impulso e força média

Pelo teorema do impulso–momento, J = m (u − v), com u = V = 2,0 m/s:

> J₁ = m₁ (V − v₁) = 2,0 · (2,0 − 5,0) = **−6,0 N·s**
> J₂ = m₂ (V − v₂) = 3,0 · (2,0 − 0) = **+6,0 N·s**

J₁ + J₂ = 0, ou seja, J₁ = −J₂, como pede a 3ª lei de Newton. O bloco 1 é freado (impulso para a esquerda) e o bloco 2 é empurrado para a direita.

**Força média** (Fmed = |J| / Δt, com Δt em segundos):

> Δt = 10 ms = 0,010 s → Fmed = 6,0 / 0,010 = **600 N**
> Δt = 100 ms = 0,100 s → Fmed = 6,0 / 0,100 = **60 N**

Com Δt dez vezes maior, o **impulso continua o mesmo** (6,0 N·s), porque ele depende só das velocidades antes e depois. No programa, mudar Δt não altera V, p nem K. Como J = Fmed · Δt é fixo, a **força média fica dez vezes menor**. É o princípio do airbag, do para-choque deformável e de dobrar os joelhos ao pular: a mesma variação de momento acontece em mais tempo, com força bem menor.

## Q5 — Blocos em sentidos opostos com momento total nulo

Escolhemos m₁ = 2,0 kg, v₁ = 3,0 m/s, m₂ = 3,0 kg e v₂ = −2,0 m/s, de modo que m₁v₁ + m₂v₂ = 6,0 − 6,0 = 0.

> V = (2,0 · 3,0 + 3,0 · (−2,0)) / 5,0 = 0 / 5,0 = **0**
> K antes = ½ · 2,0 · 3,0² + ½ · 3,0 · 2,0² = 9,0 + 6,0 = **15,0 J**
> K depois = ½ · 5,0 · 0² = **0**
> ΔK = −15,0 J → fração dissipada = **100 %**

Conferência: ΔK = −½ · 1,2 · (3,0 − (−2,0))² = −½ · 1,2 · 25 = −15,0 J.

**Explicação:** o momento total é zero antes e, por conservação, continua zero depois. Como os blocos ficam unidos, a única possibilidade é o conjunto **parar** (V = 0). Sem velocidade não há energia cinética, então **toda** a energia cinética inicial (15 J) vira deformação, calor e som. É o caso de perda máxima. Mesmo assim os impulsos não são nulos: J₁ = 2,0 · (0 − 3,0) = −6,0 N·s e J₂ = 3,0 · (0 + 2,0) = +6,0 N·s, ainda com J₁ = −J₂.
