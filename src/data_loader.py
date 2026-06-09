"""
data_loader.py
==============
Geração e carregamento dos dados (sintéticos, devidamente justificados) dos
dois cenários brasileiros do projeto:

    Cenário A — Rede de resposta a enchentes no Rio Grande do Sul (2024)
    Cenário C — Cobertura de conectividade rural via satélite

JUSTIFICATIVA DOS DADOS SINTÉTICOS
----------------------------------
As fontes oficiais (DNIT, Defesa Civil RS, ANATEL, IBGE) disponibilizam os
dados em formatos pesados (shapefiles, malhas viárias completas, planilhas de
cobertura por setor censitário) cujo download e limpeza fogem ao escopo de
uma disciplina de Estruturas de Dados. Optamos por dados SINTÉTICOS mas
REALISTAS:

  * Os IDs e nomes dos municípios são REAIS (códigos IBGE de 7 dígitos);
  * Os pesos de aresta (tempo de deslocamento em horas / custo de instalação
    em milhares de R$) são gerados de forma plausível a partir de distâncias
    aproximadas entre as sedes;
  * O índice de risco (0..1) e o custo de atendimento seguem distribuições
    coerentes com a severidade observada em cada cenário.

Isso permite reproduzir TODA a lógica de grafos, BST e algoritmos sem depender
da disponibilidade momentânea das fontes, mantendo aderência ao caso real.

Cada vértice é uma TUPLA imutável:
    (id_municipio, nome, indice_risco, custo_atendimento, populacao)

Cada aresta é uma TUPLA (u, v, peso) e o grafo é um DICIONÁRIO de listas de
adjacência: {id_vertice: [(vizinho, peso), ...]}.
"""

from __future__ import annotations

import json
import os
import random
from typing import Dict, List, Tuple

# Tipos auxiliares (documentação)
Vertice = Tuple[int, str, float, float, int]
Aresta = Tuple[int, int, float]
Grafo = Dict[int, List[Tuple[int, float]]]

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROC_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


# ---------------------------------------------------------------------------
# CENÁRIO A — Enchentes no Rio Grande do Sul (2024)
# ---------------------------------------------------------------------------
# Subconjunto de 12 municípios reais fortemente afetados pelas enchentes de
# 2024 (códigos IBGE reais). Mantemos N=12 para que a FORÇA BRUTA continue
# viável e sirva de oráculo de validação para o Guloso.
_RS_MUNICIPIOS: List[Tuple[int, str, int]] = [
    # (id_ibge, nome, populacao_aproximada)
    (4314902, "Porto Alegre", 1332570),
    (4309209, "Guaíba", 97150),
    (4314100, "Pelotas", 343132),
    (4316907, "Santa Maria", 271735),
    (4305108, "Canoas", 347657),
    (4318705, "São Leopoldo", 240457),
    (4313409, "Lajeado", 95945),
    (4314050, "Novo Hamburgo", 247032),
    (4307005, "Estrela", 35441),
    (4304606, "Caxias do Sul", 517451),
    (4311403, "Montenegro", 65692),
    (4322004, "Triunfo", 28953),
]

# Arestas (rodovias) com tempo de deslocamento aproximado em HORAS.
_RS_ROTAS: List[Aresta] = [
    (4314902, 4309209, 0.5),   # POA - Guaíba
    (4314902, 4305108, 0.4),   # POA - Canoas
    (4305108, 4318705, 0.5),   # Canoas - São Leopoldo
    (4318705, 4314050, 0.3),   # São Leopoldo - Novo Hamburgo
    (4314050, 4311403, 0.6),   # Novo Hamburgo - Montenegro
    (4311403, 4322004, 0.4),   # Montenegro - Triunfo
    (4311403, 4307005, 1.1),   # Montenegro - Estrela
    (4307005, 4313409, 0.2),   # Estrela - Lajeado
    (4314050, 4304606, 1.3),   # Novo Hamburgo - Caxias do Sul
    (4314902, 4314100, 2.4),   # POA - Pelotas
    (4314902, 4316907, 3.2),   # POA - Santa Maria
    (4316907, 4314100, 3.6),   # Santa Maria - Pelotas
    (4309209, 4314100, 2.0),   # Guaíba - Pelotas
    (4305108, 4311403, 0.9),   # Canoas - Montenegro
    (4304606, 4307005, 1.6),   # Caxias - Estrela
]


