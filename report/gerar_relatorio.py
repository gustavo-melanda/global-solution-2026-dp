# -*- coding: utf-8 -*-
"""Gera o relatório técnico em PDF (report/relatorio_final.pdf)."""

import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

BASE = os.path.dirname(__file__)
FIG = os.path.join(BASE, "figuras")
SAIDA = os.path.join(BASE, "relatorio_final.pdf")

styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=11.5,
                    spaceAfter=3, spaceBefore=4, textColor=colors.HexColor("#0b3d6b"))
H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=10,
                    spaceAfter=2, spaceBefore=2, textColor=colors.HexColor("#1f6391"))
BODY = ParagraphStyle("BODY", parent=styles["Normal"], fontSize=8.3,
                      alignment=TA_JUSTIFY, leading=10.8, spaceAfter=3)
CAP = ParagraphStyle("CAP", parent=styles["Normal"], fontSize=7,
                     alignment=TA_CENTER, textColor=colors.HexColor("#444444"),
                     leading=9, spaceAfter=6)
TITLE = ParagraphStyle("TITLE", parent=styles["Title"], fontSize=17,
                       textColor=colors.HexColor("#0b3d6b"))
SUB = ParagraphStyle("SUB", parent=styles["Normal"], fontSize=10,
                     alignment=TA_CENTER, textColor=colors.HexColor("#555555"))

story = []


def P(t, s=BODY):
    story.append(Paragraph(t, s))


def img(arquivo, largura=15.5 * cm, legenda=""):
    caminho = os.path.join(FIG, arquivo)
    if os.path.exists(caminho):
        from PIL import Image as PILImage
        w, h = PILImage.open(caminho).size
        altura = largura * h / w
        story.append(Image(caminho, width=largura, height=altura))
        if legenda:
            story.append(Paragraph(legenda, CAP))


def _cell(arquivo, largura, legenda):
    """Monta uma célula (imagem + legenda) para o grid de 2 colunas."""
    from PIL import Image as PILImage
    caminho = os.path.join(FIG, arquivo)
    w, h = PILImage.open(caminho).size
    altura = largura * h / w
    return [Image(caminho, width=largura, height=altura),
            Paragraph(legenda, CAP)]


def grid2(esq, dire):
    """Coloca duas células lado a lado em uma tabela sem bordas."""
    col = 7.6 * cm
    tabela = Table([[esq, dire]], colWidths=[col, col])
    tabela.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(tabela)


# ===================== CAPA / SEÇÃO 1 ======================================
P("Global Solution 2026 — Economia Espacial", TITLE)
P("Monitoramento de Riscos Ambientais com Árvores, Grafos e Algoritmos", SUB)
P("FIAP — Dynamic Programming (Estruturas de Dados e Algoritmos) — Prof. André Marques", SUB)
story.append(Spacer(1, 10))

P("1. Identificação do grupo e contextualização", H1)
ident = [
    ["RM", "Nome"],
    ["561564", "Ben-Hur Iung de Lima Ferreira"],
    ["556081", "Gustavo Melanda da Nova"],
    ["566518", "Felipe Cordeiro"],
    ["566356", "Deivid Ruan Marques Batista"],
]
t = Table(ident, colWidths=[4 * cm, 11.5 * cm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b3d6b")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef3f8")]),
]))
story.append(t)
story.append(Spacer(1, 8))

P("Cenários brasileiros escolhidos. O Brasil é um dos países mais "
  "vulneráveis às mudanças climáticas: a enchente histórica do Rio Grande do "
  "Sul (2024) e a precária conectividade rural em regiões remotas motivam os "
  "dois cenários implementados. <b>Cenário A — Enchentes no RS (2024):</b> "
  "rede de 12 municípios reais afetados, com rodovias ponderadas pelo tempo de "
  "deslocamento (h); objetivo: árvore geradora mínima (MST) de cobertura para "
  "posicionar equipes de resposta. <b>Cenário C — Conectividade rural via "
  "satélite:</b> 10 municípios com baixa cobertura de banda larga, com enlaces "
  "ponderados pelo custo de instalação (mil R$); objetivo: MST de menor custo "
  "para conectar todos ao <i>backbone</i>. O projeto conecta-se aos ODS 2, 9, "
  "11 e 13 da ONU. Os dados são sintéticos, porém construídos sobre IDs e nomes "
  "reais (códigos IBGE) — escolha justificada pela complexidade de download e "
  "limpeza das fontes oficiais (DNIT, ANATEL, IBGE), preservando estrutura e "
  "ordem de grandeza dos casos reais.")

