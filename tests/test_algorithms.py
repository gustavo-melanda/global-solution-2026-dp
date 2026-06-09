"""
Testes automatizados (pytest) das estruturas de dados e algoritmos.

Para rodar:  pytest -v   (a partir da raiz do projeto)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from brute_force import mst_forca_bruta
from data_loader import (carregar_cenario_conectividade,
                         carregar_cenario_rs)
from data_structures import BinarySearchTree, Grafo
from greedy import (cobertura_vizinho_proximo, mst_prim,
                    priorizar_por_risco)
from performance_monitor import gerar_grafo_aleatorio


# --------------------------- BST -------------------------------------------
def _bst_exemplo():
    bst = BinarySearchTree()
    dados = [
        (1, "A", 0.50, 1000.0, 100),
        (2, "B", 0.20, 1000.0, 100),
        (3, "C", 0.80, 1000.0, 100),
        (4, "D", 0.10, 1000.0, 100),
        (5, "E", 0.65, 1000.0, 100),
    ]
    bst.inserir_muitos(dados)
    return bst


def test_bst_in_order_crescente():
    bst = _bst_exemplo()
    riscos = [v[2] for v in bst.percurso_in_order()]
    assert riscos == sorted(riscos)


def test_bst_busca_intervalo():
    bst = _bst_exemplo()
    res = bst.buscar(0.4, 0.7)
    riscos = sorted(v[2] for v in res)
    assert riscos == [0.50, 0.65]


def test_bst_altura_e_tamanho():
    bst = _bst_exemplo()
    assert len(bst) == 5
    assert bst.altura() >= 1


def test_bst_remover():
    bst = _bst_exemplo()
    assert bst.remover(1) is True       # remove A (0.50, raiz)
    riscos = [v[2] for v in bst.percurso_in_order()]
    assert 0.50 not in riscos
    assert len(bst) == 4
    assert riscos == sorted(riscos)     # continua ordenada


def test_bst_mais_criticos():
    bst = _bst_exemplo()
    top2 = bst.mais_criticos(2)
    assert [v[2] for v in top2] == [0.80, 0.65]


# --------------------------- GRAFO -----------------------------------------
def test_grafo_construcao_e_conexao():
    v, _g, a = carregar_cenario_rs()
    grafo = Grafo.de_dados(v, a)
    assert grafo.num_vertices() == 12
    assert grafo.conectado() is True


def test_grafo_arestas_unicas():
    v, _g, a = carregar_cenario_rs()
    grafo = Grafo.de_dados(v, a)
    assert grafo.num_arestas() == len(a)


# --------------------------- PRIM ------------------------------------------
def test_prim_tem_v_menos_1_arestas():
    v, _g, a = carregar_cenario_rs()
    grafo = Grafo.de_dados(v, a)
    mst, peso, _ = mst_prim(grafo)
    assert len(mst) == grafo.num_vertices() - 1
    assert peso > 0


# ------------------- FORÇA BRUTA == GREEDY (oráculo) -----------------------
@pytest.mark.parametrize("loader", [
    carregar_cenario_rs,
    carregar_cenario_conectividade,
])
def test_fb_e_greedy_coincidem_nos_cenarios(loader):
    v, _g, a = loader()
    grafo = Grafo.de_dados(v, a)
    _mst_fb, peso_fb, _c = mst_forca_bruta(grafo)
    _mst_g, peso_g, _cg = mst_prim(grafo)
    # Para MST, Prim é ótimo => o peso deve bater com a Força Bruta.
    assert peso_g == pytest.approx(peso_fb, abs=1e-6)


@pytest.mark.parametrize("n", [5, 8, 10, 12])
def test_fb_e_greedy_coincidem_aleatorios(n):
    grafo = gerar_grafo_aleatorio(n)
    _mst_fb, peso_fb, _c = mst_forca_bruta(grafo)
    _mst_g, peso_g, _cg = mst_prim(grafo)
    assert peso_g == pytest.approx(peso_fb, abs=1e-6)


def test_contadores_instrumentados():
    v, _g, a = carregar_cenario_rs()
    grafo = Grafo.de_dados(v, a)
    _m, _p, cont_fb = mst_forca_bruta(grafo)
    _m2, _p2, cont_g = mst_prim(grafo)
    assert cont_fb.chamadas_recursivas > 0
    assert cont_g.insercoes_heap > 0


def test_nn_conecta_todos_e_nunca_melhor_que_prim():
    """O guloso míope cobre todos os vértices, mas nunca tem peso MENOR que a
    MST (Prim ótimo) — ou seja, gap >= 0."""
    for n in [10, 20, 50]:
        grafo = gerar_grafo_aleatorio(n)
        arv_nn, peso_nn, _c = cobertura_vizinho_proximo(grafo)
        _mst, peso_prim, _cp = mst_prim(grafo)
        assert len(arv_nn) == grafo.num_vertices() - 1
        assert peso_nn >= peso_prim - 1e-6


def test_nn_gera_gap_positivo_em_algum_caso():
    """Em pelo menos uma instância maior, o guloso míope deve ser pior que a
    MST (gap estritamente positivo), validando a figura de gap."""
    houve_gap = False
    for n in [20, 50, 100]:
        grafo = gerar_grafo_aleatorio(n)
        _a, peso_nn, _c = cobertura_vizinho_proximo(grafo)
        _m, peso_prim, _cp = mst_prim(grafo)
        if peso_nn > peso_prim + 1e-6:
            houve_gap = True
    assert houve_gap


def test_priorizacao_por_risco():
    v, _g, a = carregar_cenario_rs()
    grafo = Grafo.de_dados(v, a)
    top = priorizar_por_risco(grafo, k=3)
    riscos = [t[2] for t in top]
    assert riscos == sorted(riscos, reverse=True)