# ---------------------------------------------------------------------------
# CENÁRIO C — Conectividade rural via satélite
# ---------------------------------------------------------------------------
# Municípios reais com baixa cobertura de banda larga fixa. Peso da aresta =
# custo estimado de instalação de enlace de rádio/satélite (em milhares de R$).
_CONN_MUNICIPIOS: List[Tuple[int, str, int]] = [
    (1100205, "Porto Velho", 548952),   # backbone (hub)
    (1200401, "Rio Branco", 419452),
    (1302603, "Manaus", 2255903),
    (1600303, "Macapá", 522357),
    (1721000, "Palmas", 313349),
    (2111300, "São Luís", 1108975),
    (5002704, "Campo Grande", 906092),
    (5103403, "Cuiabá", 650912),
    (1400100, "Boa Vista", 436591),
    (1500107, "Belém", 1499641),
]

_CONN_ENLACES: List[Aresta] = [
    (1100205, 1200401, 95.0),
    (1100205, 5103403, 140.0),
    (1100205, 1302603, 210.0),
    (1302603, 1400100, 180.0),
    (1302603, 1500107, 165.0),
    (1500107, 1600303, 120.0),
    (1500107, 2111300, 175.0),
    (2111300, 1721000, 130.0),
    (1721000, 5103403, 150.0),
    (5103403, 5002704, 110.0),
    (5002704, 1100205, 200.0),
    (1600303, 1400100, 240.0),
    (1721000, 1500107, 160.0),
]


def _build_vertices(base, semente: int, risco_alto: bool) -> List[Vertice]:
    """Completa cada município com índice de risco e custo de atendimento."""
    rng = random.Random(semente)
    vertices: List[Vertice] = []
    for id_mun, nome, pop in base:
        if risco_alto:
            risco = round(rng.uniform(0.45, 0.95), 2)
        else:
            risco = round(rng.uniform(0.10, 0.70), 2)
        custo = round(rng.uniform(800.0, 2500.0), 1)
        vertices.append((id_mun, nome, risco, custo, pop))
    return vertices


def _build_grafo(arestas: List[Aresta]) -> Grafo:
    """Constrói o dicionário de adjacência (grafo não-direcionado ponderado)."""
    grafo: Grafo = {}
    for u, v, peso in arestas:
        grafo.setdefault(u, []).append((v, peso))
        grafo.setdefault(v, []).append((u, peso))
    return grafo


def carregar_cenario_rs() -> Tuple[List[Vertice], Grafo, List[Aresta]]:
    """Cenário A — Enchentes RS 2024."""
    vertices = _build_vertices(_RS_MUNICIPIOS, semente=2024, risco_alto=True)
    grafo = _build_grafo(_RS_ROTAS)
    return vertices, grafo, list(_RS_ROTAS)


def carregar_cenario_conectividade() -> Tuple[List[Vertice], Grafo, List[Aresta]]:
    """Cenário C — Conectividade rural via satélite."""
    vertices = _build_vertices(_CONN_MUNICIPIOS, semente=42, risco_alto=False)
    grafo = _build_grafo(_CONN_ENLACES)
    return vertices, grafo, list(_CONN_ENLACES)


def serializar(nome: str, vertices, grafo, arestas) -> str:
    """Salva grafo + vértices em JSON em data/processed/."""
    os.makedirs(PROC_DIR, exist_ok=True)
    caminho = os.path.join(PROC_DIR, f"{nome}.json")
    dados = {
        "vertices": vertices,
        "arestas": arestas,
        # JSON não tem chave inteira; convertemos para str na serialização.
        "grafo": {str(k): v for k, v in grafo.items()},
    }
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    return caminho


if __name__ == "__main__":
    for nome, loader in (
        ("cenario_rs_enchentes", carregar_cenario_rs),
        ("cenario_conectividade_rural", carregar_cenario_conectividade),
    ):
        v, g, a = loader()
        p = serializar(nome, v, g, a)
        print(f"[OK] {nome}: {len(v)} vértices, {len(a)} arestas -> {p}")
