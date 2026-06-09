"""Configuração compartilhada dos testes."""
import sys

# A Força Bruta usa recursão profunda em instâncias N=12; elevamos o limite
# para evitar RecursionError durante a suíte.
sys.setrecursionlimit(20000)
