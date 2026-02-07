"""
Router principal da API v1

FASE 5 - Todos os recursos implementados conforme RAG V1.1
FASE 6 - Autenticação JWT adicionada
V1.2 - Athletes habilitado, lookup tables adicionadas
V1.3 - FASE 5 Features (importação, filtros, timeline, notificações)

IMPORTANTE: Este __init__.py agora apenas re-exporta o api_router do api.py
para evitar duplicação e garantir que todos os routers sejam incluídos.
"""

# Importar e re-exportar o api_router do api.py
from app.api.v1.api import api_router

__all__ = ['api_router']