# ===================== SEÇÃO 2 =============================================
P("2. Modelagem das estruturas de dados", H1)
P("Grafo. Formalmente G = (V, E), com V = municípios e E = rotas/enlaces "
  "ponderados. Cada vértice é a tupla imutável "
  "(id_municipio, nome, indice_risco, custo_atendimento, populacao) e cada "
  "aresta é (u, v, peso). A representação adotada é a <b>lista de "
  "adjacência</b> em um dicionário {id: [(vizinho, peso), ...]}. "
  "Justificativa de complexidade: o espaço é O(V + E) contra O(V²) da matriz; "
  "como a rede de municípios é esparsa (poucas rotas por município), a lista "
  "de adjacência é muito mais econômica e a iteração sobre vizinhos custa "
  "O(grau(v)) em vez de O(V).")
P("BST por índice de risco. Uma árvore binária de busca, implementada do "
  "zero com as classes <font face='Courier'>Node</font> e "
  "<font face='Courier'>BinarySearchTree</font> (sem bibliotecas externas), "
  "ordena os municípios pelo índice de risco. Operações: "
  "<font face='Courier'>inserir</font>, "
  "<font face='Courier'>buscar(r_min, r_max)</font> (consulta por intervalo "
  "com poda), <font face='Courier'>percurso_in_order</font> (ordem crescente "
  "de risco para priorização), <font face='Courier'>altura</font> e "
  "<font face='Courier'>remover</font> (com sucessor in-order).")

P("2.1. Tabela de estruturas de dados", H2)
tab = [
    ["Estrutura", "Onde é usada", "Justificativa"],
    ["Lista", "Adjacência; visita BFS; arestas da MST", "Acesso sequencial O(1) por índice"],
    ["Tupla", "Vértice (id,nome,risco,custo,pop); aresta", "Imutável, leve, hashável"],
    ["Dicionário", "Grafo; custos e predecessores (Prim)", "Busca por id O(1) amortizado"],
    ["Conjunto", "Visitados (BFS); fronteira (Prim)", "Pertencimento O(1)"],
    ["Heap (heapq)", "Fila de prioridade no Prim", "Extrair mínimo O(log n)"],
    ["Deque", "Fila do BFS", "Inserção/remoção O(1) nas pontas"],
    ["Árvore (BST)", "Municípios por índice de risco", "Busca/intervalo O(altura)"],
    ["Grafo (dict)", "Rede de municípios e rotas", "Espaço O(V+E), esparso"],
]
t2 = Table(tab, colWidths=[2.7 * cm, 6.5 * cm, 6.3 * cm])
t2.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f6391")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTSIZE", (0, 0), (-1, -1), 7.5),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef3f8")]),
]))
story.append(t2)

# ===================== SEÇÃO 3 =============================================
P("3. Análise de complexidade teórica", H1)
P("Força Bruta (enumeração de árvores geradoras). Pela fórmula de Cayley, um "
  "grafo completo K_N possui N^(N-2) árvores geradoras; a enumeração é, no pior "
  "caso, super-exponencial. Tempo O(N^(N-2)·N) e espaço O(N) pela pilha de "
  "recursão. Usa backtracking e Union-Find para podar ciclos e ramos inviáveis.")
P("Guloso — Prim com heap binário. Cada vértice é extraído uma vez "
  "(O(V log V)) e cada aresta pode gerar uma inserção no heap "
  "(O(E log V)). Total: O((V + E) log V) no tempo e O(V + E) no espaço. A "
  "decisão local — sempre adicionar a aresta de menor peso que cruza o corte "
  "(árvore | resto) — é ótima pela propriedade do corte, logo o Prim produz a "
  "MST global (gap = 0).")

# ===================== SEÇÃO 4 =============================================
P("4. Resultados e figuras obrigatórias", H1)

