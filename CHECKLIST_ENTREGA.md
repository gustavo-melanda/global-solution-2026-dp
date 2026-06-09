# Checklist de Entrega — Global Solution 2026 (Dynamic Programming)

Marque cada item conforme concluir. Baseado na seção 7 do enunciado.

## 0. Limpeza
- [ ] Removidos `.venv/`, `.pytest_cache/`, `pytest-cache-files-*` (não vão para a entrega)
      `rm -rf .venv .pytest_cache pytest-cache-files-*`

## 1. Validação (tudo precisa passar)
- [ ] `python validar_projeto.py` → **57/57 (100%)**
- [ ] `python -m pytest tests/ -q` → **18 passed**

## 2. Identificação do grupo (NOME + RA) — req. 7.1 e 7.2
- [ ] README.md com os 4 integrantes e RMs corretos
- [ ] Relatório PDF com a tabela de identificação na 1ª seção

## 3. Estrutura obrigatória do repositório — req. 7.1
- [ ] `README.md` (português, instruções de execução, descrição dos módulos)
- [ ] `requirements.txt`
- [ ] `data/raw/` e `data/processed/`
- [ ] `src/data_structures.py`
- [ ] `src/brute_force.py`
- [ ] `src/greedy.py`
- [ ] `src/performance_monitor.py`
- [ ] `src/visualizations.py`
- [ ] `notebooks/analise_resultados.ipynb`
- [ ] `tests/test_algorithms.py`
- [ ] `report/relatorio_final.pdf`

## 4. Conteúdo técnico exigido
- [ ] Grafo como lista de adjacência (dict) — justificado no relatório
- [ ] BST do zero (Node + BinarySearchTree), sem libs externas de árvore
- [ ] Uso de list, tuple, dict, set, deque, heapq (tabela no relatório)
- [ ] Força Bruta com backtracking + contadores (oráculo de validação)
- [ ] Guloso (Prim) com heapq + integração com a BST
- [ ] ≥ 2 cenários brasileiros (A — Enchentes RS; C — Conectividade rural)
- [ ] Monitor de desempenho (tempo, memória, operações, N=5..100)

## 5. Figuras obrigatórias (em report/figuras/)
- [ ] Grafo com MST destacada (2 cenários)
- [ ] BST (instância de 10–15 nós)
- [ ] Tempo de execução × N (FB vs Guloso)
- [ ] Explosão combinatória
- [ ] Gap de otimalidade (Prim vs guloso míope)

## 6. Relatório técnico (PDF) — req. 7.2, seções na ordem
- [ ] 1. Identificação + contextualização do cenário
- [ ] 2. Modelagem (grafo e BST) com escolha das estruturas justificada
- [ ] 3. Análise de complexidade teórica dos dois algoritmos
- [ ] 4. Resultados com todas as figuras e interpretações
- [ ] 5. Escala de decisão com gap de otimização
- [ ] 6. Conclusão com recomendação prática e conexão com ODS
- [ ] 7. Referências

## 7. GitHub — req. 7.1
- [ ] Repositório PÚBLICO criado
- [ ] Commits DISTRIBUÍDOS entre os 4 integrantes
- [ ] `report/relatorio_final.pdf` versionado no repo
- [ ] Link público submetido na plataforma da FIAP
