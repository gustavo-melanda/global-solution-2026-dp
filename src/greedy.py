"""
greedy.py
=========
ALGORITMO GULOSO — Prim para a Árvore Geradora Mínima (MST).

Variante escolhida: PRIM (justificativa no relatório). A cada passo o
algoritmo adiciona a aresta de MENOR peso que conecta um vértice novo à árvore
já construída — decisão local ótima que comprovadamente leva à MST global.

Requisitos do enunciado atendidos:
  * heap (heapq) como fila de prioridade da fronteira de expansão;
  * dicionário de custos mínimos (chave) e de predecessores;
  * conjunto (set) de vértices já incluídos na árvore;
  * reconstrução e exibição da árvore ótima;
  * integração com a BST para priorizar municípios de alto risco;
  * contadores de operações (inserções no heap / arestas relaxadas).
"""

from __future__ import annotations

import heapq
from typing import Dict, List, Optional, Tuple

from data_structures import BinarySearchTree, Grafo

Aresta = Tuple[int, int, float]


class ContadorGreedy:
    """Instrumentação do Guloso."""

    def __init__(self) -> None:
        self.insercoes_heap: int = 0
        self.arestas_relaxadas: int = 0
        self.extracoes_heap: int = 0


def mst_prim(grafo: Grafo,
             origem: Optional[int] = None
             ) -> Tuple[List[Aresta], float, ContadorGreedy]:
    """
    Prim com heap binário (heapq).

    Decisão local: extrai do heap a aresta de menor custo que toca a fronteira.
    Prova informal de corretude (propriedade do corte): para qualquer corte do
    grafo, a aresta de menor peso que o cruza pertence a alguma MST; Prim sempre
    escolhe exatamente essa aresta para o corte (árvore atual | resto), logo a
    escolha gulosa nunca exclui a solução ótima.

    Retorna: (arestas_da_mst, peso_total, contador).
    """
    vertices = grafo.vertices()
    contador = ContadorGreedy()
    if not vertices:
        return [], 0.0, contador

    if origem is None:
        origem = vertices[0]

    na_arvore: set = set()                       # SET de incluídos
    predecessor: Dict[int, Optional[int]] = {}   # DICT de predecessores
    custo_min: Dict[int, float] = {}             # DICT custo mínimo p/ alcançar
    mst: List[Aresta] = []
    peso_total = 0.0

    # heap de tuplas (peso, vertice_destino, vertice_origem)
    heap: List[Tuple[float, int, Optional[int]]] = [(0.0, origem, None)]
    contador.insercoes_heap += 1

    while heap and len(na_arvore) < len(vertices):
        peso, u, pred = heapq.heappop(heap)
        contador.extracoes_heap += 1
        if u in na_arvore:
            continue
        na_arvore.add(u)
        if pred is not None:
            mst.append((pred, u, peso))
            peso_total += peso
        # relaxa as arestas dos vizinhos ainda fora da árvore
        for (v, w) in grafo.vizinhos(u):
            contador.arestas_relaxadas += 1
            if v not in na_arvore and (v not in custo_min or w < custo_min[v]):
                custo_min[v] = w
                predecessor[v] = u
                heapq.heappush(heap, (w, v, u))
                contador.insercoes_heap += 1

    return mst, round(peso_total, 4), contador


def cobertura_vizinho_proximo(grafo: Grafo,
                              origem: Optional[int] = None
                              ) -> Tuple[List[Aresta], float, ContadorGreedy]:
    """
    GULOSO MÍOPE (vizinho-mais-próximo) — heurística de cobertura SUBÓTIMA.

    A cada passo, a partir do ÚLTIMO município incluído, escolhe a aresta de
    menor peso que leva a um município ainda não coberto (decisão local restrita
    à vizinhança do último nó). Se o último nó não tem vizinho novo, salta para
    o nó já coberto que tenha a aresta de menor peso para fora — mas continua
    sem reavaliar globalmente a fronteira.

    Diferente do Prim (que olha TODA a fronteira), esta heurística pode "se
    prender" a um caminho ruim e produzir uma árvore de peso MAIOR que a MST.
    Por isso gera um GAP DE OTIMALIDADE > 0% em relação à Força Bruta, servindo
    para ilustrar o trade-off qualidade × simplicidade da decisão local.
    """
    vertices = grafo.vertices()
    contador = ContadorGreedy()
    if not vertices:
        return [], 0.0, contador
    if origem is None:
        origem = vertices[0]

    cobertos: set = set([origem])
    arvore: List[Aresta] = []
    peso_total = 0.0
    atual = origem

    while len(cobertos) < len(vertices):
        # 1) tenta o vizinho mais próximo do nó ATUAL (visão local míope)
        melhor = None
        for (v, w) in grafo.vizinhos(atual):
            contador.arestas_relaxadas += 1
            if v not in cobertos and (melhor is None or w < melhor[1]):
                melhor = (v, w)
        if melhor is not None:
            v, w = melhor
            arvore.append((atual, v, w))
            peso_total += w
            cobertos.add(v)
            atual = v
            continue
        # 2) nó atual sem vizinho novo: escolhe, entre os já cobertos, a aresta
        #    de menor peso que alcança algum não coberto (ainda sem visão global
        #    completa de fronteira — escolha gulosa restrita).
        salto = None
        for u in cobertos:
            for (v, w) in grafo.vizinhos(u):
                contador.arestas_relaxadas += 1
                if v not in cobertos and (salto is None or w < salto[2]):
                    salto = (u, v, w)
        if salto is None:
            break  # grafo desconexo
        u, v, w = salto
        arvore.append((u, v, w))
        peso_total += w
        cobertos.add(v)
        atual = v

    return arvore, round(peso_total, 4), contador


def priorizar_por_risco(grafo: Grafo, k: int = 5) -> List[Tuple[int, str, float]]:
    """
    Usa a BST (construída a partir dos vértices) para devolver os k municípios
    de MAIOR risco — usados para priorizar a ordem de atendimento/cobertura.
    """
    bst = BinarySearchTree()
    bst.inserir_muitos(list(grafo.atributos.values()))
    criticos = bst.mais_criticos(k)
    return [(c[0], c[1], c[2]) for c in criticos]


def exibir_mst(grafo: Grafo, mst: List[Aresta], peso: float) -> str:
    """Formata a MST de forma legível (para log e relatório)."""
    linhas = [f"MST (Prim) — peso total = {peso}"]
    for (u, v, w) in mst:
        linhas.append(f"  {grafo.nome(u)} --({w})--> {grafo.nome(v)}")
    return "\n".join(linhas)


if __name__ == "__main__":
    from data_loader import carregar_cenario_rs

    v, _g, a = carregar_cenario_rs()
    grafo = Grafo.de_dados(v, a)
    mst, peso, cont = mst_prim(grafo)
    print(exibir_mst(grafo, mst, peso))
    print(f"  inserções no heap   = {cont.insercoes_heap}")
    print(f"  arestas relaxadas   = {cont.arestas_relaxadas}")
    print("\nMunicípios de maior risco (via BST):")
    for (idm, nome, risco) in priorizar_por_risco(grafo):
        print(f"  {nome}: risco={risco}")
