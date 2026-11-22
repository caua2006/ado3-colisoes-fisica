/*
 * fisica.js — Camadas 1 e 2 (mesmas funções do programa Python).
 * ADO-3, Opção B: colisão perfeitamente inelástica.
 *
 * Todas as fórmulas vêm da Seção 2 ("Resumo teórico") do enunciado.
 * Unidades SI: kg, m/s, J, N·s, N, s.
 * Nada aqui desenha ou lê a página: só contas.
 *
 * Script clássico (sem type=module): as funções ficam no escopo global
 * para funcionar também abrindo o index.html direto (file://).
 */
'use strict';

/* ------------------------------------------------------------------ */
/* Camada 1 — fórmulas puras (uma função por fórmula)                  */
/* ------------------------------------------------------------------ */

/**
 * Momento linear de um corpo.
 * p = m·v   [kg·m/s]
 * Enunciado, Seção 2: "Momento linear total: p = m1v1 + m2v2" (cada parcela).
 */
function momento(m, v) {
  return m * v;
}

/**
 * Energia cinética de um corpo.
 * K = ½·m·v²   [J]
 * Enunciado, Seção 2: "Energia cinética total: K = ½m1v1² + ½m2v2²" (cada parcela).
 */
function cinetica(m, v) {
  return 0.5 * m * v * v;
}

/**
 * Massa reduzida do par.
 * μ = m1·m2/(m1 + m2)   [kg]
 * Enunciado, Seção 2, quadro da colisão perfeitamente inelástica.
 */
function massaReduzida(m1, m2) {
  return (m1 * m2) / (m1 + m2);
}

/**
 * Velocidade comum depois da colisão perfeitamente inelástica.
 * V = (m1·v1 + m2·v2)/(m1 + m2)   [m/s]
 * Enunciado, Seção 2, quadro da colisão perfeitamente inelástica
 * (vem da conservação do momento com u1 = u2 = V).
 */
function colisaoInelastica(m1, m2, v1, v2) {
  return (m1 * v1 + m2 * v2) / (m1 + m2);
}

/**
 * Variação da energia cinética prevista pela fórmula fechada.
 * ΔK = K_depois − K_antes = −½·μ·(v1 − v2)²   [J]
 * Enunciado, Seção 2, quadro da colisão perfeitamente inelástica.
 */
function variacaoEnergiaFormula(m1, m2, v1, v2) {
  const mu = massaReduzida(m1, m2);
  const vRel = v1 - v2;
  return -0.5 * mu * vRel * vRel;
}

/**
 * Impulso sobre um corpo (teorema do impulso–momento linear).
 * J = m·(u − v)   [N·s]
 * Enunciado, Seção 2: "J1 = m1(u1 − v1) e J2 = m2(u2 − v2)".
 */
function impulso(m, vAntes, vDepois) {
  return m * (vDepois - vAntes);
}

/**
 * Força média durante o contato.
 * Fmed = |J|/Δt   [N]   (J em N·s, Δt em s)
 * Enunciado, Seção 2: "Se o contato dura Δt, a força média é Fmed = |J|/Δt".
 */
function forcaMedia(J, dt) {
  if (!(dt > 0)) {
    throw new RangeError('Δt deve ser positivo (em segundos).');
  }
  return Math.abs(J) / dt;
}

/* ------------------------------------------------------------------ */
/* Camada 2 — cenário completo (interface principal)                   */
/* ------------------------------------------------------------------ */

/**
 * Simula a colisão e devolve um objeto congelado com os MESMOS campos do
 * ResultadoColisao do Python (nomes idênticos, em snake_case):
 *
 *   houve_colisao        bool    false se v1 <= v2 (requisito R5)
 *   v1, v2, u1, u2       m/s     velocidades antes e depois (u1 = u2 = V)
 *   p_antes, p_depois    kg·m/s
 *   K_antes, K_depois    J
 *   dK, dK_formula       J       medido (K_depois − K_antes) e pela fórmula com μ
 *   fracao_dissipada     —       |dK|/K_antes (0 se K_antes = 0)
 *   J1, J2               N·s
 *   F_media              N
 *   dt_contato           s       (o slider está em ms; a interface converte)
 *
 * Sem colisão (v1 <= v2): u1 = v1, u2 = v2, J = 0, Fmed = 0, dK = dK_formula = 0.
 * Massas <= 0 ou Δt <= 0 lançam RangeError (equivalente ao ValueError do Python).
 */
function simularColisao(m1, m2, v1, v2, dtContato) {
  if (!(m1 > 0) || !(m2 > 0)) {
    throw new RangeError('As massas devem ser positivas (em kg).');
  }
  if (!(dtContato > 0)) {
    throw new RangeError('Δt deve ser positivo (em segundos).');
  }

  // O choque só acontece se o bloco 1 alcança o bloco 2 (Seção 2: exige v1 > v2).
  const houveColisao = v1 > v2;

  let u1 = v1;
  let u2 = v2;
  if (houveColisao) {
    const V = colisaoInelastica(m1, m2, v1, v2);
    u1 = V;
    u2 = V;
  }

  const pAntes = momento(m1, v1) + momento(m2, v2);
  const pDepois = momento(m1, u1) + momento(m2, u2);
  const KAntes = cinetica(m1, v1) + cinetica(m2, v2);
  const KDepois = cinetica(m1, u1) + cinetica(m2, u2);

  const dK = KDepois - KAntes;
  const dKFormula = houveColisao ? variacaoEnergiaFormula(m1, m2, v1, v2) : 0;
  const fracao = KAntes > 0 ? Math.abs(dK) / KAntes : 0;

  const J1 = impulso(m1, v1, u1);
  const J2 = impulso(m2, v2, u2);
  // |J1| = |J2| pela 3ª lei de Newton; usamos J1.
  const F = forcaMedia(J1, dtContato);

  return Object.freeze({
    houve_colisao: houveColisao,
    v1: v1,
    v2: v2,
    u1: u1,
    u2: u2,
    p_antes: pAntes,
    p_depois: pDepois,
    K_antes: KAntes,
    K_depois: KDepois,
    dK: dK,
    dK_formula: dKFormula,
    fracao_dissipada: fracao,
    J1: J1,
    J2: J2,
    F_media: F,
    dt_contato: dtContato
  });
}
