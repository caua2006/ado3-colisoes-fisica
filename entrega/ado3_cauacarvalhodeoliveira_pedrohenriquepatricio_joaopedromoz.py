"""
ADO-3 — Colisões, Impulso e Conservação do Momento Linear
Disciplina: Física: Práticas Extensivas
Professor: Prof. Ettore Baldini-Neto
Grupo: Cauã Carvalho de Oliveira, Pedro Henrique Patrício, João Pedro Moz
Opção escolhida: B — colisão perfeitamente inelástica (os blocos seguem unidos)

Como rodar:
    python ado3_cauacarvalhodeoliveira_pedrohenriquepatricio_joaopedromoz.py
Bibliotecas: matplotlib e numpy (somente).

Organização (cada camada só usa as camadas abaixo dela):
    1. Fórmulas puras (Seção 2 do enunciado), uma função por fórmula
    2. Cenário: simular_colisao(...) -> ResultadoColisao
    3. Cinemática: larguras, instante do choque tc, posições x(t) em MRU
    4. Apresentação: formatar_painel(resultado) -> texto do painel
    5. Interface matplotlib: classe AppColisao (animação, sliders, botões, barras)

Importar este arquivo não abre janela nem cria figura: a interface só é
construída dentro de `if __name__ == "__main__"`.
Todas as grandezas estão em unidades do SI (kg, m, s, m/s, kg·m/s, J, N·s, N).
"""

from __future__ import annotations

from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle
from matplotlib.widgets import Button, Slider

# =============================================================================
# 2. Constantes
# =============================================================================

# Valores padrão sugeridos na Opção B do enunciado (Seção 3)
M1_PADRAO = 2.0       # kg
M2_PADRAO = 3.0       # kg
V1_PADRAO = 5.0       # m/s
V2_PADRAO = 0.0       # m/s
DT_MS_PADRAO = 10.0   # ms (duração do contato, Q4)

# Faixas dos sliders (R2)
MASSA_MIN, MASSA_MAX, MASSA_PASSO = 0.5, 10.0, 0.1          # kg
VELOC_MIN, VELOC_MAX, VELOC_PASSO = -10.0, 10.0, 0.1        # m/s
DT_MS_MIN, DT_MS_MAX, DT_MS_PASSO = 1.0, 200.0, 1.0         # ms

# Pista da animação (eixo x em metros)
X_MIN, X_MAX = 0.0, 20.0        # m, limites visíveis da pista
X1_INICIAL = 6.0                # m, centro inicial do bloco 1
X2_INICIAL = 14.0               # m, centro inicial do bloco 2
ALTURA_BLOCO = 1.0              # m, altura visual (fixa)

# Largura visual proporcional à massa: w = LARGURA_POR_KG·m, limitada a [W_MIN, W_MAX].
# Na faixa dos sliders (0,5–10 kg) a largura é exatamente proporcional (0,125–2,5 m).
LARGURA_POR_KG = 0.25           # m/kg
LARGURA_MIN = 0.12              # m
LARGURA_MAX = 2.5               # m
# Garantia de que os blocos começam separados para quaisquer massas:
# a soma das meias-larguras é no máximo LARGURA_MAX (= 2·LARGURA_MAX/2) < X2_INICIAL − X1_INICIAL.
assert X2_INICIAL - X1_INICIAL > LARGURA_MAX

# Animação
INTERVALO_MS = 30                   # ms entre quadros
DT_QUADRO = INTERVALO_MS / 1000.0   # s de tempo simulado por quadro (tempo real)
ESPERA_FIM_S = 1.0                  # s parado depois que um bloco sai da tela, antes de recomeçar
TEMPO_APOS_CHOQUE_S = 8.0           # s após tc (ou após t = 0, sem choque) até recomeçar


# =============================================================================
# 3. Camada 1 — Fórmulas puras (Seção 2 do enunciado)
# =============================================================================

def momento(m: float, v: float) -> float:
    """Momento linear de um corpo: p = m·v.

    Unidades: m em kg, v em m/s -> p em kg·m/s.
    Fonte: enunciado, Seção 2 ("Momento linear total: p = m1v1 + m2v2").
    """
    return m * v


def cinetica(m: float, v: float) -> float:
    """Energia cinética de um corpo: K = ½·m·v².

    Unidades: m em kg, v em m/s -> K em J.
    Fonte: enunciado, Seção 2 ("Energia cinética total: K = ½m1v1² + ½m2v2²").
    """
    return 0.5 * m * v ** 2


def massa_reduzida(m1: float, m2: float) -> float:
    """Massa reduzida do par: μ = m1·m2 / (m1 + m2).

    Unidades: kg -> kg.
    Fonte: enunciado, Seção 2, quadro da colisão perfeitamente inelástica.
    """
    return m1 * m2 / (m1 + m2)


