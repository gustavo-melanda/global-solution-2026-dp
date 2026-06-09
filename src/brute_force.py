"""
brute_force.py
==============
FORÇA BRUTA — busca exaustiva da Árvore Geradora Mínima (MST).

Para grafos pequenos (N <= 12 vértices) enumeramos TODAS as árvores geradoras
possíveis por recursão com BACKTRACKING e escolhemos a de menor peso total.
Serve como ORÁCULO de validação para o algoritmo Guloso (Prim).

Instrumentação exigida pelo enunciado:
  * contador de chamadas recursivas;
  * contador de árvores geradoras (soluções) avaliadas;
  * registro do custo de cada solução e identificação do ótimo global.

Estratégia: enumeração de subconjuntos de E com exatamente V-1 arestas que
formam uma árvore geradora (conexa e acíclica), verificada com Union-Find.
Usa backtracking para podar ramos que já não cabem em V-1 arestas.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from data_structures import Grafo

Aresta = Tuple[int, int, float]


class ContadorFB:
    """Agrupa os contadores de instrumentação da Força Bruta."""

    def __init__(self) -> None:
        self.chamadas_recursivas: int = 0
        self.arvores_avaliadas: int = 0


# ---- Union-Find (para testar ciclo/conexão) -------------------------------
def _find(pai: Dict[int, int], x: int) -> int:
    while pai[x] != x:
        pai[x] = pai[pai[x]]   # path compression
        x = pai[x]
    return x


def _union(pai: Dict[int, int], a: int, b: int) -> bool:
    ra, rb = _find(pai, a), _find(pai, b)
    if ra == rb:
        return False           # formaria ciclo
    pai[ra] = rb
    return True


def mst_forca_bruta(grafo: Grafo) -> Tuple[List[Aresta], float, ContadorFB]:
    """
    Enumera todas as árvores geradoras e devolve a de menor peso.

    Retorna: (arestas_da_mst, peso_total, contador).
    """
    vertices = grafo.vertices()
    n = len(vertices)
    arestas = sorted(grafo.arestas(), key=lambda e: e[2])
    m = len(arestas)
    contador = ContadorFB()

    melhor_peso = float("inf")
    melhor_arvore: List[Aresta] = []

    def backtrack(inicio: int, escolhidas: List[Aresta],
                  pai: Dict[int, int], peso: float, comps: int) -> None:
        nonlocal melhor_peso, melhor_arvore
        contador.chamadas_recursivas += 1

        # Poda 1: já passou do peso do melhor encontrado.
        if peso >= melhor_peso:
            return

        # Caso base: V-1 arestas escolhidas formando 1 componente => MST.
        if len(escolhidas) == n - 1:
            if comps == 1:
                contador.arvores_avaliadas += 1
                if peso < melhor_peso:
                    melhor_peso = peso
                    melhor_arvore = list(escolhidas)
            return

        # Poda 2: arestas restantes insuficientes para completar a árvore.
        if m - inicio < (n - 1) - len(escolhidas):
            return

        for i in range(inicio, m):
            u, v, p = arestas[i]
            pai_copia = dict(pai)            # estado para backtracking
            if _union(pai_copia, u, v):      # só adiciona se não criar ciclo
                escolhidas.append((u, v, p))
                backtrack(i + 1, escolhidas, pai_copia, peso + p, comps - 1)
                escolhidas.pop()             # desfaz (backtracking)

    pai0 = {v: v for v in vertices}
    backtrack(0, [], pai0, 0.0, n)

    if melhor_peso == float("inf"):
        return [], float("inf"), contador
    return melhor_arvore, round(melhor_peso, 4), contador


def contar_arvores_geradoras(grafo: Grafo) -> int:
    """
    Conta (sem otimizar) quantas árvores geradoras o grafo possui — usado
    para evidenciar a EXPLOSÃO COMBINATÓRIA em função de N.
    """
    vertices = grafo.vertices()
    n = len(vertices)
    arestas = grafo.arestas()
    m = len(arestas)
    total = 0

    def bt(inicio: int, k: int, pai: Dict[int, int]) -> None:
        nonlocal total
        if k == n - 1:
            # confirma conexão
            raizes = {_find(pai, v) for v in vertices}
            if len(raizes) == 1:
                total += 1
            return
        if m - inicio < (n - 1) - k:
            return
        for i in range(inicio, m):
            u, v, _p = arestas[i]
            pai_copia = dict(pai)
            if _union(pai_copia, u, v):
                bt(i + 1, k + 1, pai_copia)

    bt(0, 0, {v: v for v in vertices})
    return total


if __name__ == "__main__":
    from data_loader import carregar_cenario_rs
    from data_structures import Grafo as G

    v, _g, a = carregar_cenario_rs()
    grafo = G.de_dados(v, a)
    mst, peso, cont = mst_forca_bruta(grafo)
    print(f"MST (Força Bruta): peso={peso}h  arestas={len(mst)}")
    print(f"  chamadas recursivas = {cont.chamadas_recursivas}")
    print(f"  árvores avaliadas   = {cont.arvores_avaliadas}")
