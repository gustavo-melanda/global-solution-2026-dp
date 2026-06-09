# Global Solution 2026 — Economia Espacial
## Monitoramento de Riscos Ambientais com Árvores, Grafos e Algoritmos

**FIAP — Dynamic Programming (Estruturas de Dados e Algoritmos) — 1º Semestre de 2026**
Prof. André Marques

---

## Identificação do grupo

| Nome | RM |
|------|----|
| Ben-Hur Iung de Lima Ferreira | 561564 |
| Gustavo Melanda da Nova | 556081 |
| Felipe Cordeiro Soares do Carmo | 566518 |
| Deivid Ruan Marques Batista | 566356 |

---

## Visão geral

Sistema de monitoramento e triagem de riscos ambientais em municípios
brasileiros. Os municípios e suas conexões são modelados como um **grafo
ponderado**; os dados de risco são organizados em uma **árvore binária de busca
(BST)**; e a cobertura mínima de rotas é resolvida com **Força Bruta**
(baseline/oráculo) e com um **algoritmo Guloso (Prim)**.

Cenários brasileiros implementados:

- **Cenário A — Enchentes no Rio Grande do Sul (2024):** rede de 12 municípios
  reais afetados; arestas = rodovias com tempo de deslocamento (h). Objetivo:
  MST de cobertura mínima para posicionar equipes de resposta.
- **Cenário C — Conectividade rural via satélite:** 10 municípios com baixa
  cobertura de banda larga; arestas = custo de instalação de enlace (mil R$).
  Objetivo: MST de menor custo para conectar todos ao *backbone*.

Conexão com os **ODS da ONU**: 2 (fome zero), 9 (indústria, inovação e
infraestrutura), 11 (cidades sustentáveis) e 13 (ação climática).

---

## Estrutura do repositório

```
global-solution-2026-fund/
  README.md                      Este arquivo
  requirements.txt               Dependências Python
  data/raw/                      Dados brutos (referência das fontes)
  data/processed/                Grafos serializados em JSON
  src/data_loader.py             Geração/carga dos dados dos cenários
  src/data_structures.py         Node, BST, Grafo (lista de adjacência)
  src/brute_force.py             Enumeração exaustiva da MST (baseline)
  src/greedy.py                  Prim (MST) com heapq + integração BST
  src/performance_monitor.py     Tempo, memória, contadores, escalabilidade
  src/visualizations.py          Geração de todas as figuras obrigatórias
  notebooks/analise_resultados.ipynb   Análise interativa + escala de decisão
  tests/test_algorithms.py       Testes unitários (pytest)
  report/relatorio_final.pdf     Relatório técnico
  report/figuras/                Figuras geradas
```

---

## Instalação

```bash
pip install -r requirements.txt
```

Dependências: `networkx`, `matplotlib`, `seaborn`, `pytest`.
A fila de prioridade usa `heapq` (nativo) e a memória é medida com
`tracemalloc` (nativo).

---

## Como executar

A partir da pasta `src/`:

```bash
cd src

# 1) Gerar os dados dos cenários (JSON em data/processed/)
python data_loader.py

# 2) Rodar a Força Bruta e o Guloso no cenário RS
python brute_force.py
python greedy.py

# 3) Benchmark completo (tabela tempo/memória/operações por N)
python performance_monitor.py

# 4) Gerar TODAS as figuras obrigatórias (report/figuras/)
python visualizations.py
```

Testes automatizados (a partir da raiz do projeto):

```bash
pytest -v
```

---

## Validação dos requisitos

Para verificar automaticamente todos os arquivos e requisitos do enunciado,
execute na raiz do projeto:

```bash
python validar_projeto.py     # checagem completa: 57/57 itens
python -m pytest tests/ -q     # testes de corretude: 18 passed
```

O `validar_projeto.py` confere estrutura de pastas, BST e grafo, algoritmos
(incluindo o oráculo Força Bruta = Prim), monitor de desempenho, figuras
obrigatórias, relatório PDF e identificação do grupo. Ele retorna código de
saída 0 se tudo passou.

---

## Descrição dos módulos

| Módulo | Responsabilidade |
|--------|------------------|
| `data_loader.py` | Define vértices (tuplas) e arestas dos cenários; serializa o grafo em JSON. Justifica o uso de dados sintéticos realistas. |
| `data_structures.py` | `Node` + `BinarySearchTree` (inserir, buscar por intervalo, in-order, altura, remover) implementadas do zero. `Grafo` como dicionário de listas de adjacência, com BFS (deque + set). |
| `brute_force.py` | Enumera todas as árvores geradoras por backtracking + Union-Find; instrumenta chamadas recursivas e soluções avaliadas; serve de oráculo. |
| `greedy.py` | Prim com `heapq`; dicionários de custo e predecessor; `set` da fronteira; integração com a BST para priorizar municípios de alto risco. |
| `performance_monitor.py` | Mede tempo (`perf_counter`), memória (`tracemalloc`) e operações elementares; estuda escalabilidade N = 5, 8, 10, 12, 20, 50, 100. |
| `visualizations.py` | Gera grafo+MST, BST, tempo×N, explosão combinatória e gap de otimalidade. |

---

## Resultados principais

- **Validação:** para os dois cenários e para grafos aleatórios de
  N ∈ {5, 8, 10, 12}, o peso da MST do Prim **coincide exatamente** com o ótimo
  da Força Bruta (gap = 0%), confirmando a otimalidade do Guloso para o problema
  de MST.
- **Gap de otimalidade real:** além do Prim (ótimo), implementamos um guloso
  *míope* (vizinho-mais-próximo) que decide apenas pela vizinhança do último nó.
  Ele é igualmente rápido, mas produz árvores **até ~11,6% mais caras** (N=50) —
  o que torna a figura de gap informativa e ilustra que nem todo guloso é ótimo.
- **Escalabilidade:** a Força Bruta cresce de forma explosiva — em N = 12 já
  realiza milhares de chamadas recursivas — enquanto o Prim permanece na ordem
  de microssegundos até N = 100.

Veja `report/relatorio_final.pdf` para a análise completa, as figuras e a escala
de decisão comentada.

---

## Estruturas de dados utilizadas (resumo)

| Estrutura | Onde é usada |
|-----------|--------------|
| Lista (`list`) | Lista de adjacência; sequência de visita BFS/DFS; arestas da MST |
| Tupla (`tuple`) | Vértice imutável `(id, nome, risco, custo, pop)`; aresta `(u, v, peso)` |
| Dicionário (`dict`) | Grafo `{id: [(viz, peso)]}`; custos e predecessores no Prim |
| Conjunto (`set`) | Vértices visitados (BFS); fronteira do Prim; arestas únicas |
| Heap (`heapq`) | Fila de prioridade da fronteira de expansão no Prim |
| Fila (`deque`) | Fila do BFS no grafo |
| Árvore binária | BST de municípios ordenada por índice de risco |
| Grafo (`dict` de listas) | Rede de municípios e rotas/enlaces |

---

## Fontes de dados (referência)

DNIT (malha viária), Defesa Civil RS, ANATEL (cobertura), IBGE (malha
municipal), INMET/ANA (clima e pluviometria), NASA Earthdata (NDVI), INPE
PRODES/DETER (desmatamento). Os dados deste repositório são **sintéticos**,
construídos sobre IDs/nomes reais (códigos IBGE) — ver justificativa em
`src/data_loader.py` e no relatório.
