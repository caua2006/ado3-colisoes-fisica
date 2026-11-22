/*
 * cinematica.js — Camada 3 (mesmas funções do programa Python).
 *
 * Antes e depois do choque cada bloco está em MRU: x(t) = x0 + v·t
 * (enunciado, Seção 2). O choque é instantâneo; Δt de contato só entra em Fmed.
 * Posições em metros (centro de cada bloco), tempo em segundos.
 *
 * Depende de: fisica.js (só usa o objeto devolvido por simularColisao).
 */
'use strict';

/* Constantes visuais (metros). */
const LARGURA_POR_KG = 0.25;  // m/kg: largura visual proporcional à massa
const LARGURA_MIN = 0.12;     // m
const LARGURA_MAX = 2.5;      // m
const PISTA_INICIO = 0;       // m (início da régua)
const PISTA_FIM = 20;         // m (fim da régua)
const X1_INICIAL = 6;         // m, centro do bloco 1 em t = 0
const X2_INICIAL = 14;        // m, centro do bloco 2 em t = 0

/**
 * Largura visual do bloco, proporcional à massa, limitada a [mín, máx].
 * w = clamp(0,25·m, 0,12, 2,5)   [m]  (mesmas constantes do Python)
 * Requisito R1: "tamanho visual dependente da massa".
 */
function larguraBloco(m) {
  return Math.min(LARGURA_MAX, Math.max(LARGURA_MIN, LARGURA_POR_KG * m));
}

/**
 * Instante do choque (fórmula fechada).
 * O choque ocorre quando a distância entre os centros vale a soma das
 * meias-larguras (enunciado, Seção 2):
 *   x2_0 + v2·tc − (x1_0 + v1·tc) = (w1 + w2)/2
 *   tc = (x2_0 − x1_0 − (w1 + w2)/2) / (v1 − v2)   [s]
 * Devolve null se v1 <= v2 (os blocos não se alcançam). Se já começassem
 * encostados, tc seria <= 0; nesse caso devolve 0 (igual ao Python).
 */
function instanteColisao(x1_0, x2_0, w1, w2, v1, v2) {
  if (!(v1 > v2)) {
    return null;
  }
  return Math.max(0, (x2_0 - x1_0 - (w1 + w2) / 2) / (v1 - v2));
}

/**
 * Junta tudo o que a animação precisa: posições iniciais, larguras, tc e o resultado.
 * (No Python é o "cenario" recebido por posicoes.)
 */
function montarCenario(m1, m2, resultado) {
  const w1 = larguraBloco(m1);
  const w2 = larguraBloco(m2);
  const tc = resultado.houve_colisao
    ? instanteColisao(X1_INICIAL, X2_INICIAL, w1, w2, resultado.v1, resultado.v2)
    : null;
  return Object.freeze({
    x1_0: X1_INICIAL,
    x2_0: X2_INICIAL,
    w1: w1,
    w2: w2,
    tc: tc,
    resultado: resultado
  });
}

/**
 * Posições dos centros no instante t   [m]
 *   t < tc:  x = x0 + v·t                      (MRU antes)
 *   t >= tc: x = x(tc) + V·(t − tc)            (MRU depois, blocos unidos)
 * Sem colisão (tc = null): MRU com v1 e v2 o tempo todo.
 * Devolve [x1, x2].
 */
function posicoes(t, cenario) {
  const r = cenario.resultado;
  const tc = cenario.tc;
  if (tc === null || t < tc) {
    return [cenario.x1_0 + r.v1 * t, cenario.x2_0 + r.v2 * t];
  }
  const x1c = cenario.x1_0 + r.v1 * tc;
  const x2c = cenario.x2_0 + r.v2 * tc;
  const dt = t - tc;
  return [x1c + r.u1 * dt, x2c + r.u2 * dt];
}