def colisao_inelastica(m1: float, m2: float, v1: float, v2: float) -> float:
    """Velocidade comum após a colisão perfeitamente inelástica: V = (m1v1 + m2v2)/(m1 + m2).

    Unidades: massas em kg, velocidades em m/s -> V em m/s.
    Fonte: enunciado, Seção 2, quadro da colisão perfeitamente inelástica
    (conservação do momento com u1 = u2 = V).
    """
    return (m1 * v1 + m2 * v2) / (m1 + m2)


def variacao_energia_formula(m1: float, m2: float, v1: float, v2: float) -> float:
    """Variação de energia cinética na colisão perfeitamente inelástica:
    ΔK = K_depois − K_antes = −½·μ·(v1 − v2)².

    Unidades: massas em kg, velocidades em m/s -> ΔK em J (sempre ≤ 0).
    Fonte: enunciado, Seção 2, quadro da colisão perfeitamente inelástica.
    """
    return -0.5 * massa_reduzida(m1, m2) * (v1 - v2) ** 2


def impulso(m: float, v_antes: float, v_depois: float) -> float:
    """Impulso sobre um corpo (teorema do impulso–momento): J = m·(u − v).

    Unidades: m em kg, velocidades em m/s -> J em N·s (= kg·m/s).
    Fonte: enunciado, Seção 2 ("J1 = m1(u1 − v1) e J2 = m2(u2 − v2)").
    """
    return m * (v_depois - v_antes)


def forca_media(J: float, dt: float) -> float:
    """Força média durante o contato: Fmed = |J| / Δt.

    Unidades: J em N·s, Δt em s -> Fmed em N.
    Fonte: enunciado, Seção 2 ("Se o contato dura Δt, a força média é Fmed = |J|/Δt").
    Levanta ValueError se Δt ≤ 0.
    """
    if dt <= 0:
        raise ValueError("A duração do contato Δt deve ser positiva (s).")
    return abs(J) / dt


# =============================================================================
# 4. Camada 2 — Cenário: simular_colisao -> ResultadoColisao
# =============================================================================

@dataclass(frozen=True)
class ResultadoColisao:
    """Tudo o que o painel, as barras e o relatório precisam (unidades SI)."""

    houve_colisao: bool      # False se v1 <= v2 (R5)
    v1: float                # m/s, velocidade do bloco 1 antes
    v2: float                # m/s, velocidade do bloco 2 antes
    u1: float                # m/s, velocidade do bloco 1 depois (= V se houve colisão)
    u2: float                # m/s, velocidade do bloco 2 depois (= V se houve colisão)
    p_antes: float           # kg·m/s
    p_depois: float          # kg·m/s
    K_antes: float           # J
    K_depois: float          # J
    dK: float                # J, medido: K_depois − K_antes
    dK_formula: float        # J, pela fórmula −½·μ·(v1 − v2)²
    fracao_dissipada: float  # adimensional, |dK| / K_antes (0 se K_antes = 0)
    J1: float                # N·s, impulso sobre o bloco 1
    J2: float                # N·s, impulso sobre o bloco 2
    F_media: float           # N, |J| / Δt
    dt_contato: float        # s (o slider está em ms; a conversão é feita na interface)


def simular_colisao(m1: float, m2: float, v1: float, v2: float,
                    dt_contato: float) -> ResultadoColisao:
    """Resolve a colisão frontal perfeitamente inelástica em fórmula fechada.

    Entradas: m1, m2 em kg; v1, v2 em m/s (positivo para a direita); dt_contato em s.
    Há choque só se v1 > v2 (o bloco 1, à esquerda, alcança o bloco 2).
    Sem colisão (v1 <= v2): u1 = v1, u2 = v2, J = 0, Fmed = 0, houve_colisao = False.
    Levanta ValueError se alguma massa ou Δt for ≤ 0.
    """
    if m1 <= 0 or m2 <= 0:
        raise ValueError("As massas devem ser positivas (kg).")
    if dt_contato <= 0:
        raise ValueError("A duração do contato Δt deve ser positiva (s).")

    houve_colisao = v1 > v2
    if houve_colisao:
        V = colisao_inelastica(m1, m2, v1, v2)
        u1 = u2 = V
        dK_formula = variacao_energia_formula(m1, m2, v1, v2)
    else:
        u1, u2 = v1, v2
        dK_formula = 0.0

    # Momento e energia totais: p = m1v1 + m2v2, K = ½m1v1² + ½m2v2² (Seção 2)
    p_antes = momento(m1, v1) + momento(m2, v2)
    p_depois = momento(m1, u1) + momento(m2, u2)
    K_antes = cinetica(m1, v1) + cinetica(m2, v2)
    K_depois = cinetica(m1, u1) + cinetica(m2, u2)
    dK = K_depois - K_antes
    fracao = abs(dK) / K_antes if K_antes > 0 else 0.0

    # Impulsos (teorema do impulso–momento) e força média
    J1 = impulso(m1, v1, u1)
    J2 = impulso(m2, v2, u2)
    F_media = forca_media(J1, dt_contato)

    return ResultadoColisao(
        houve_colisao=houve_colisao,
        v1=v1, v2=v2, u1=u1, u2=u2,
        p_antes=p_antes, p_depois=p_depois,
        K_antes=K_antes, K_depois=K_depois,
        dK=dK, dK_formula=dK_formula,
        fracao_dissipada=fracao,
        J1=J1, J2=J2, F_media=F_media,
        dt_contato=dt_contato,
    )


