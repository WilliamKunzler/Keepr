"""Blueprints — camada de apresentação (rotas HTTP).

Cada recurso tem seu próprio blueprint, registrado no factory com prefixo
de URL. As rotas só roteiam (SRP): chamam services, retornam JSON.
"""
