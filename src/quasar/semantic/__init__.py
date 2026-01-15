"""
Quasar semantic analysis module.

Responsible for type checking and semantic validation.
"""

from quasar.semantic.errors import SemanticError
from quasar.semantic.symbols import Symbol, SymbolTable
from quasar.semantic.analyzer import SemanticAnalyzer

__all__ = [
    "SemanticError",
    "Symbol",
    "SymbolTable",
    "SemanticAnalyzer",
]
