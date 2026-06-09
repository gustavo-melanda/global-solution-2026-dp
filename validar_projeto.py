# -*- coding: utf-8 -*-
"""
validar_projeto.py
==================
Validador automático do projeto contra os requisitos do enunciado da
Global Solution 2026 — Dynamic Programming.

Rode da RAIZ do projeto:

    python validar_projeto.py

Ele verifica, item a item, e imprime um relatório com [OK] / [FALHOU] e um
placar final. Código de saída 0 se tudo passou, 1 caso contrário.
"""

from __future__ import annotations

import importlib.util
import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(RAIZ, "src")
sys.path.insert(0, SRC)

# Coletor de resultados: (descrição, ok, detalhe)
resultados = []


def checar(descricao: str, condicao: bool, detalhe: str = "") -> None:
    resultados.append((descricao, bool(condicao), detalhe))


def _existe(*partes) -> bool:
    return os.path.exists(os.path.join(RAIZ, *partes))


# ===========================================================================
# 1) ESTRUTURA OBRIGATÓRIA DE ARQUIVOS/PASTAS
# ===========================================================================
print("\n" + "=" * 70)
print(" 1. ESTRUTURA DO REPOSITÓRIO")
print("=" * 70)

estrutura = [
    ("README.md", ["README.md"]),
    ("requirements.txt", ["requirements.txt"]),
    ("data/raw/", ["data", "raw"]),
    ("data/processed/", ["data", "processed"]),
    ("src/data_structures.py", ["src", "data_structures.py"]),
    ("src/brute_force.py", ["src", "brute_force.py"]),
    ("src/greedy.py", ["src", "greedy.py"]),
    ("src/performance_monitor.py", ["src", "performance_monitor.py"]),
    ("src/visualizations.py", ["src", "visualizations.py"]),
    ("notebooks/analise_resultados.ipynb", ["notebooks", "analise_resultados.ipynb"]),
    ("tests/test_algorithms.py", ["tests", "test_algorithms.py"]),
    ("report/relatorio_final.pdf", ["report", "relatorio_final.pdf"]),
]
for nome, partes in estrutura:
    checar(f"Arquivo/pasta existe: {nome}", _existe(*partes))


# ===========================================================================
# 2) ESTRUTURAS DE DADOS (BST do zero, grafo como lista de adjacência)
# ===========================================================================
print("\n" + "=" * 70)
print(" 2. ESTRUTURAS DE DADOS")
print("=" * 70)

try:
    import data_structures as ds
    from data_loader import carregar_cenario_conectividade, carregar_cenario_rs

    # BST: classes Node e BinarySearchTree implementadas
    checar("Classe Node existe", hasattr(ds, "Node"))
    checar("Classe BinarySearchTree existe", hasattr(ds, "BinarySearchTree"))

    bst = ds.BinarySearchTree()
    for m in ("inserir", "buscar", "percurso_in_order", "altura", "remover"):
        checar(f"BST possui método {m}()", hasattr(bst, m))

    # BST funcional: in-order ordenado
    dados = [(1, "A", 0.5, 1, 1), (2, "B", 0.2, 1, 1), (3, "C", 0.8, 1, 1),
             (4, "D", 0.1, 1, 1), (5, "E", 0.65, 1, 1)]
    bst.inserir_muitos(dados)
    riscos = [v[2] for v in bst.percurso_in_order()]
    checar("BST in-order devolve risco em ordem crescente",
           riscos == sorted(riscos), f"{riscos}")
    intervalo = sorted(v[2] for v in bst.buscar(0.4, 0.7))
    checar("BST busca por intervalo [0.4,0.7] correta",
           intervalo == [0.5, 0.65], f"{intervalo}")
    n_antes = len(bst)
    bst.remover(1)
    checar("BST remover() reduz tamanho e mantém ordem",
           len(bst) == n_antes - 1 and
           [v[2] for v in bst.percurso_in_order()] ==
           sorted(v[2] for v in bst.percurso_in_order()))

    # Grafo: lista de adjacência (dict) + sem bibliotecas externas de árvore
    checar("Classe Grafo existe", hasattr(ds, "Grafo"))
    v, _g, a = carregar_cenario_rs()
    grafo = ds.Grafo.de_dados(v, a)
    checar("Grafo é dict de listas de adjacência",
           isinstance(grafo.adj, dict))
    checar("Grafo do RS tem 12 vértices", grafo.num_vertices() == 12,
           f"{grafo.num_vertices()} vértices")
    checar("Grafo do RS é conexo", grafo.conectado())

    # Uso de deque/set no BFS (estruturas exigidas)
    fonte = importlib.util.find_spec("data_structures")
    with open(os.path.join(SRC, "data_structures.py"), encoding="utf-8") as f:
        codigo_ds = f.read()
    checar("Usa deque (fila) no código", "deque" in codigo_ds)
    checar("Usa set (conjunto) no código", "set(" in codigo_ds or "set:" in codigo_ds)

    # Vértice é tupla; aresta é tupla
    checar("Vértice é uma tupla", isinstance(v[0], tuple))