grid2(
    _cell("grafo_mst_rs.png", 7.2 * cm,
          "Figura 1 — Grafo do Cenário A (Enchentes RS, 2024). MST em vermelho; "
          "nós por índice de risco. Fonte: dados sintéticos sobre IDs IBGE "
          "reais. MST de peso 10,5 h conecta os 12 municípios no menor tempo "
          "total, priorizando rotas curtas (Estrela–Lajeado, 0,2 h) e "
          "descartando redundâncias (Canoas–Montenegro, 0,9 h)."),
    _cell("grafo_mst_conectividade.png", 7.2 * cm,
          "Figura 2 — Grafo do Cenário C (Conectividade rural). MST em vermelho; "
          "peso = custo de instalação (mil R$). Fonte: dados sintéticos sobre "
          "IDs IBGE reais. A MST define a rede de enlaces de menor custo que "
          "conecta todos ao backbone (Porto Velho), evitando enlaces caros "
          "(Boa Vista–Macapá, 240 mil R$)."),
)

img("bst_rs.png", 14 * cm,
    "Figura 3 — BST do Cenário A organizada pelo índice de risco. Cada nó traz "
    "nome e risco. Permite consultas por intervalo e o percurso in-order "
    "devolve os municípios em ordem crescente de criticidade — base para "
    "priorizar o atendimento. A altura indica o grau de balanceamento.")

grid2(
    _cell("desempenho_tempo.png", 7.2 * cm,
          "Figura 4 — Escalabilidade: tempo (log) × N. A Força Bruta (vermelho) "
          "só foi medida até N=12; o Guloso (verde) escala suavemente até "
          "N=100. O salto da FB entre N=10 e N=12 evidencia a explosão "
          "combinatória."),
    _cell("gap_otimalidade.png", 7.2 * cm,
          "Figura 5 — Gap de otimalidade: guloso ótimo (Prim, verde) vs guloso "
          "míope de vizinho-mais-próximo (vermelho). O Prim mantém gap 0% (é "
          "ótimo para MST), enquanto o guloso míope chega a ~11,6% em N=50, "
          "ilustrando o custo de uma decisão local pobre. Referência: Força "
          "Bruta (N≤12) e MST do Prim (N>12)."),
)

img("explosao_combinatoria.png", 9.5 * cm,
    "Figura 6 — Explosão combinatória: nº de árvores geradoras de K_N "
    "(Cayley, N^(N-2)). Em N=9 já são mais de 4,7 milhões de árvores, "
    "tornando a enumeração completa inviável.")

# ===================== SEÇÃO 5 =============================================
P("5. Escala de decisão e análise de desempenho", H1)
res = [
    ["N", "FB (ms)", "Prim (ms)", "Peso Prim", "Peso NN", "Gap Prim", "Gap NN"],
    ["5", "0,100", "0,033", "12,80", "12,80", "0%", "0%"],
    ["8", "0,800", "0,024", "19,03", "19,03", "0%", "0%"],
    ["10", "1,806", "0,026", "21,84", "21,84", "0%", "0%"],
    ["12", "26,32", "0,030", "21,93", "22,24", "0%", "1,41%"],
    ["20", "—", "0,069", "29,21", "29,21", "0%", "0%"],
    ["50", "—", "0,101", "86,00", "95,95", "0%", "11,57%"],
    ["100", "—", "0,245", "192,13", "211,83", "0%", "10,25%"],
]
t3 = Table(res, colWidths=[1.2*cm, 1.9*cm, 2.1*cm, 2.4*cm, 2.2*cm, 2*cm, 1.9*cm])
t3.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f6391")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTSIZE", (0, 0), (-1, -1), 8),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef3f8")]),
]))
story.append(t3)
story.append(Spacer(1, 6))
P("Cruzamento e ponto de inviabilidade. As curvas praticamente não se cruzam: "
  "o Guloso já é mais rápido a partir de N=5. O ponto crítico da Força Bruta "
  "está em <b>N≈12</b>: o tempo salta de ~1,7 ms (N=10) para ~25 ms (N=12) e as "
  "chamadas recursivas vão de 927 para 11.493 — crescimento típico da "
  "super-exponencial N^(N-2). Acima de N=12 a enumeração completa deixa de ser "
  "viável, enquanto o Prim resolve N=100 em ~0,23 ms.")