# =============================================================================
# 5. Camada 3 — Cinemática (MRU antes e depois do choque)
# =============================================================================

def largura_bloco(m: float) -> float:
    """Largura visual do bloco, proporcional à massa: w = LARGURA_POR_KG·m (m/kg · kg = m),
    limitada a [LARGURA_MIN, LARGURA_MAX]. Atende ao R1 (tamanho dependente da massa).
    """
    return float(np.clip(LARGURA_POR_KG * m, LARGURA_MIN, LARGURA_MAX))


def instante_colisao(x1_0: float, x2_0: float, w1: float, w2: float,
                     v1: float, v2: float) -> float | None:
    """Instante do choque em fórmula fechada (Seção 2: distância entre os centros
    igual à soma das meias-larguras):

        x2_0 + v2·tc − (x1_0 + v1·tc) = (w1 + w2)/2
        tc = (x2_0 − x1_0 − (w1 + w2)/2) / (v1 − v2)

    Unidades: posições e larguras em m, velocidades em m/s -> tc em s.
    Supõe o bloco 1 à esquerda (x1_0 < x2_0). Retorna None se v1 <= v2 (não há choque).
    Se os blocos já começassem encostados, tc seria ≤ 0; nesse caso retorna 0.
    """
    if v1 <= v2:
        return None
    tc = (x2_0 - x1_0 - (w1 + w2) / 2.0) / (v1 - v2)
    return max(tc, 0.0)


@dataclass(frozen=True)
class Cenario:
    """Dados da animação: posições iniciais (m), larguras (m), tc (s) e o resultado físico."""

    x1_0: float
    x2_0: float
    w1: float
    w2: float
    tc: float | None
    resultado: ResultadoColisao


def montar_cenario(m1: float, m2: float, resultado: ResultadoColisao,
                   x1_0: float = X1_INICIAL, x2_0: float = X2_INICIAL) -> Cenario:
    """Junta posições iniciais, larguras e tc para a animação.

    Os centros iniciais (6 m e 14 m) estão a 8 m um do outro, mais que a soma máxima
    das meias-larguras (2,5 m), então os blocos sempre começam separados.
    """
    w1 = largura_bloco(m1)
    w2 = largura_bloco(m2)
    tc = instante_colisao(x1_0, x2_0, w1, w2, resultado.v1, resultado.v2)
    return Cenario(x1_0=x1_0, x2_0=x2_0, w1=w1, w2=w2, tc=tc, resultado=resultado)


def posicoes(t: float, cenario: Cenario) -> tuple[float, float]:
    """Centros dos blocos no instante t (s), em MRU (Seção 2: x(t) = x0 + v·t):

        t < tc:  x = x0 + v·t
        t >= tc: x = x(tc) + V·(t − tc)     (u1 = u2 = V: seguem unidos)

    Sem colisão (tc = None), cada bloco segue em MRU com a própria velocidade.
    O Δt de contato não altera a animação (choque tratado como instantâneo).
    """
    r = cenario.resultado
    if cenario.tc is None or t < cenario.tc:
        return cenario.x1_0 + r.v1 * t, cenario.x2_0 + r.v2 * t
    tc = cenario.tc
    x1c = cenario.x1_0 + r.v1 * tc
    x2c = cenario.x2_0 + r.v2 * tc
    return x1c + r.u1 * (t - tc), x2c + r.u2 * (t - tc)


def bloco_fora_da_pista(x: float, w: float) -> bool:
    """True se o bloco de centro x (m) e largura w (m) saiu inteiro de [X_MIN, X_MAX]."""
    return x + w / 2.0 < X_MIN or x - w / 2.0 > X_MAX


# =============================================================================
# 6. Camada 4 — Apresentação (texto puro do painel, R3)
# =============================================================================

def _fmt(valor: float, casas: int = 2, sinal: bool = False) -> str:
    """Número com vírgula decimal (padrão brasileiro), sem '-0,00'."""
    if abs(valor) < 0.5 * 10 ** (-casas):
        valor = 0.0
    texto = f"{valor:+.{casas}f}" if sinal else f"{valor:.{casas}f}"
    return texto.replace(".", ",")