except Exception as e:  # pragma: no cover
    checar("Importação/uso das estruturas de dados", False, repr(e))


# ===========================================================================
# 3) ALGORITMOS: FORÇA BRUTA E GULOSO (PRIM) + ORÁCULO
# ===========================================================================
print("\n" + "=" * 70)
print(" 3. ALGORITMOS")
print("=" * 70)

try:
    from brute_force import mst_forca_bruta
    from greedy import (cobertura_vizinho_proximo, mst_prim,
                        priorizar_por_risco)

    with open(os.path.join(SRC, "greedy.py"), encoding="utf-8") as f:
        codigo_greedy = f.read()
    with open(os.path.join(SRC, "brute_force.py"), encoding="utf-8") as f:
        codigo_fb = f.read()

    checar("Greedy usa heapq (fila de prioridade)", "heapq" in codigo_greedy)
    checar("Força Bruta usa recursão/backtracking",
           "def backtrack" in codigo_fb or "backtrack(" in codigo_fb)

    # Oráculo: Prim deve coincidir com a Força Bruta nos dois cenários
    for nome, loader in (("RS", carregar_cenario_rs),
                         ("Conectividade", carregar_cenario_conectividade)):
        vv, _gg, aa = loader()
        g = ds.Grafo.de_dados(vv, aa)
        _m, peso_fb, cont_fb = mst_forca_bruta(g)
        mst_g, peso_g, cont_g = mst_prim(g)
        checar(f"[{nome}] Prim == Força Bruta (gap 0%)",
               abs(peso_g - peso_fb) < 1e-6,
               f"Prim={peso_g} FB={peso_fb}")
        checar(f"[{nome}] MST tem V-1 arestas",
               len(mst_g) == g.num_vertices() - 1)
        checar(f"[{nome}] FB instrumenta chamadas recursivas",
               cont_fb.chamadas_recursivas > 0,
               f"{cont_fb.chamadas_recursivas} chamadas")
        checar(f"[{nome}] Prim instrumenta inserções no heap",
               cont_g.insercoes_heap > 0)

    # Guloso míope deve gerar gap > 0 em pelo menos uma instância grande
    from performance_monitor import gerar_grafo_aleatorio
    gap_positivo = False
    for n in (20, 50, 100):
        gg = gerar_grafo_aleatorio(n)
        _a, peso_nn, _c = cobertura_vizinho_proximo(gg)
        _m2, peso_prim, _c2 = mst_prim(gg)
        if peso_nn > peso_prim + 1e-6:
            gap_positivo = True
    checar("Guloso míope gera gap de otimalidade > 0% (subótimo)",
           gap_positivo)

    # Priorização por risco usa a BST
    top = priorizar_por_risco(ds.Grafo.de_dados(*[
        carregar_cenario_rs()[0], carregar_cenario_rs()[2]]), k=3) \
        if False else priorizar_por_risco(
            ds.Grafo.de_dados(carregar_cenario_rs()[0],
                              carregar_cenario_rs()[2]), k=3)
    riscos_top = [t[2] for t in top]
    checar("Priorização por risco (via BST) em ordem decrescente",
           riscos_top == sorted(riscos_top, reverse=True), f"{riscos_top}")
