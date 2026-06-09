"""
data_structures.py
==================
Estruturas de dados implementadas DO ZERO para o sistema de monitoramento de
riscos ambientais.

Contém:
  * Classe Node e BinarySearchTree (BST) — implementadas manualmente, SEM
    bibliotecas externas (proibido sortedcontainers/bintrees);
  * Classe Grafo — dicionário de listas de adjacência;
  * Uso explícito e justificado de: list, tuple, dict, set, deque, heapq.

Cada vértice é a tupla:
    (id_municipio, nome, indice_risco, custo_atendimento, populacao)
"""

from __future__ import annotations

from collections import deque
from typing import Dict, Iterable, List, Optional, Tuple

Vertice = Tuple[int, str, float, float, int]


# ===========================================================================
# 1) ÁRVORE BINÁRIA DE BUSCA (BST) POR ÍNDICE DE RISCO
# ===========================================================================
class Node:
    """Nó da BST. A chave de ordenação é o índice de risco (float)."""

    __slots__ = ("id_municipio", "nome", "risco", "custo", "populacao",
                 "esquerda", "direita")

    def __init__(self, vertice: Vertice) -> None:
        id_municipio, nome, risco, custo, populacao = vertice
        self.id_municipio: int = id_municipio
        self.nome: str = nome
        self.risco: float = risco        # chave da BST
        self.custo: float = custo
        self.populacao: int = populacao
        self.esquerda: Optional["Node"] = None
        self.direita: Optional["Node"] = None

    def como_tupla(self) -> Vertice:
        return (self.id_municipio, self.nome, self.risco,
                self.custo, self.populacao)

    def __repr__(self) -> str:  # pragma: no cover
        return f"Node({self.nome!r}, risco={self.risco})"


class BinarySearchTree:
    """
    BST sobre os vértices do grafo, ordenada pelo ÍNDICE DE RISCO.

    Propriedade mantida: risco(esquerda) < risco(pai) <= risco(direita).
    Empates de risco vão para a subárvore direita (estável e determinístico).
    """

    def __init__(self) -> None:
        self.raiz: Optional[Node] = None
        self._tamanho: int = 0

    def __len__(self) -> int:
        return self._tamanho

    # ---- inserir -----------------------------------------------------------
    def inserir(self, vertice: Vertice) -> None:
        """Insere um município mantendo a propriedade BST. O(altura)."""
        novo = Node(vertice)
        if self.raiz is None:
            self.raiz = novo
            self._tamanho += 1
            return
        atual = self.raiz
        while True:
            if novo.risco < atual.risco:
                if atual.esquerda is None:
                    atual.esquerda = novo
                    break
                atual = atual.esquerda
            else:
                if atual.direita is None:
                    atual.direita = novo
                    break
                atual = atual.direita
        self._tamanho += 1

    def inserir_muitos(self, vertices: Iterable[Vertice]) -> None:
        for v in vertices:
            self.inserir(v)

    # ---- busca por intervalo ----------------------------------------------
    def buscar(self, r_min: float, r_max: float) -> List[Vertice]:
        """
        Retorna todos os municípios com risco em [r_min, r_max], em ordem
        crescente de risco. Poda subárvores fora do intervalo. O(altura + k).
        """
        resultado: List[Vertice] = []

        def _visita(no: Optional[Node]) -> None:
            if no is None:
                return
            if no.risco > r_min:
                _visita(no.esquerda)
            if r_min <= no.risco <= r_max:
                resultado.append(no.como_tupla())
            if no.risco < r_max:
                _visita(no.direita)

        _visita(self.raiz)
        return resultado

    # ---- percurso in-order -------------------------------------------------
    def percurso_in_order(self) -> List[Vertice]:
        """Municípios em ordem CRESCENTE de risco (útil para priorização)."""
        resultado: List[Vertice] = []
        pilha: List[Node] = []           # uso de LIST como pilha
        atual = self.raiz
        while pilha or atual is not None:
            while atual is not None:
                pilha.append(atual)
                atual = atual.esquerda
            atual = pilha.pop()
            resultado.append(atual.como_tupla())
            atual = atual.direita
        return resultado

    def mais_criticos(self, k: int) -> List[Vertice]:
        """Os k municípios de MAIOR risco (in-order reverso)."""
        return list(reversed(self.percurso_in_order()))[:k]

    # ---- altura / balanceamento -------------------------------------------
    def altura(self) -> int:
        """Altura da árvore (nº de arestas no caminho mais longo)."""

        def _alt(no: Optional[Node]) -> int:
            if no is None:
                return -1
            return 1 + max(_alt(no.esquerda), _alt(no.direita))

        return _alt(self.raiz)

    def esta_balanceada(self) -> bool:
        """Heurística: altura <= 2 * log2(n+1) indica bom balanceamento."""
        import math
        n = len(self)
        if n <= 1:
            return True
        return self.altura() <= 2 * math.ceil(math.log2(n + 1))

    # ---- remoção -----------------------------------------------------------
    def remover(self, id_municipio: int) -> bool:
        """
        Remove o nó cujo id_municipio corresponde, reequilibrando ponteiros
        pelo sucessor in-order. Retorna True se removeu. O(altura).
        """
        # Como a chave da BST é o risco e o id não é a chave, localizamos o
        # risco correspondente primeiro (percorrendo) e então removemos por
        # (risco, id). Mantemos simples para fins didáticos.
        alvo = None
        for no_tupla in self.percurso_in_order():
            if no_tupla[0] == id_municipio:
                alvo = no_tupla
                break
        if alvo is None:
            return False
        self.raiz = self._remover_por_chave(self.raiz, alvo[2], id_municipio)
        self._tamanho -= 1
        return True

    def _remover_por_chave(self, no: Optional[Node], risco: float,
                           id_municipio: int) -> Optional[Node]:
        if no is None:
            return None
        if risco < no.risco:
            no.esquerda = self._remover_por_chave(no.esquerda, risco, id_municipio)
        elif risco > no.risco:
            no.direita = self._remover_por_chave(no.direita, risco, id_municipio)
        else:
            # mesmo risco — confirmar pelo id
            if no.id_municipio != id_municipio:
                # empate de risco: procurar na direita (regra de inserção)
                no.direita = self._remover_por_chave(no.direita, risco, id_municipio)
                return no
            # nó encontrado
            if no.esquerda is None:
                return no.direita
            if no.direita is None:
                return no.esquerda
            # dois filhos: usa sucessor in-order (menor da subárvore direita)
            suc = no.direita
            while suc.esquerda is not None:
                suc = suc.esquerda
            # copia atributos do sucessor para este nó
            no.id_municipio = suc.id_municipio
            no.nome = suc.nome
            no.risco = suc.risco
            no.custo = suc.custo
            no.populacao = suc.populacao
            no.direita = self._remover_por_chave(no.direita, suc.risco,
                                                 suc.id_municipio)
        return no


