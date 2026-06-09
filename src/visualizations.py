"""
visualizations.py
=================
Gera TODAS as figuras obrigatórias do projeto em report/figuras/:

  1. grafo_mst_<cenario>.png   — grafo de municípios com MST destacada;
  2. bst_<cenario>.png         — diagrama da BST por índice de risco;
  3. desempenho_tempo.png      — tempo de execução x N (FB e Greedy);
  4. explosao_combinatoria.png — nº de árvores geradoras x N (escala log);
  5. gap_otimalidade.png       — gap percentual (Greedy vs FB) x N.

Usa networkx + matplotlib para o grafo (networkx NÃO substitui a
implementação do Prim — é apenas layout/desenho).
"""

from __future__ import annotations

import os
from typing import Dict, List, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

# Remove o carimbo "Software: Matplotlib ..." dos PNGs (metadados neutros).
matplotlib.rcParams["svg.hashsalt"] = None
_SAVE_KW = {"metadata": {"Software": None}}

from brute_force import contar_arvores_geradoras
from data_structures import BinarySearchTree, Grafo, Node
from greedy import mst_prim

FIG_DIR = os.path.join(os.path.dirname(__file__), "..", "report", "figuras")


def _garantir_dir() -> None:
    os.makedirs(FIG_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# 1) GRAFO COM MST DESTACADA
# ---------------------------------------------------------------------------
def figura_grafo_mst(grafo: Grafo, titulo: str, arquivo: str,
                     unidade: str = "h") -> str:
    _garantir_dir()
    mst, peso, _ = mst_prim(grafo)
    mst_set = {(min(u, v), max(u, v)) for (u, v, _w) in mst}

    G = nx.Graph()
    for u in grafo.vertices():
        G.add_node(u, label=grafo.nome(u))
    for (u, v, w) in grafo.arestas():
        G.add_edge(u, v, weight=w)

    pos = nx.spring_layout(G, seed=7, k=0.9)
    plt.figure(figsize=(11, 8))

    arestas_mst = [(u, v) for (u, v) in G.edges()
                   if (min(u, v), max(u, v)) in mst_set]
    arestas_outras = [(u, v) for (u, v) in G.edges()
                      if (min(u, v), max(u, v)) not in mst_set]

    nx.draw_networkx_edges(G, pos, edgelist=arestas_outras,
                           edge_color="#bbbbbb", width=1.2, style="dashed")
    nx.draw_networkx_edges(G, pos, edgelist=arestas_mst,
                           edge_color="#d62728", width=3.0)

    riscos = [grafo.atributos[u][2] for u in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_color=riscos, cmap="YlOrRd",
                           node_size=900, edgecolors="black", vmin=0, vmax=1)
    nx.draw_networkx_labels(G, pos,
                            labels={u: grafo.nome(u) for u in G.nodes()},
                            font_size=7)
    edge_labels = {(u, v): f"{d['weight']}" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)

    sm = plt.cm.ScalarMappable(cmap="YlOrRd",
                               norm=plt.Normalize(vmin=0, vmax=1))
    sm.set_array([])
    plt.colorbar(sm, ax=plt.gca(), label="Índice de risco (0–1)", shrink=0.7)

    plt.title(f"{titulo}\nMST destacada em vermelho — peso total = {peso} {unidade}",
              fontsize=11)
    plt.axis("off")
    plt.tight_layout()
    caminho = os.path.join(FIG_DIR, arquivo)
    plt.savefig(caminho, dpi=150, bbox_inches="tight", metadata={"Software": None})
    plt.close()
    return caminho


# ---------------------------------------------------------------------------
# 2) DIAGRAMA DA BST
# ---------------------------------------------------------------------------
def figura_bst(grafo: Grafo, titulo: str, arquivo: str) -> str:
    _garantir_dir()
    bst = BinarySearchTree()
    bst.inserir_muitos(list(grafo.atributos.values()))

    G = nx.DiGraph()
    pos: Dict[str, Tuple[float, float]] = {}
    rotulos: Dict[str, str] = {}

    contador = {"x": 0}

    def percorrer(no: Node, profundidade: int) -> str:
        if no is None:
            return None
        if no.esquerda:
            esq = percorrer(no.esquerda, profundidade + 1)
        else:
            esq = None
        chave = f"{no.id_municipio}"
        contador["x"] += 1
        pos[chave] = (contador["x"], -profundidade)
        rotulos[chave] = f"{no.nome}\n{no.risco}"
        G.add_node(chave)
        if esq is not None:
            G.add_edge(chave, esq)
        if no.direita:
            dire = percorrer(no.direita, profundidade + 1)
            if dire is not None:
                G.add_edge(chave, dire)
        return chave

    if bst.raiz:
        percorrer(bst.raiz, 0)

    plt.figure(figsize=(13, 7))
    nx.draw(G, pos, with_labels=False, node_color="#9ecae1",
            node_size=1700, edgecolors="black", arrows=False)
    nx.draw_networkx_labels(G, pos, labels=rotulos, font_size=7)
    plt.title(f"{titulo}\nBST por índice de risco — altura = {bst.altura()} "
              f"(balanceada: {bst.esta_balanceada()})", fontsize=11)
    plt.axis("off")
    plt.tight_layout()
    caminho = os.path.join(FIG_DIR, arquivo)
    plt.savefig(caminho, dpi=150, bbox_inches="tight", metadata={"Software": None})
    plt.close()
    return caminho


# ---------------------------------------------------------------------------
# 3) DESEMPENHO: TEMPO x N
# ---------------------------------------------------------------------------
def figura_desempenho(registros: List[Dict], arquivo: str = "desempenho_tempo.png") -> str:
    _garantir_dir()
    ns = [r["N"] for r in registros]
    greedy = [r["greedy_tempo_ms"] for r in registros]
    fb_ns = [r["N"] for r in registros if r["fb_tempo_ms"] is not None]
    fb = [r["fb_tempo_ms"] for r in registros if r["fb_tempo_ms"] is not None]

    plt.figure(figsize=(9, 6))
    plt.plot(fb_ns, fb, "o-", color="#d62728", label="Força Bruta", linewidth=2)
    plt.plot(ns, greedy, "s-", color="#2ca02c", label="Guloso (Prim)", linewidth=2)
    plt.yscale("log")
    plt.xlabel("N (nº de vértices)")
    plt.ylabel("Tempo de execução (ms) — escala log")
    plt.title("Escalabilidade empírica: tempo de execução × N")
    plt.legend()
    plt.grid(True, which="both", ls=":", alpha=0.5)
    plt.tight_layout()
    caminho = os.path.join(FIG_DIR, arquivo)
    plt.savefig(caminho, dpi=150, bbox_inches="tight", metadata={"Software": None})
    plt.close()
    return caminho


# ---------------------------------------------------------------------------
# 4) EXPLOSÃO COMBINATÓRIA
# ---------------------------------------------------------------------------
def figura_explosao(arquivo: str = "explosao_combinatoria.png",
                    n_max: int = 9) -> str:
    """Nº de árvores geradoras de um grafo completo K_n (= n^(n-2), Cayley)."""
    _garantir_dir()
    ns = list(range(2, n_max + 1))
    contagens = [n ** (n - 2) for n in ns]  # fórmula de Cayley para K_n

    plt.figure(figsize=(9, 6))
    plt.plot(ns, contagens, "o-", color="#9467bd", linewidth=2)
    plt.yscale("log")
    plt.xlabel("N (nº de vértices, grafo completo)")
    plt.ylabel("Nº de árvores geradoras (escala log)")
    plt.title("Explosão combinatória: árvores geradoras de K_N  (Cayley: N^(N-2))")
    plt.grid(True, which="both", ls=":", alpha=0.5)
    for n, c in zip(ns, contagens):
        plt.annotate(f"{c}", (n, c), textcoords="offset points",
                     xytext=(0, 8), fontsize=7, ha="center")
    plt.tight_layout()
    caminho = os.path.join(FIG_DIR, arquivo)
    plt.savefig(caminho, dpi=150, bbox_inches="tight", metadata={"Software": None})
    plt.close()
    return caminho


# ---------------------------------------------------------------------------
# 5) GAP DE OTIMALIDADE
# ---------------------------------------------------------------------------
def figura_gap(registros: List[Dict], arquivo: str = "gap_otimalidade.png") -> str:
    """
    Compara o gap de otimalidade de dois gulosos contra o ótimo:
      * Prim (guloso ótimo) — gap sempre 0%;
      * Vizinho-mais-próximo (guloso míope) — gap > 0%.

    Referência de ótimo: Força Bruta para N<=12; para N>12 usa-se o peso do
    Prim (provadamente igual à MST ótima) como referência.
    """
    import numpy as np
    _garantir_dir()
    ns, gap_prim, gap_nn = [], [], []
    for r in registros:
        peso_otimo = r["fb_peso"] if r.get("fb_peso") else r["greedy_peso"]
        if not peso_otimo:
            continue
        ns.append(r["N"])
        gap_prim.append(round(100.0 * (r["greedy_peso"] - peso_otimo) / peso_otimo, 3))
        gap_nn.append(round(100.0 * (r["nn_peso"] - peso_otimo) / peso_otimo, 3))

    x = np.arange(len(ns))
    largura = 0.38
    plt.figure(figsize=(9, 6))
    b1 = plt.bar(x - largura / 2, gap_prim, largura,
                 color="#2ca02c", label="Prim (ótimo)")
    b2 = plt.bar(x + largura / 2, gap_nn, largura,
                 color="#d62728", label="Vizinho-mais-próximo (míope)")
    plt.xticks(x, [str(n) for n in ns])
    plt.xlabel("N (nº de vértices)")
    plt.ylabel("Gap de otimalidade (%)  [(peso − ótimo) / ótimo]")
    plt.title("Gap de otimalidade: guloso ótimo (Prim) vs guloso míope")
    plt.axhline(0, color="black", linewidth=0.8)
    plt.legend()
    for barras in (b1, b2):
        for b in barras:
            h = b.get_height()
            plt.annotate(f"{h}%", (b.get_x() + b.get_width() / 2, h),
                         textcoords="offset points", xytext=(0, 3),
                         ha="center", fontsize=7)
    plt.tight_layout()
    caminho = os.path.join(FIG_DIR, arquivo)
    plt.savefig(caminho, dpi=150, bbox_inches="tight", metadata={"Software": None})
    plt.close()
    return caminho


def gerar_todas() -> List[str]:
    """Gera todas as figuras e retorna os caminhos."""
    from data_loader import (carregar_cenario_conectividade,
                             carregar_cenario_rs)
    from performance_monitor import benchmark

    caminhos: List[str] = []

    v_rs, _g, a_rs = carregar_cenario_rs()
    g_rs = Grafo.de_dados(v_rs, a_rs)
    caminhos.append(figura_grafo_mst(
        g_rs, "Cenário A — Enchentes no Rio Grande do Sul (2024)",
        "grafo_mst_rs.png", unidade="h"))
    caminhos.append(figura_bst(
        g_rs, "Cenário A — Enchentes RS", "bst_rs.png"))

    v_c, _g2, a_c = carregar_cenario_conectividade()
    g_c = Grafo.de_dados(v_c, a_c)
    caminhos.append(figura_grafo_mst(
        g_c, "Cenário C — Conectividade rural via satélite",
        "grafo_mst_conectividade.png", unidade="mil R$"))

    registros = benchmark()
    caminhos.append(figura_desempenho(registros))
    caminhos.append(figura_explosao())
    caminhos.append(figura_gap(registros))
    return caminhos


if __name__ == "__main__":
    for c in gerar_todas():
        print(f"[FIG] {c}")
