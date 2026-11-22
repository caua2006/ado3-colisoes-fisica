# ADO-3 — Colisões, Impulso e Conservação do Momento Linear

Física: Práticas Extensivas, Prof. Ettore Baldini-Neto.
**Opção B: colisão perfeitamente inelástica.**

Animação interativa de uma colisão frontal (1D) entre dois blocos que ficam unidos depois do choque.
Tudo sai das fórmulas fechadas da seção 2 do enunciado, sem integração numérica:

- V = (m1·v1 + m2·v2)/(m1 + m2), velocidade comum depois do choque (m/s)
- ΔK = −½·μ·(v1 − v2)², com μ = m1·m2/(m1 + m2), energia dissipada (J)
- J1 = m1·(V − v1) = −J2 e Fmed = |J|/Δt, impulso (N·s) e força média (N)

O programa mostra os blocos em MRU antes e depois do instante de colisão tc, tem sliders para m1, m2, v1, v2 e Δt,
um painel com p, K, ΔK, J e Fmed e gráficos de barras de p e K antes e depois. O caso sem colisão (v1 ≤ v2) aparece
como mensagem na tela.

## Integrantes

- Cauã Carvalho de Oliveira
- Pedro Henrique Patrício
- João Pedro Moz

## Estrutura

```
ado3colisoesimpulsomomentolinear/
├── enunciado/   enunciado_ado3.pdf
├── entrega/     ado3_cauacarvalhodeoliveira_pedrohenriquepatricio_joaopedromoz.py
├── relatorio/   relatorio_ado3.md e relatorio_ado3.pdf
└── docs/        versão web (GitHub Pages)
```

O programa Python é dividido em cinco partes, cada uma usando só as anteriores:

1. Fórmulas (momento, cinetica, massa_reduzida, colisao_inelastica, impulso, forca_media)
2. Resultado da colisão (simular_colisao)
3. Cinemática (largura dos blocos, instante do choque, posições em MRU)
4. Texto do painel (formatar_painel)
5. Interface matplotlib (animação, sliders, botões e barras)

A versão web em `docs/js/` usa as mesmas funções, com os mesmos nomes.

## Como rodar o Python

Requer Python 3 com **matplotlib** e **numpy**.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install matplotlib numpy
python entrega/ado3_cauacarvalhodeoliveira_pedrohenriquepatricio_joaopedromoz.py
```

Valores padrão: m1 = 2,0 kg, m2 = 3,0 kg, v1 = 5,0 m/s, v2 = 0, Δt = 10 ms.
Resultado: V = 2,0 m/s; p = 10,0 kg·m/s antes e depois; K: 25,0 J → 10,0 J (ΔK = −15,0 J, 60 % dissipado);
J1 = −6,0 N·s, J2 = +6,0 N·s; Fmed = 600 N (60 N com Δt = 100 ms).

## Versão web

JavaScript puro, sem dependências. Basta abrir `docs/index.html` no navegador.

Para publicar no GitHub Pages: **Settings > Pages > Deploy from a branch > main, pasta /docs**.