def formatar_painel(resultado: ResultadoColisao) -> str:
    """Monta o texto do painel de resultados (R3) a partir do ResultadoColisao."""
    r = resultado
    linhas = []
    if r.houve_colisao:
        linhas.append("Colisão perfeitamente inelástica")
    else:
        linhas.append("Sem colisão: v1 ≤ v2")
    linhas += [
        "",
        "Velocidades antes:",
        f"  v1 = {_fmt(r.v1)} m/s",
        f"  v2 = {_fmt(r.v2)} m/s",
        "Velocidades depois:",
    ]
    if r.houve_colisao:
        linhas.append(f"  u1 = u2 = V = {_fmt(r.u1)} m/s")
    else:
        linhas += [f"  u1 = {_fmt(r.u1)} m/s", f"  u2 = {_fmt(r.u2)} m/s"]
    linhas += [
        "",
        "Momento linear total:",
        f"  p antes  = {_fmt(r.p_antes)} kg·m/s",
        f"  p depois = {_fmt(r.p_depois)} kg·m/s",
        "",
        "Energia cinética total:",
        f"  K antes  = {_fmt(r.K_antes)} J",
        f"  K depois = {_fmt(r.K_depois)} J",
        f"  ΔK medido    = {_fmt(r.dK)} J",
        f"  ΔK pela fórmula −½ μ (v1 − v2)² = {_fmt(r.dK_formula)} J",
        f"  Fração dissipada |ΔK| / K antes = {_fmt(100.0 * r.fracao_dissipada, 1)} %",
        "",
        "Impulsos e força média:",
        f"  J1 = {_fmt(r.J1, sinal=True)} N·s",
        f"  J2 = {_fmt(r.J2, sinal=True)} N·s",
        f"  Δt = {_fmt(r.dt_contato * 1000.0, 0)} ms",
        f"  Fmed = |J|/Δt = {_fmt(r.F_media)} N",
    ]
    return "\n".join(linhas)


# =============================================================================
# 7. Camada 5 — Interface matplotlib (só desenha e lê controles)
# =============================================================================

