# Fontes de dados (brutos)

Os dados deste projeto são **sintéticos**, mas construídos sobre identificadores
e nomes reais (códigos IBGE de 7 dígitos). As fontes oficiais que embasam os
cenários são:

| Cenário | Fonte oficial | Conteúdo de referência |
|---------|---------------|------------------------|
| A — Enchentes RS 2024 | DNIT (`dnit.gov.br`) | Malha viária federal (tempo de deslocamento) |
| A — Enchentes RS 2024 | Defesa Civil RS | Municípios afetados pelas enchentes de 2024 |
| C — Conectividade rural | ANATEL (`mapa.anatel.gov.br`) | Cobertura de banda larga fixa |
| C — Conectividade rural | IBGE (`ibge.gov.br/geociencias`) | Malha municipal e população |
| Risco ambiental | NASA Earthdata (MODIS NDVI) | Cobertura vegetal |
| Risco ambiental | INMET (`bdmep.inmet.gov.br`) / ANA | Precipitação e hidrologia |
| Desmatamento | INPE PRODES/DETER (`terrabrasilis.dpi.inpe.br`) | Alertas Amazônia |

## Por que dados sintéticos?

As fontes acima entregam dados em shapefiles e planilhas extensas cujo download
e limpeza fogem ao escopo de uma disciplina de Estruturas de Dados. Os dados
sintéticos preservam a estrutura e a ordem de grandeza dos casos reais (IDs e
nomes reais, pesos plausíveis), permitindo reproduzir integralmente a lógica de
grafos, BST e algoritmos sem dependência da disponibilidade momentânea das
fontes. Ver `src/data_loader.py`.