# ===========================================================================
# 2) GRAFO — DICIONÁRIO DE LISTAS DE ADJACÊNCIA
# ===========================================================================
class Grafo:
    """
    Grafo ponderado não-direcionado.

    Representação: DICIONÁRIO {id_vertice: [(vizinho, peso), ...]} (lista de
    adjacência). Justificativa de complexidade (ver relatório):
      * Espaço: O(V + E)  -> esparso, muito melhor que matriz O(V^2);
      * Vizinhos de v: O(grau(v));
      * As redes de municípios são esparsas (poucas rotas por município),
        portanto a lista de adjacência domina a matriz em espaço e em
        iteração sobre vizinhos.
    """

    def __init__(self) -> None:
        self.adj: Dict[int, List[Tuple[int, float]]] = {}
        self.atributos: Dict[int, Vertice] = {}   # id -> tupla do vértice

    # ---- construção --------------------------------------------------------
    def adicionar_vertice(self, vertice: Vertice) -> None:
        id_municipio = vertice[0]
        self.atributos[id_municipio] = vertice
        self.adj.setdefault(id_municipio, [])

    def adicionar_aresta(self, u: int, v: int, peso: float) -> None:
        self.adj.setdefault(u, []).append((v, peso))
        self.adj.setdefault(v, []).append((u, peso))

    @classmethod
    def de_dados(cls, vertices: List[Vertice],
                 arestas: List[Tuple[int, int, float]]) -> "Grafo":
        g = cls()
        for v in vertices:
            g.adicionar_vertice(v)
        for (u, v, peso) in arestas:
            g.adicionar_aresta(u, v, peso)
        return g

    # ---- consultas ---------------------------------------------------------
    def vertices(self) -> List[int]:
        return list(self.adj.keys())

    def vizinhos(self, u: int) -> List[Tuple[int, float]]:
        return self.adj.get(u, [])

    def arestas(self) -> List[Tuple[int, int, float]]:
        """Lista de arestas únicas (u < v) — usa SET para evitar duplicatas."""
        vistas: set = set()
        resultado: List[Tuple[int, float]] = []
        for u in self.adj:
            for (v, peso) in self.adj[u]:
                chave = (min(u, v), max(u, v))
                if chave not in vistas:
                    vistas.add(chave)
                    resultado.append((u, v, peso))
        return resultado

    def nome(self, u: int) -> str:
        return self.atributos[u][1] if u in self.atributos else str(u)

    def num_vertices(self) -> int:
        return len(self.adj)

    def num_arestas(self) -> int:
        return len(self.arestas())

    # ---- BFS (usa DEQUE e SET) --------------------------------------------
    def bfs(self, origem: int) -> List[int]:
        """Ordem de visita em largura. deque = fila O(1); set = visitados."""
        visitados: set = set([origem])
        fila: deque = deque([origem])
        ordem: List[int] = []
        while fila:
            u = fila.popleft()
            ordem.append(u)
            for (v, _peso) in self.vizinhos(u):
                if v not in visitados:
                    visitados.add(v)
                    fila.append(v)
        return ordem

    def conectado(self) -> bool:
        if not self.adj:
            return True
        return len(self.bfs(self.vertices()[0])) == self.num_vertices()
