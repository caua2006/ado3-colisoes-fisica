/*
 * painel.js — Camada 4 (equivale a formatar_painel do programa Python).
 * Recebe o resultado de simularColisao e devolve o conteúdo do painel.
 * Não faz contas físicas: só formata números.
 */
'use strict';

/**
 * Formata um número em pt-BR (vírgula decimal, sinal de menos tipográfico).
 * Valores que arredondariam para zero viram "0" (evita "−0,00").
 */
function formatarNumero(x, casas) {
  if (casas === undefined) casas = 2;
  if (Math.abs(x) < 0.5 * Math.pow(10, -casas)) x = 0;
  const texto = Math.abs(x).toFixed(casas).replace('.', ',');
  return (x < 0 ? '−' : '') + texto;
}

/** Igual a formatarNumero, mas com "+" explícito para positivos. */
function formatarComSinal(x, casas) {
  const texto = formatarNumero(x, casas);
  const zero = formatarNumero(0, casas);
  return texto.charAt(0) === '−' || texto === zero ? texto : '+' + texto;
}

/**
 * Conteúdo do painel (requisito R3) em seções:
 * [{ titulo, linhas: [[rótulo, valor, unidade, destaque?], ...] }, ...]
 * Velocidades antes e depois, p antes/depois, K antes/depois e ΔK,
 * impulsos J1, J2 e força média.
 */
function secoesPainel(r) {
  const f = formatarNumero;
  const s = formatarComSinal;
  const depois = r.houve_colisao
    ? [['u1 = u2 = V', s(r.u1), 'm/s', true]]
    : [['u1', s(r.u1), 'm/s'], ['u2', s(r.u2), 'm/s']];

  return [
    {
      titulo: 'Velocidades',
      linhas: [['v1', s(r.v1), 'm/s'], ['v2', s(r.v2), 'm/s']].concat(depois)
    },
    {
      titulo: 'Momento linear total',
      linhas: [
        ['p antes', f(r.p_antes), 'kg·m/s'],
        ['p depois', f(r.p_depois), 'kg·m/s']
      ]
    },
    {
      titulo: 'Energia cinética total',
      linhas: [
        ['K antes', f(r.K_antes), 'J'],
        ['K depois', f(r.K_depois), 'J'],
        ['ΔK medido', s(r.dK), 'J'],
        ['ΔK = −½ μ (v1 − v2)²', s(r.dK_formula), 'J'],
        ['Fração dissipada', f(100 * r.fracao_dissipada, 1), '%', true]
      ]
    },
    {
      titulo: 'Impulso e força média',
      linhas: [
        ['J1', s(r.J1), 'N·s'],
        ['J2', s(r.J2), 'N·s'],
        ['Δt', f(r.dt_contato * 1000, 0), 'ms'],
        ['Fmed = |J| / Δt', f(r.F_media, 1), 'N', true]
      ]
    }
  ];
}

/** Versão em texto puro do painel (mesmo conteúdo de formatar_painel no Python). */
function formatarPainel(r) {
  const linhas = [r.houve_colisao
    ? 'Colisão perfeitamente inelástica'
    : 'Sem colisão: v1 ≤ v2'];
  secoesPainel(r).forEach(function (sec) {
    linhas.push('', sec.titulo);
    sec.linhas.forEach(function (l) {
      linhas.push('  ' + l[0] + ' = ' + l[1] + ' ' + l[2]);
    });
  });
  return linhas.join('\n');
}
