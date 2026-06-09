"""
performance_monitor.py
======================
Monitoramento de desempenho dos algoritmos Força Bruta e Guloso (Prim).

Para cada tamanho de instância N registra:
  * Tempo de execução (ms) via time.perf_counter();
  * Memória alocada (MB) via tracemalloc;
  * Nº de operações elementares (chamadas recursivas na FB;
    inserções no heap / arestas relaxadas no Prim);
  * Escalabilidade empírica: curva N vs tempo.

Gera grafos aleatórios CONEXOS de tamanho N para o estudo de escalabilidade.
A Força Bruta só é executada para N pequeno (<= LIMITE_FB) por ser inviável
acima disso (explosão combinatória).
"""

from __future__ import annotations

import random
import time
import tracemalloc
from typing import Dict, List, Optional, Tuple

from brute_force import mst_forca_bruta
from data_structures import Grafo
from greedy import cobertura_vizinho_proximo, mst_prim

LIMITE_FB = 12   # acima disso a Força Bruta torna-se impraticável


def gerar_grafo_aleatorio(n: int, semente: int = 1) -> Grafo:
    """
    Gera um grafo conexo de n vértices: primeiro uma árvore aleatória
    (garante conexão) e depois algumas arestas extras (densidade moderada).
    """
    rng = random.Random(semente + n)
    vertices = [
        (1000 + i, f"M{i}", round(rng.uniform(0.1, 0.95), 2),
         round(rng.uniform(800, 2500), 1), rng.randint(5000, 500000))
        for i in range(n)
    ]
    arestas: List[Tuple[int, int, float]] = []
    # árvore geradora aleatória
    for i in range(1, n):
        j = rng.randint(0, i - 1)
        arestas.append((1000 + i, 1000 + j, round(rng.uniform(0.3, 5.0), 2)))
    # arestas extras (esparso): ~ n/2 a mais
    extras = max(0, n // 2)
    for _ in range(extras):
        a = rng.randint(0, n - 1)
        b = rng.randint(0, n - 1)
        if a != b:
            arestas.append((1000 + a, 1000 + b, round(rng.uniform(0.3, 5.0), 2)))
    return Grafo.de_dados(vertices, arestas)


def medir(funcao, grafo: Grafo) -> Dict[str, float]:
    """Mede tempo (ms), memória de pico (MB) e devolve o contador."""
    tracemalloc.start()
    t0 = time.perf_counter()
    resultado = funcao(grafo)
    t1 = time.perf_counter()
    _atual, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "tempo_ms": (t1 - t0) * 1000.0,
        "memoria_mb": pico / (1024 * 1024),
        "resultado": resultado,
    }


def benchmark(tamanhos: Optional[List[int]] = None) -> List[Dict]:
    """
    Roda o benchmark completo. Retorna lista de registros por N com tempos,
    memória, operações e pesos das MSTs (FB e Greedy).
    """
    if tamanhos is None:
        tamanhos = [5, 8, 10, 12, 20, 50, 100]

    registros: List[Dict] = []
    for n in tamanhos:
        grafo = gerar_grafo_aleatorio(n)
        reg: Dict = {"N": n}

        # ---- Guloso ótimo (Prim) ----
        m_g = medir(mst_prim, grafo)
        _mst_g, peso_g, cont_g = m_g["resultado"]
        reg["greedy_tempo_ms"] = m_g["tempo_ms"]
        reg["greedy_memoria_mb"] = m_g["memoria_mb"]
        reg["greedy_peso"] = peso_g
        reg["greedy_ops"] = cont_g.insercoes_heap + cont_g.arestas_relaxadas

        # ---- Guloso míope (vizinho-mais-próximo, SUBÓTIMO) ----
        m_nn = medir(cobertura_vizinho_proximo, grafo)
        _arv_nn, peso_nn, _cont_nn = m_nn["resultado"]
        reg["nn_tempo_ms"] = m_nn["tempo_ms"]
        reg["nn_peso"] = peso_nn

        # ---- Força Bruta (só para N pequeno) ----
        if n <= LIMITE_FB:
            m_fb = medir(mst_forca_bruta, grafo)
            _mst_fb, peso_fb, cont_fb = m_fb["resultado"]
            reg["fb_tempo_ms"] = m_fb["tempo_ms"]
            reg["fb_memoria_mb"] = m_fb["memoria_mb"]
            reg["fb_peso"] = peso_fb
            reg["fb_ops"] = cont_fb.chamadas_recursivas
            # gaps de otimalidade (%) vs ótimo da Força Bruta
            if peso_fb and peso_fb != float("inf"):
                reg["gap_prim_pct"] = round(100.0 * (peso_g - peso_fb) / peso_fb, 3)
                reg["gap_nn_pct"] = round(100.0 * (peso_nn - peso_fb) / peso_fb, 3)
                # compatibilidade: gap_pct aponta para o guloso míope (o que varia)
                reg["gap_pct"] = reg["gap_nn_pct"]
        else:
            reg["fb_tempo_ms"] = None
            reg["fb_memoria_mb"] = None
            reg["fb_peso"] = None
            reg["fb_ops"] = None
            reg["gap_prim_pct"] = None
            reg["gap_nn_pct"] = None
            reg["gap_pct"] = None

        registros.append(reg)
    return registros


def imprimir_tabela(registros: List[Dict]) -> None:
    cab = (f"{'N':>4} | {'FB tempo(ms)':>13} | {'Prim(ms)':>9} | "
           f"{'Prim peso':>9} | {'NN peso':>8} | {'gap Prim':>9} | {'gap NN':>7}")
    print(cab)
    print("-" * len(cab))
    for r in registros:
        fb_t = f"{r['fb_tempo_ms']:.3f}" if r["fb_tempo_ms"] is not None else "—"
        g_pr = f"{r['gap_prim_pct']}%" if r.get("gap_prim_pct") is not None else "—"
        g_nn = f"{r['gap_nn_pct']}%" if r.get("gap_nn_pct") is not None else "—"
        print(f"{r['N']:>4} | {fb_t:>13} | {r['greedy_tempo_ms']:>9.4f} | "
              f"{r['greedy_peso']:>9} | {r['nn_peso']:>8} | {g_pr:>9} | {g_nn:>7}")


if __name__ == "__main__":
    regs = benchmark()
    imprimir_tabela(regs)
