/*
 * app.js — Camada 5 (interface web: DOM + canvas).
 * Só lê controles e desenha. Toda conta física vem de simularColisao (fisica.js)
 * e toda posição vem de posicoes (cinematica.js).
 *
 * Depende de: fisica.js, cinematica.js, painel.js (carregados antes, nessa ordem).
 */
'use strict';

(function () {
  /* Duração máxima de uma rodada da animação (s): depois disso ela para sozinha. */
  const T_MAX = 30;

  /* ---------------- Referências do DOM ---------------- */
  const el = function (id) { return document.getElementById(id); };
  const controles = {
    m1: el('m1'), m2: el('m2'), v1: el('v1'), v2: el('v2'), dt: el('dt')
  };
  const saidas = {
    m1: el('m1-valor'), m2: el('m2-valor'), v1: el('v1-valor'),
    v2: el('v2-valor'), dt: el('dt-valor')
  };
  const unidades = { m1: ' kg', m2: ' kg', v1: ' m/s', v2: ' m/s', dt: ' ms' };
  const casas = { m1: 1, m2: 1, v1: 1, v2: 1, dt: 0 };

  const btnPausar = el('btn-pausar');
  const btnReiniciar = el('btn-reiniciar');
  const painel = el('painel');
  const aviso = el('aviso');
  const relogio = el('relogio');
  const fase = el('fase');
  const canvasCena = el('cena');
  const canvasP = el('barras-p');
  const canvasK = el('barras-k');

  /* ---------------- Estado ---------------- */
  let resultado = null;   // ResultadoColisao (objeto congelado)
  let cenario = null;     // posições iniciais, larguras, tc
  let m1 = 2, m2 = 3;
  let t = 0;              // s, tempo simulado
  let rodando = true;
  let terminou = false;   // rodada acabou (blocos fora da pista ou T_MAX)
  let ultimoQuadro = null;
  let cores = {};

  /* ---------------- Cores (tokens CSS do :root) ---------------- */
  function lerCores() {
    const css = getComputedStyle(document.documentElement);
    const v = function (nome) { return css.getPropertyValue(nome).trim(); };
    cores = {
      fundo: v('--cor-superficie'),
      texto: v('--cor-texto'),
      suave: v('--cor-texto-suave'),
      linha: v('--cor-borda'),
      bloco1: v('--cor-bloco1'),
      bloco2: v('--cor-bloco2'),
      antes: v('--cor-antes'),
      depois: v('--cor-depois'),
      alerta: v('--cor-alerta'),
      alertaFundo: v('--cor-alerta-fundo'),
      fonte: v('--fonte-base') || 'system-ui, sans-serif',
      mono: v('--fonte-mono') || 'monospace'
    };
  }

  /* ---------------- Canvas nítido (devicePixelRatio) ---------------- */
  /* Ajusta o buffer ao tamanho exibido × DPR e devolve o contexto em pixels CSS. */
  function prepararCanvas(canvas) {
    const dpr = window.devicePixelRatio || 1;
    const largura = canvas.clientWidth;
    const altura = canvas.clientHeight;
    const bw = Math.max(1, Math.round(largura * dpr));
    const bh = Math.max(1, Math.round(altura * dpr));
    if (canvas.width !== bw || canvas.height !== bh) {
      canvas.width = bw;
      canvas.height = bh;
    }
    const ctx = canvas.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, largura, altura);
    return { ctx: ctx, w: largura, h: altura };
  }

  /* Retângulo com cantos arredondados (fallback para navegadores sem roundRect). */
  function retanguloArredondado(ctx, x, y, w, h, r) {
    r = Math.max(0, Math.min(r, w / 2, h / 2));
    ctx.beginPath();
    if (ctx.roundRect) {
      ctx.roundRect(x, y, w, h, r);
    } else {
      ctx.rect(x, y, w, h);
    }
  }

  /* ---------------- Leitura dos controles + reinício ---------------- */
  function valor(nome) {
    return parseFloat(controles[nome].value);
  }

  function atualizarSaidas() {
    Object.keys(controles).forEach(function (nome) {
      saidas[nome].textContent = formatarNumero(valor(nome), casas[nome]) + unidades[nome];
    });
  }

  /* Monta o painel de resultados como listas de definição (rótulo · valor · unidade). */
  function renderizarPainel(r) {
    painel.textContent = '';
    secoesPainel(r).forEach(function (sec) {
      const grupo = document.createElement('div');
      grupo.className = 'grupo';
      const h3 = document.createElement('h3');
      h3.textContent = sec.titulo;
      const dl = document.createElement('dl');
      sec.linhas.forEach(function (l) {
        const linha = document.createElement('div');
        linha.className = 'linha' + (l[3] ? ' destaque' : '');
        const dt = document.createElement('dt');
        dt.textContent = l[0];
        const dd = document.createElement('dd');
        const num = document.createElement('span');
        num.className = 'num';
        num.textContent = l[1];
        const un = document.createElement('span');
        un.className = 'un';
        un.textContent = ' ' + l[2];
        dd.append(num, un);
        linha.append(dt, dd);
        dl.append(linha);
      });
      grupo.append(h3, dl);
      painel.append(grupo);
    });
  }

  /* Recalcula tudo e zera o tempo (requisito R2: qualquer mudança reinicia). */
  function reiniciar() {
    m1 = valor('m1');
    m2 = valor('m2');
    const v1 = valor('v1');
    const v2 = valor('v2');
    const dtContato = valor('dt') / 1000;   // slider em ms → s

    resultado = simularColisao(m1, m2, v1, v2, dtContato);
    cenario = montarCenario(m1, m2, resultado);
    t = 0;
    ultimoQuadro = null;
    rodando = true;
    terminou = false;
    btnPausar.textContent = 'Pausar';
    btnPausar.setAttribute('aria-pressed', 'false');

    atualizarSaidas();
    renderizarPainel(resultado);
    aviso.hidden = resultado.houve_colisao;
    desenharBarras();
  }

  function alternarPausa() {
    // Se a rodada acabou, o botão recomeça do início.
    if (terminou) {
      reiniciar();
      return;
    }
    rodando = !rodando;
    ultimoQuadro = null;
    btnPausar.textContent = rodando ? 'Pausar' : 'Continuar';
    btnPausar.setAttribute('aria-pressed', rodando ? 'false' : 'true');
  }

  /* ---------------- Cena: pista, régua, blocos e setas de velocidade ---------------- */

  /* Seta horizontal de comprimento proporcional à velocidade (vetor v). */
  function desenharSeta(ctx, x, y, comprimento, cor, texto) {
    const dir = comprimento >= 0 ? 1 : -1;
    const ponta = 7;
    ctx.strokeStyle = cor;
    ctx.fillStyle = cor;
    ctx.lineWidth = 2;
    if (Math.abs(comprimento) > ponta) {
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(x + comprimento - dir * ponta, y);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(x + comprimento, y);
      ctx.lineTo(x + comprimento - dir * ponta, y - 4.5);
      ctx.lineTo(x + comprimento - dir * ponta, y + 4.5);
      ctx.closePath();
      ctx.fill();
    }
    ctx.font = '500 11px ' + cores.mono;
    ctx.textBaseline = 'bottom';
    ctx.textAlign = 'center';
    ctx.fillText(texto, x + comprimento / 2, y - 6);
  }

  function desenharCena() {
    const c = prepararCanvas(canvasCena);
    const ctx = c.ctx;
    const margem = 18;                       // px nas laterais
    const escala = (c.w - 2 * margem) / (PISTA_FIM - PISTA_INICIO);   // px por metro
    const xPx = function (x) { return margem + (x - PISTA_INICIO) * escala; };
    const yChao = c.h - 44;                  // px, linha da pista
    const alturaMax = Math.min(84, yChao - 80);
    const pxPorMs = Math.min(9, escala * 0.45);   // comprimento da seta por m/s

    // Faixa do chão
    ctx.fillStyle = cores.linha;
    ctx.globalAlpha = 0.45;
    ctx.fillRect(xPx(PISTA_INICIO), yChao, xPx(PISTA_FIM) - xPx(PISTA_INICIO), 10);
    ctx.globalAlpha = 1;
    ctx.strokeStyle = cores.texto;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(xPx(PISTA_INICIO), yChao + 0.5);
    ctx.lineTo(xPx(PISTA_FIM), yChao + 0.5);
    ctx.stroke();

    // Régua em metros: traço a cada 1 m, número a cada 2 m (ou 5 m em telas estreitas)
    const passoRotulo = escala < 22 ? 5 : 2;
    ctx.fillStyle = cores.suave;
    ctx.strokeStyle = cores.suave;
    ctx.lineWidth = 1;
    ctx.font = '11px ' + cores.mono;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    for (let x = PISTA_INICIO; x <= PISTA_FIM; x++) {
      const comRotulo = x % passoRotulo === 0;
      const px = Math.round(xPx(x)) + 0.5;
      ctx.beginPath();
      ctx.moveTo(px, yChao + 10);
      ctx.lineTo(px, yChao + (comRotulo ? 18 : 14));
      ctx.stroke();
      if (comRotulo) ctx.fillText(String(x), px, yChao + 21);
    }
    ctx.textAlign = 'right';
    ctx.font = '11px ' + cores.fonte;
    ctx.fillText('x (m)', c.w - margem, yChao + 33);

    // Marca do ponto de contato (onde o choque aconteceu)
    if (resultado.houve_colisao && t >= cenario.tc) {
      const xc = cenario.x1_0 + resultado.v1 * cenario.tc + cenario.w1 / 2;
      ctx.save();
      ctx.setLineDash([3, 4]);
      ctx.strokeStyle = cores.suave;
      ctx.beginPath();
      ctx.moveTo(Math.round(xPx(xc)) + 0.5, 30);
      ctx.lineTo(Math.round(xPx(xc)) + 0.5, yChao);
      ctx.stroke();
      ctx.restore();
      ctx.fillStyle = cores.suave;
      ctx.font = '11px ' + cores.fonte;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      ctx.fillText('choque em tc = ' + formatarNumero(cenario.tc, 2) + ' s', xPx(xc), 14);
    }

    // Blocos: largura ∝ massa (R1); altura também cresce para reforçar o tamanho
    const pos = posicoes(t, cenario);
    const unidos = resultado.houve_colisao && t >= cenario.tc;
    const vAtual = unidos
      ? [resultado.u1, resultado.u2]
      : [resultado.v1, resultado.v2];
    const blocos = [
      { x: pos[0], w: cenario.w1, cor: cores.bloco1, nome: 'm₁' },
      { x: pos[1], w: cenario.w2, cor: cores.bloco2, nome: 'm₂' }
    ];
    const geo = blocos.map(function (b) {
      const largPx = b.w * escala;
      const altPx = alturaMax * (0.5 + 0.5 * b.w / LARGURA_MAX);
      return { esq: xPx(b.x - b.w / 2), largPx: largPx, altPx: altPx, topo: yChao - altPx };
    });

    ctx.save();
    ctx.beginPath();
    ctx.rect(0, 0, c.w, yChao);
    ctx.clip();
    blocos.forEach(function (b, i) {
      const g = geo[i];
      ctx.fillStyle = b.cor;
      retanguloArredondado(ctx, g.esq, g.topo, g.largPx, g.altPx, 4);
      ctx.fill();
      // Nome dentro do bloco, se couber
      if (g.largPx > 22) {
        ctx.fillStyle = '#ffffff';
        ctx.font = '600 12px ' + cores.fonte;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(b.nome, g.esq + g.largPx / 2, g.topo + g.altPx / 2);
      }
    });
    ctx.restore();

    // Setas de velocidade acima dos blocos (uma só quando seguem unidos)
    if (unidos) {
      const esq = Math.min(geo[0].esq, geo[1].esq);
      const dir = Math.max(geo[0].esq + geo[0].largPx, geo[1].esq + geo[1].largPx);
      const topo = Math.min(geo[0].topo, geo[1].topo);
      desenharSeta(ctx, (esq + dir) / 2, topo - 14, vAtual[0] * pxPorMs, cores.texto,
        'V = ' + formatarNumero(vAtual[0], 1) + ' m/s');
    } else {
      blocos.forEach(function (b, i) {
        const g = geo[i];
        desenharSeta(ctx, g.esq + g.largPx / 2, g.topo - 14, vAtual[i] * pxPorMs, b.cor,
          formatarNumero(vAtual[i], 1) + ' m/s');
      });
    }

    // Requisito R5: mensagem na própria cena quando não há colisão
    if (!resultado.houve_colisao) {
      ctx.font = '600 15px ' + cores.fonte;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = cores.alerta;
      ctx.fillText('Sem colisão: v1 ≤ v2', c.w / 2, 20);
    }

    // Estado no cabeçalho
    if (!resultado.houve_colisao) {
      fase.textContent = 'sem choque';
    } else if (t < cenario.tc) {
      fase.textContent = 'antes do choque';
    } else {
      fase.textContent = 'depois do choque: unidos';
    }
    relogio.textContent = 't = ' + formatarNumero(t, 2) + ' s';
  }

  /* ---------------- Barras: antes × depois (aceita negativos) ---------------- */
  /* destacarPerda: desenha a parte perdida (antes − depois) tracejada sobre a barra "depois". */
  function desenharGraficoBarras(canvas, antes, depois, destacarPerda) {
    const c = prepararCanvas(canvas);
    const ctx = c.ctx;
    const topo = 22, base = c.h - 26;       // px: área útil vertical
    const esq = 8, dir = c.w - 8;

    // Faixa do eixo sempre inclui o zero; folga de 15 % acima/abaixo
    let maximo = Math.max(0, antes, depois);
    let minimo = Math.min(0, antes, depois);
    if (maximo - minimo < 1e-9) maximo = 1;   // tudo zero: eixo de 0 a 1
    const folga = 0.15 * (maximo - minimo);
    if (maximo > 0) maximo += folga;
    if (minimo < 0) minimo -= folga;
    const yPx = function (v) {
      return base - (v - minimo) / (maximo - minimo) * (base - topo);
    };
    const y0 = yPx(0);

    // Linhas de grade discretas
    ctx.strokeStyle = cores.linha;
    ctx.lineWidth = 1;
    for (let k = 1; k <= 3; k++) {
      const y = Math.round(topo + (base - topo) * k / 4) + 0.5;
      ctx.beginPath();
      ctx.moveTo(esq, y);
      ctx.lineTo(dir, y);
      ctx.stroke();
    }

    const barras = [
      { rotulo: 'antes', valor: antes, cor: cores.antes },
      { rotulo: 'depois', valor: depois, cor: cores.depois }
    ];
    const larguraFaixa = (dir - esq) / barras.length;
    const largBarra = Math.min(72, larguraFaixa * 0.56);

    barras.forEach(function (b, i) {
      const cx = esq + larguraFaixa * (i + 0.5);
      const y = yPx(b.valor);
      ctx.fillStyle = b.cor;
      retanguloArredondado(ctx, cx - largBarra / 2, Math.min(y, y0), largBarra, Math.abs(y0 - y), 3);
      ctx.fill();

      // Energia dissipada: contorno tracejado de "depois" até o nível de "antes"
      let yRotulo = y;
      if (destacarPerda && i === 1 && antes > depois + 1e-9) {
        const yA = yPx(antes);
        ctx.save();
        ctx.fillStyle = cores.alertaFundo;
        ctx.fillRect(cx - largBarra / 2, yA, largBarra, y - yA);
        ctx.setLineDash([4, 3]);
        ctx.strokeStyle = cores.alerta;
        ctx.lineWidth = 1.5;
        ctx.strokeRect(cx - largBarra / 2 + 0.75, yA + 0.75, largBarra - 1.5, y - yA - 1.5);
        ctx.restore();
        yRotulo = yA;
        if (y - yA > 18) {
          ctx.fillStyle = cores.alerta;
          ctx.font = '600 11px ' + cores.mono;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText('−' + formatarNumero(antes - depois, 1), cx, (y + yA) / 2);
        }
      }

      // Valor: acima da barra se positivo, abaixo se negativo
      ctx.fillStyle = cores.texto;
      ctx.font = '600 12px ' + cores.mono;
      ctx.textAlign = 'center';
      const negativo = b.valor < 0;
      ctx.textBaseline = negativo ? 'top' : 'bottom';
      ctx.fillText(formatarNumero(b.valor, 1), cx, negativo ? y + 4 : yRotulo - 4);

      // Rótulo da categoria embaixo
      ctx.fillStyle = cores.suave;
      ctx.font = '12px ' + cores.fonte;
      ctx.textBaseline = 'top';
      ctx.fillText(b.rotulo, cx, base + 8);
    });

    // Linha do zero
    ctx.strokeStyle = cores.texto;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(esq, Math.round(y0) + 0.5);
    ctx.lineTo(dir, Math.round(y0) + 0.5);
    ctx.stroke();
  }

  function desenharBarras() {
    if (!resultado) return;
    desenharGraficoBarras(canvasP, resultado.p_antes, resultado.p_depois, false);
    desenharGraficoBarras(canvasK, resultado.K_antes, resultado.K_depois, true);
  }

  /* ---------------- Laço da animação (requestAnimationFrame) ---------------- */
  /* A rodada acaba quando os dois blocos saem da pista ou em T_MAX. */
  function blocosForaDaPista() {
    const pos = posicoes(t, cenario);
    const fora = function (x, w) {
      return x + w / 2 < PISTA_INICIO || x - w / 2 > PISTA_FIM;
    };
    return fora(pos[0], cenario.w1) && fora(pos[1], cenario.w2);
  }

  function quadro(agora) {
    if (rodando) {
      if (ultimoQuadro !== null) {
        // limita o passo a 0,1 s para não "pular" ao voltar de outra aba
        t += Math.min(0.1, (agora - ultimoQuadro) / 1000);
      }
      ultimoQuadro = agora;
      if (t >= T_MAX || blocosForaDaPista()) {
        terminou = true;
        rodando = false;
        btnPausar.textContent = 'Recomeçar';
        btnPausar.setAttribute('aria-pressed', 'false');
      }
    }
    desenharCena();
    requestAnimationFrame(quadro);
  }

  /* ---------------- Ligações ---------------- */
  Object.keys(controles).forEach(function (nome) {
    controles[nome].addEventListener('input', reiniciar);
  });
  btnPausar.addEventListener('click', alternarPausa);
  btnReiniciar.addEventListener('click', reiniciar);

  window.addEventListener('resize', desenharBarras);
  const esquemaEscuro = window.matchMedia('(prefers-color-scheme: dark)');
  const aoMudarEsquema = function () { lerCores(); desenharBarras(); };
  if (esquemaEscuro.addEventListener) {
    esquemaEscuro.addEventListener('change', aoMudarEsquema);
  } else if (esquemaEscuro.addListener) {
    esquemaEscuro.addListener(aoMudarEsquema);   // Safari antigo
  }

  lerCores();
  reiniciar();
  requestAnimationFrame(quadro);
})();