except Exception as e:  # pragma: no cover
    checar("Importação/uso dos algoritmos", False, repr(e))


# ===========================================================================
# 4) DESEMPENHO E FIGURAS OBRIGATÓRIAS
# ===========================================================================
print("\n" + "=" * 70)
print(" 4. DESEMPENHO E FIGURAS")
print("=" * 70)

try:
    from performance_monitor import benchmark

    with open(os.path.join(SRC, "performance_monitor.py"), encoding="utf-8") as f:
        codigo_perf = f.read()
    checar("Mede tempo com perf_counter", "perf_counter" in codigo_perf)
    checar("Mede memória com tracemalloc", "tracemalloc" in codigo_perf)

    regs = benchmark([5, 8, 12])
    checar("Benchmark roda e devolve registros", len(regs) == 3)
    checar("Benchmark expõe gap do Prim e do guloso míope",
           "gap_prim_pct" in regs[0] and "gap_nn_pct" in regs[0])

    figuras = [
        "grafo_mst_rs.png", "grafo_mst_conectividade.png", "bst_rs.png",
        "desempenho_tempo.png", "explosao_combinatoria.png",
        "gap_otimalidade.png",
    ]
    for fig in figuras:
        checar(f"Figura gerada: {fig}",
               _existe("report", "figuras", fig))
except Exception as e:  # pragma: no cover
    checar("Desempenho/figuras", False, repr(e))


# ===========================================================================
# 5) RELATÓRIO (PDF) E DADOS SERIALIZADOS
# ===========================================================================
print("\n" + "=" * 70)
print(" 5. RELATÓRIO E DADOS")
print("=" * 70)

checar("Relatório PDF existe", _existe("report", "relatorio_final.pdf"))
if _existe("report", "relatorio_final.pdf"):
    tam = os.path.getsize(os.path.join(RAIZ, "report", "relatorio_final.pdf"))
    checar("Relatório PDF não está vazio", tam > 10000, f"{tam} bytes")

checar("JSON do cenário RS serializado",
       _existe("data", "processed", "cenario_rs_enchentes.json"))
checar("JSON do cenário Conectividade serializado",
       _existe("data", "processed", "cenario_conectividade_rural.json"))

# Identificação do grupo no README (sem placeholders)
if _existe("README.md"):
    with open(os.path.join(RAIZ, "README.md"), encoding="utf-8") as f:
        readme = f.read()
    checar("README sem placeholders de nome/RA",
           "[NOME" not in readme and "[RA]" not in readme)
    checar("README cita os integrantes (RM)", "561564" in readme)


# ===========================================================================
# PLACAR FINAL
# ===========================================================================
print("\n" + "=" * 70)
print(" RESULTADO DA VALIDAÇÃO")
print("=" * 70)
ok = 0
for desc, passou, detalhe in resultados:
    marca = "[OK]    " if passou else "[FALHOU]"
    extra = f"  ({detalhe})" if (detalhe and not passou) else ""
    print(f"{marca} {desc}{extra}")
    ok += int(passou)

total = len(resultados)
print("-" * 70)
print(f" {ok}/{total} verificações passaram "
      f"({100*ok//total if total else 0}%).")
if ok == total:
    print(" [OK] TODOS OS REQUISITOS VALIDADOS.")
else:
    print(f" [!] {total-ok} item(ns) precisam de atencao (ver [FALHOU] acima).")
print("=" * 70 + "\n")

sys.exit(0 if ok == total else 1)