P("5.1. Escala de decisão (4 níveis)", H2)
esc = [
    ["Nível", "Configuração", "Qualidade", "Custo", "Recomendação"],
    ["1 — Excelente", "Prim (qualquer N viável)", "Ótima (0% gap)", "µs a < 1 ms", "Recomendado"],
    ["2 — Validação", "Força Bruta, N ≤ 12", "Ótima (oráculo)", "Alto em N=12", "Só p/ validar"],
    ["3 — Aceitável", "Guloso míope, N grande", "Subótima (~10% gap)", "µs", "Só se simplicidade exigir"],
    ["4 — Inviável", "Força Bruta, N > 12", "Não termina", "Explosivo", "Descartar"],
]
t4 = Table(esc, colWidths=[2.5*cm, 3.6*cm, 2.8*cm, 2.2*cm, 3.4*cm])
t4.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f6391")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTSIZE", (0, 0), (-1, -1), 7.5),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef3f8")]),
]))
story.append(t4)
story.append(Spacer(1, 6))
P("Trade-off qualidade × custo. Nem todo guloso é ótimo. O Prim, que avalia "
  "toda a fronteira a cada passo, é provadamente ótimo para MST (gap 0%). Já o "
  "guloso míope de vizinho-mais-próximo, que decide apenas com base no último "
  "nó incluído, é igualmente rápido, mas produz árvores até ~11,6% mais caras "
  "(N=50) — esse é o gap de otimalidade real medido na Figura 5. A lição "
  "prática é dupla: (i) a Força Bruta só serve como oráculo em instâncias "
  "pequenas, pois explode em N≈12; e (ii) entre dois gulosos de custo "
  "computacional semelhante, a qualidade da decisão local é o que separa a "
  "solução ótima de uma aproximação. A escolha da estrutura de dados também "
  "pesa: trocar o heap por busca linear da menor aresta elevaria o Prim de "
  "O((V+E)log V) para O(V²).")

# ===================== SEÇÃO 6 =============================================
P("6. Conclusão e conexão com os ODS", H1)
P("O sistema demonstra como estruturas de dados adequadas (grafo esparso, BST, "
  "heap) e a escolha algorítmica correta transformam um problema intratável "
  "por força bruta em uma solução de microssegundos. Recomendação prática: "
  "adotar o Prim para o planejamento operacional dos dois cenários, reservando "
  "a Força Bruta apenas como oráculo de validação em instâncias pequenas. O "
  "projeto contribui para os ODS 9 e 11 (infraestrutura e cidades resilientes, "
  "via roteamento eficiente de equipes e enlaces), ODS 13 (ação climática, ao "
  "priorizar resposta a eventos extremos) e ODS 2 (segurança alimentar, ao "
  "apoiar logística em regiões agrícolas isoladas).")

# ===================== SEÇÃO 7 =============================================
P("7. Referências", H1)
P("• Cormen, T. et al. (2022). <i>Introduction to Algorithms</i>, 4th Ed. MIT "
  "Press (Caps. 22–25).<br/>"
  "• Sedgewick, R.; Wayne, K. (2011). <i>Algorithms</i>, 4th Ed. "
  "Addison-Wesley (Parte 4).<br/>"
  "• Skiena, S. (2020). <i>The Algorithm Design Manual</i>, 3rd Ed. Springer."
  "<br/>• Fontes de dados: DNIT (dnit.gov.br), ANATEL (mapa.anatel.gov.br), "
  "IBGE (ibge.gov.br/geociencias), INMET (bdmep.inmet.gov.br), NASA Earthdata "
  "(earthdata.nasa.gov), INPE PRODES/DETER (terrabrasilis.dpi.inpe.br).")


def _footer(canvas, doc):
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.grey)
    canvas.drawString(2 * cm, 1 * cm,
                      "FIAP — Global Solution 2026 | Dynamic Programming")
    canvas.drawRightString(19 * cm, 1 * cm, f"Página {doc.page}")


doc = SimpleDocTemplate(
    SAIDA, pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm,
    topMargin=1.5*cm, bottomMargin=1.5*cm,
    title="Relatório Técnico — Monitoramento de Riscos Ambientais",
    author="Ben-Hur Ferreira, Gustavo Melanda, Felipe Cordeiro, Deivid Batista",
    subject="FIAP Global Solution 2026 — Dynamic Programming",
    creator="Grupo FIAP",
)
doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
print(f"[OK] {SAIDA}")