class AppColisao:
    """Janela com animação (R1), sliders e botões (R2), painel (R3),
    barras de p e K (R4) e aviso de "sem colisão" (R5).

    A interface não faz conta física: lê tudo do ResultadoColisao e do Cenario.
    Referências da animação e dos widgets ficam em atributos para o garbage
    collector não apagá-los.
    """

    # Paleta (a mesma da versão web, docs/estilo.css)
    COR_FUNDO = "#f6f5f1"
    COR_SUPERFICIE = "#ffffff"
    COR_TEXTO = "#1b1f23"
    COR_SUAVE = "#5b636b"
    COR_BORDA = "#e1e3e5"
    COR_DESTAQUE = "#1f4f8a"
    COR_BLOCO1 = "#2f6db5"
    COR_BLOCO2 = "#c8642b"
    COR_ANTES = "#a3abb3"
    COR_DEPOIS = "#1f4f8a"
    COR_ALERTA = "#b3261e"
    COR_ALERTA_FUNDO = "#fbeceb"

    ESCALA_SETA = 0.35   # m de seta por m/s de velocidade (só visual)

    def __init__(self) -> None:
        plt.rcParams.update({
            "font.size": 10,
            "text.color": self.COR_TEXTO,
            "axes.edgecolor": self.COR_BORDA,
            "axes.labelcolor": self.COR_SUAVE,
            "xtick.color": self.COR_SUAVE,
            "ytick.color": self.COR_SUAVE,
        })
        self.fig = plt.figure(figsize=(13, 8), facecolor=self.COR_FUNDO)
        if self.fig.canvas.manager is not None:   # None em backends sem janela
            self.fig.canvas.manager.set_window_title(
                "ADO-3 — Colisão perfeitamente inelástica")
        self.t = 0.0                 # s, tempo simulado
        self.pausado = False
        self._espera_fim = 0.0       # s restantes de espera após um bloco sair da tela
        self._textos_painel = []     # textos do painel, recriados a cada reinício

        self._criar_cabecalho()
        self._criar_eixo_animacao()
        self._criar_barras()
        self._criar_painel()
        self._criar_widgets()

        self.reiniciar()
        self.anim = FuncAnimation(self.fig, self._atualizar_quadro,
                                  interval=INTERVALO_MS, blit=False,
                                  cache_frame_data=False)

    # ---------- construção da figura ----------

    def _estilizar_eixo(self, ax) -> None:
        """Fundo branco e só o eixo de baixo visível."""
        ax.set_facecolor(self.COR_SUPERFICIE)
        for lado in ("top", "right", "left"):
            ax.spines[lado].set_visible(False)
        ax.spines["bottom"].set_color(self.COR_BORDA)
        ax.tick_params(length=3)

    def _criar_cabecalho(self) -> None:
        self.fig.text(0.04, 0.955, "Colisão perfeitamente inelástica",
                      fontsize=17, fontweight="bold", va="center")
        self.fig.text(0.04, 0.922,
                      "ADO-3 · Física: Práticas Extensivas · Prof. Ettore Baldini-Neto  —  "
                      "Cauã Carvalho de Oliveira, Pedro Henrique Patrício, João Pedro Moz",
                      fontsize=9, color=self.COR_SUAVE, va="center")

    def _criar_eixo_animacao(self) -> None:
        ax = self.fig.add_axes([0.04, 0.58, 0.62, 0.30])
        self._estilizar_eixo(ax)
        ax.set_xlim(X_MIN, X_MAX)
        ax.set_ylim(-0.5, 2.9)
        ax.set_xticks(np.arange(X_MIN, X_MAX + 0.1, 2.0))
        ax.set_xlabel("x (m)", loc="right")
        ax.set_yticks([])
        ax.axhspan(-0.12, 0.0, color=self.COR_BORDA, zorder=1)     # faixa do chão
        ax.axhline(0.0, color=self.COR_TEXTO, linewidth=1.4, zorder=2)
        self.ax_anim = ax

        # Blocos (largura e altura dependem da massa)
        self.ret1 = Rectangle((0.0, 0.0), 1.0, ALTURA_BLOCO, facecolor=self.COR_BLOCO1,
                              edgecolor="white", linewidth=1.0, zorder=4)
        self.ret2 = Rectangle((0.0, 0.0), 1.0, ALTURA_BLOCO, facecolor=self.COR_BLOCO2,
                              edgecolor="white", linewidth=1.0, zorder=4)
        ax.add_patch(self.ret1)
        ax.add_patch(self.ret2)
        estilo_nome = dict(ha="center", va="center", color="white",
                           fontsize=10, fontweight="bold", zorder=5)
        self.rot1 = ax.text(0.0, 0.0, "m₁", **estilo_nome)
        self.rot2 = ax.text(0.0, 0.0, "m₂", **estilo_nome)

        # Setas de velocidade (comprimento ∝ v) e seus rótulos
        self.setas = []
        self.rotulos_seta = []
        for cor in (self.COR_BLOCO1, self.COR_BLOCO2):
            seta = ax.annotate("", xy=(0, 0), xytext=(0, 0), zorder=6,
                               arrowprops=dict(arrowstyle="-|>", color=cor, lw=2,
                                               shrinkA=0, shrinkB=0, mutation_scale=14))
            self.setas.append(seta)
            self.rotulos_seta.append(ax.text(0, 0, "", ha="center", va="bottom",
                                             fontsize=9, color=cor, family="monospace",
                                             zorder=6))

        # Marca do ponto de contato (aparece depois do choque)
        self.linha_choque = ax.axvline(0.0, color=self.COR_SUAVE, linestyle=(0, (3, 4)),
                                       linewidth=1, zorder=3, visible=False)
        self.txt_choque = ax.text(0.0, 2.4, "", ha="center", va="top", fontsize=9,
                                  color=self.COR_SUAVE)

        self.txt_tempo = ax.text(0.01, 0.97, "", transform=ax.transAxes, ha="left",
                                 va="top", fontsize=9, color=self.COR_SUAVE,
                                 family="monospace")
        self.txt_estado = ax.text(0.99, 0.97, "", transform=ax.transAxes, ha="right",
                                  va="top", fontsize=9, color=self.COR_SUAVE)
        # Mensagem do R5 (vazia quando há colisão)
        self.txt_aviso = ax.text(0.5, 0.80, "", transform=ax.transAxes, ha="center",
                                 va="center", fontsize=13, color=self.COR_ALERTA,
                                 fontweight="bold",
                                 bbox=dict(boxstyle="round,pad=0.5",
                                           facecolor=self.COR_ALERTA_FUNDO,
                                           edgecolor="none"))

    def _criar_barras(self) -> None:
        self.ax_p = self.fig.add_axes([0.05, 0.30, 0.26, 0.19])
        self.ax_K = self.fig.add_axes([0.40, 0.30, 0.26, 0.19])
        cores = [self.COR_ANTES, self.COR_DEPOIS]
        nomes = ["antes", "depois"]

        for ax, titulo in ((self.ax_p, "Momento linear total p (kg·m/s)"),
                           (self.ax_K, "Energia cinética total K (J)")):
            self._estilizar_eixo(ax)
            ax.spines["left"].set_visible(True)
            ax.spines["left"].set_color(self.COR_BORDA)
            ax.set_title(titulo, fontsize=10, loc="left", color=self.COR_TEXTO, pad=10)
            ax.grid(axis="y", color=self.COR_BORDA, linewidth=0.8)
            ax.set_axisbelow(True)

        self.barras_p = self.ax_p.bar(nomes, [0.0, 0.0], color=cores, width=0.55)
        self.ax_p.axhline(0.0, color=self.COR_TEXTO, linewidth=0.8)
        self.rotulos_p = [self.ax_p.text(b.get_x() + b.get_width() / 2, 0.0, "",
                                         ha="center", fontsize=9, fontweight="bold")
                          for b in self.barras_p]

        self.barras_K = self.ax_K.bar(nomes, [0.0, 0.0], color=cores, width=0.55)
        self.rotulos_K = [self.ax_K.text(b.get_x() + b.get_width() / 2, 0.0, "",
                                         ha="center", fontsize=9, fontweight="bold")
                          for b in self.barras_K]
        # Energia dissipada: retângulo tracejado de K depois até K antes
        b = self.barras_K[1]
        self.ret_perda = Rectangle((b.get_x(), 0.0), b.get_width(), 0.0,
                                   facecolor=self.COR_ALERTA_FUNDO,
                                   edgecolor=self.COR_ALERTA, linestyle="--",
                                   linewidth=1.2, zorder=3)
        self.ax_K.add_patch(self.ret_perda)
        self.txt_perda = self.ax_K.text(b.get_x() + b.get_width() / 2, 0.0, "",
                                        ha="center", va="center", fontsize=9,
                                        color=self.COR_ALERTA, fontweight="bold", zorder=4)

    def _criar_painel(self) -> None:
        ax = self.fig.add_axes([0.70, 0.25, 0.27, 0.66])
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_facecolor(self.COR_SUPERFICIE)
        for spine in ax.spines.values():
            spine.set_color(self.COR_BORDA)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        self.ax_painel = ax

    def _criar_widgets(self) -> None:
        def eixo(y: float):
            ax = self.fig.add_axes([0.13, y, 0.47, 0.022], facecolor=self.COR_FUNDO)
            return ax

        def slider(y, rotulo, vmin, vmax, vinit, passo, cor):
            s = Slider(eixo(y), rotulo, vmin, vmax, valinit=vinit, valstep=passo,
                       color=cor, track_color=self.COR_BORDA, initcolor="none",
                       handle_style={"facecolor": "white", "edgecolor": cor, "size": 12})
            s.label.set_color(self.COR_TEXTO)
            s.valtext.set_family("monospace")
            return s

        self.slider_m1 = slider(0.19, "m₁ (kg)", MASSA_MIN, MASSA_MAX, M1_PADRAO,
                                MASSA_PASSO, self.COR_BLOCO1)
        self.slider_m2 = slider(0.155, "m₂ (kg)", MASSA_MIN, MASSA_MAX, M2_PADRAO,
                                MASSA_PASSO, self.COR_BLOCO2)
        self.slider_v1 = slider(0.12, "v₁ (m/s)", VELOC_MIN, VELOC_MAX, V1_PADRAO,
                                VELOC_PASSO, self.COR_BLOCO1)
        self.slider_v2 = slider(0.085, "v₂ (m/s)", VELOC_MIN, VELOC_MAX, V2_PADRAO,
                                VELOC_PASSO, self.COR_BLOCO2)
        self.slider_dt = slider(0.05, "Δt contato (ms)", DT_MS_MIN, DT_MS_MAX,
                                DT_MS_PADRAO, DT_MS_PASSO, self.COR_SUAVE)
        # (slider, casas decimais do valor exibido)
        self.sliders = [(self.slider_m1, 1), (self.slider_m2, 1), (self.slider_v1, 1),
                        (self.slider_v2, 1), (self.slider_dt, 0)]
        for s, _casas in self.sliders:
            s.on_changed(self._ao_mudar_slider)   # qualquer slider reinicia (R2)

        ax_pausa = self.fig.add_axes([0.70, 0.07, 0.13, 0.065])
        ax_rein = self.fig.add_axes([0.84, 0.07, 0.13, 0.065])
        self.btn_pausa = Button(ax_pausa, "Pausar", color=self.COR_DESTAQUE,
                                hovercolor="#2a62a8")
        self.btn_reiniciar = Button(ax_rein, "Reiniciar", color=self.COR_SUPERFICIE,
                                    hovercolor="#e8eef6")
        self.btn_pausa.label.set_color("white")
        self.btn_reiniciar.label.set_color(self.COR_DESTAQUE)
        for ax, cor in ((ax_pausa, self.COR_DESTAQUE), (ax_rein, self.COR_DESTAQUE)):
            for spine in ax.spines.values():
                spine.set_color(cor)
        for btn in (self.btn_pausa, self.btn_reiniciar):
            btn.label.set_fontweight("bold")
        self.btn_pausa.on_clicked(self._alternar_pausa)
        self.btn_reiniciar.on_clicked(lambda _evento: self.reiniciar())

    # ---------- controle ----------

    def _ler_controles(self) -> tuple[float, float, float, float, float]:
        """Valores dos sliders (arredondados para tirar ruído do valstep). Δt sai em s."""
        m1 = round(float(self.slider_m1.val), 3)
        m2 = round(float(self.slider_m2.val), 3)
        v1 = round(float(self.slider_v1.val), 3)
        v2 = round(float(self.slider_v2.val), 3)
        dt_s = round(float(self.slider_dt.val), 3) / 1000.0   # ms -> s
        return m1, m2, v1, v2, dt_s

    def _atualizar_valores_sliders(self) -> None:
        """Mostra o valor de cada slider com vírgula decimal (padrão brasileiro)."""
        for s, casas in self.sliders:
            s.valtext.set_text(_fmt(float(s.val), casas))

    def reiniciar(self) -> None:
        """Recalcula a física com os valores dos sliders e volta para t = 0."""
        m1, m2, v1, v2, dt_s = self._ler_controles()
        self.resultado = simular_colisao(m1, m2, v1, v2, dt_s)
        self.cenario = montar_cenario(m1, m2, self.resultado)
        self.t = 0.0
        self._espera_fim = 0.0
        self.pausado = False
        self.btn_pausa.label.set_text("Pausar")

        r = self.resultado
        c = self.cenario
        self._atualizar_valores_sliders()
        self._desenhar_painel(formatar_painel(r))
        self.txt_aviso.set_text("" if r.houve_colisao else "Sem colisão: v1 ≤ v2")
        self.txt_aviso.set_visible(not r.houve_colisao)

        # Tamanho visual dos blocos: largura ∝ massa (camada 3); altura acompanha
        self.alt1 = ALTURA_BLOCO * (0.55 + 0.45 * c.w1 / LARGURA_MAX)
        self.alt2 = ALTURA_BLOCO * (0.55 + 0.45 * c.w2 / LARGURA_MAX)
        self.ret1.set_width(c.w1)
        self.ret1.set_height(self.alt1)
        self.ret2.set_width(c.w2)
        self.ret2.set_height(self.alt2)
        self.rot1.set_visible(c.w1 >= 0.45)
        self.rot2.set_visible(c.w2 >= 0.45)

        # Marca do choque: x do ponto de contato (face direita do bloco 1 em tc)
        if c.tc is not None:
            x_contato = c.x1_0 + r.v1 * c.tc + c.w1 / 2.0
            self.linha_choque.set_xdata([x_contato, x_contato])
            self.txt_choque.set_x(x_contato)
            self.txt_choque.set_text(f"choque em tc = {_fmt(c.tc)} s")

        self._atualizar_barras(self.ax_p, self.barras_p, self.rotulos_p,
                               [r.p_antes, r.p_depois], simetrico=True)
        self._atualizar_barras(self.ax_K, self.barras_K, self.rotulos_K,
                               [r.K_antes, r.K_depois], simetrico=False)
        self._atualizar_perda(r)
        self._desenhar_blocos()
        self.fig.canvas.draw_idle()

    def _ao_mudar_slider(self, _valor: float) -> None:
        self.reiniciar()

    def _alternar_pausa(self, _evento) -> None:
        self.pausado = not self.pausado
        self.btn_pausa.label.set_text("Continuar" if self.pausado else "Pausar")
        self.fig.canvas.draw_idle()

    # ---------- desenho ----------

    def _desenhar_painel(self, texto: str) -> None:
        """Desenha o texto da camada 4 em duas colunas: rótulo à esquerda, valor à direita.

        Linhas sem recuo são títulos de seção; linhas recuadas são "rótulo = valor".
        """
        for t in self._textos_painel:
            t.remove()
        self._textos_painel = []
        ax = self.ax_painel
        y, passo = 0.955, 0.037
        for i, linha in enumerate(texto.split("\n")):
            if not linha.strip():
                y -= passo * 0.6
                continue
            if i == 0:   # título do painel (vermelho quando não há colisão)
                cor = self.COR_TEXTO if self.resultado.houve_colisao else self.COR_ALERTA
                self._textos_painel.append(ax.text(0.06, y, linha, fontsize=11.5,
                                                   fontweight="bold", color=cor, va="center"))
            elif not linha.startswith(" "):   # título de seção
                self._textos_painel.append(ax.text(0.06, y, linha.rstrip(":"), fontsize=9,
                                                   color=self.COR_SUAVE, va="center",
                                                   fontweight="bold"))
            else:
                rotulo, _, valor = linha.strip().rpartition(" = ")
                self._textos_painel.append(ax.text(0.09, y, rotulo, fontsize=9.5,
                                                   va="center"))
                self._textos_painel.append(ax.text(0.94, y, valor, fontsize=9.5,
                                                   va="center", ha="right",
                                                   family="monospace"))
            y -= passo

    def _atualizar_barras(self, ax, barras, rotulos, valores, simetrico: bool) -> None:
        """Atualiza alturas e rótulos das barras; p pode ser negativo (eixo simétrico)."""
        for barra, rotulo, valor in zip(barras, rotulos, valores):
            barra.set_height(valor)
            rotulo.set_position((barra.get_x() + barra.get_width() / 2, valor))
            rotulo.set_text(_fmt(valor))
            rotulo.set_va("bottom" if valor >= 0 else "top")
        maximo = max(abs(v) for v in valores)
        limite = 1.3 * maximo if maximo > 0 else 1.0
        if simetrico:
            ax.set_ylim(-limite, limite)
        else:
            ax.set_ylim(0.0, limite)

    def _atualizar_perda(self, r: ResultadoColisao) -> None:
        """Mostra a energia dissipada (K antes − K depois) tracejada sobre a barra 'depois'."""
        perda = r.K_antes - r.K_depois
        visivel = perda > 1e-9
        self.ret_perda.set_visible(visivel)
        self.txt_perda.set_visible(visivel)
        if visivel:
            self.ret_perda.set_y(r.K_depois)
            self.ret_perda.set_height(perda)
            self.txt_perda.set_y(r.K_depois + perda / 2.0)
            self.txt_perda.set_text(f"-{_fmt(perda, 1)}")
            # rótulo de K depois vai para o topo da área tracejada
            self.rotulos_K[1].set_position((self.rotulos_K[1].get_position()[0], r.K_antes))

    def _posicionar_seta(self, i: int, x: float, y: float, v: float, texto: str,
                         cor: str) -> None:
        seta, rotulo = self.setas[i], self.rotulos_seta[i]
        comprimento = v * self.ESCALA_SETA
        seta.set_visible(abs(comprimento) > 0.05)
        seta.xy = (x + comprimento, y)
        seta.set_position((x, y))
        seta.arrow_patch.set_color(cor)
        rotulo.set_visible(True)
        rotulo.set_position((x + comprimento / 2.0, y + 0.12))
        rotulo.set_text(texto)
        rotulo.set_color(cor)

    def _desenhar_blocos(self) -> None:
        c = self.cenario
        r = self.resultado
        x1, x2 = posicoes(self.t, c)
        self.ret1.set_x(x1 - c.w1 / 2.0)
        self.ret2.set_x(x2 - c.w2 / 2.0)
        self.rot1.set_position((x1, self.alt1 / 2.0))
        self.rot2.set_position((x2, self.alt2 / 2.0))

        unidos = c.tc is not None and self.t >= c.tc
        self.linha_choque.set_visible(unidos)
        self.txt_choque.set_visible(unidos)
        y_seta = max(self.alt1, self.alt2) + 0.45
        if unidos:
            # Uma seta só: os blocos seguem juntos com V
            centro = ((x1 - c.w1 / 2.0) + (x2 + c.w2 / 2.0)) / 2.0
            self._posicionar_seta(0, centro, y_seta, r.u1,
                                  f"V = {_fmt(r.u1, 1)} m/s", self.COR_TEXTO)
            self.setas[1].set_visible(False)
            self.rotulos_seta[1].set_visible(False)
        else:
            self._posicionar_seta(0, x1, self.alt1 + 0.45, r.v1,
                                  f"{_fmt(r.v1, 1)} m/s", self.COR_BLOCO1)
            self._posicionar_seta(1, x2, self.alt2 + 0.45, r.v2,
                                  f"{_fmt(r.v2, 1)} m/s", self.COR_BLOCO2)

        tc_txt = f"{_fmt(c.tc)} s" if c.tc is not None else "não há"
        self.txt_tempo.set_text(f"t = {_fmt(self.t)} s    tc = {tc_txt}")
        if c.tc is None:
            self.txt_estado.set_text("")
        elif self.t < c.tc:
            self.txt_estado.set_text("antes do choque")
        else:
            self.txt_estado.set_text("depois do choque: blocos unidos")

    def _atualizar_quadro(self, _quadro):
        """Chamado pela FuncAnimation a cada INTERVALO_MS."""
        if not self.pausado:
            if self._espera_fim > 0.0:
                # Um bloco saiu da tela: fica parado um instante e recomeça do t = 0
                self._espera_fim -= DT_QUADRO
                if self._espera_fim <= 0.0:
                    self._espera_fim = 0.0
                    self.t = 0.0
            else:
                self.t += DT_QUADRO
                c = self.cenario
                x1, x2 = posicoes(self.t, c)
                # Recomeça se um bloco saiu da tela ou se passou TEMPO_APOS_CHOQUE_S
                # do choque (ou do início, sem choque) sem sair, ex.: V = 0 na Q5.
                saiu = bloco_fora_da_pista(x1, c.w1) or bloco_fora_da_pista(x2, c.w2)
                limite = (c.tc if c.tc is not None else 0.0) + TEMPO_APOS_CHOQUE_S
                if saiu or self.t > limite:
                    self._espera_fim = ESPERA_FIM_S
        self._desenhar_blocos()
        return (self.ret1, self.ret2, self.rot1, self.rot2,
                self.txt_tempo, self.txt_estado)

    def mostrar(self) -> None:
        plt.show()


# =============================================================================
# 8. Execução
# =============================================================================

if __name__ == "__main__":
    app = AppColisao()
    app.mostrar()
