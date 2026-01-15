"""
Symbol table for semantic analysis.
"""

from dataclasses import dataclass
from typing import Optional

from quasar.ast import TypeAnnotation


@dataclass
class Symbol:
    """
    Represents a symbol in the symbol table.
    
    Attributes:
        name: The identifier name.
        type_annotation: The declared type.
        is_const: Whether this is a constant (cannot be reassigned).
        is_function: Whether this is a function.
    """
    name: str
    type_annotation: Optional[TypeAnnotation]
    is_const: bool = False
    is_function: bool = False


class SymbolTable:
    """
    Hierarchical symbol table supporting nested scopes.
    
    Each scope is a dictionary mapping names to Symbol objects.
    Lookup searches from innermost to outermost scope.
    """
    
    def __init__(self) -> None:
        """Initialize with a single global scope."""
        self._scopes: list[dict[str, Symbol]] = [{}]
    
    def enter_scope(self) -> None:
        """Enter a new nested scope."""
        self._scopes.append({})
    
    def exit_scope(self) -> None:
        """Exit the current scope and return to parent."""
        if len(self._scopes) > 1:
            self._scopes.pop()
    
    def define(self, symbol: Symbol) -> bool:
        """
        Define a symbol in the current scope.
        
        Returns True if successful, False if already defined in current scope.
        """
        current = self._scopes[-1]
        if symbol.name in current:
            return False
        current[symbol.name] = symbol
        return True
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """
        Look up a symbol by name, searching from innermost to outermost scope.
        
        Returns the Symbol if found, None otherwise.
        """
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        return None
    
    def lookup_current_scope(self, name: str) -> Optional[Symbol]:
        """
        Look up a symbol only in the current (innermost) scope.
        
        Returns the Symbol if found, None otherwise.
        """
        return self._scopes[-1].get(name)
    
    @property
    def depth(self) -> int:
        """Return the current scope depth (0 = global)."""
        return len(self._scopes) - 1
