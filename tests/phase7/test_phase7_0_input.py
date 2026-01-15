"""
Phase 7.0 Tests — input() Built-in Function

Tests for the input() built-in which reads user input from stdin.

Signature:
    fn input() -> str
    fn input(prompt: str) -> str
"""

import pytest

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.semantic import SemanticAnalyzer, SemanticError
from quasar.codegen import CodeGenerator


def analyze(source: str):
    """Helper to run semantic analysis."""
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    return SemanticAnalyzer().analyze(ast)


def compile_to_python(source: str) -> str:
    """Helper to compile Quasar to Python."""
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    ast = SemanticAnalyzer().analyze(ast)
    return CodeGenerator().generate(ast)


# =============================================================================
# Semantic: Valid Usage
# =============================================================================

class TestInputSemanticValid:
    """Test valid input() usage."""
    
    def test_input_no_args(self):
        """input() with no arguments is valid."""
        source = """
        let s: str = input()
        """
        ast = analyze(source)
        assert ast is not None
    
    def test_input_with_string_prompt(self):
        """input("prompt") with string argument is valid."""
        source = """
        let name: str = input("Enter your name: ")
        """
        ast = analyze(source)
        assert ast is not None
    
    def test_input_with_variable_prompt(self):
        """input(prompt_var) with string variable is valid."""
        source = """
        let prompt: str = "Enter value: "
        let value: str = input(prompt)
        """
        ast = analyze(source)
        assert ast is not None
    
    def test_input_return_type_is_str(self):
        """input() returns str type."""
        source = """
        let s: str = input()
        """
        ast = analyze(source)
        assert ast is not None
    
    def test_input_in_expression(self):
        """input() can be used in expressions."""
        source = """
        print("{}", input("Name: "))
        """
        ast = analyze(source)
        assert ast is not None


# =============================================================================
# Semantic: Error Cases
# =============================================================================

class TestInputSemanticErrors:
    """Test input() error cases."""
    
    def test_input_too_many_args(self):
        """E0600: input() takes at most 1 argument."""
        source = """
        let s: str = input("a", "b")
        """
        with pytest.raises(SemanticError) as exc:
            analyze(source)
        assert exc.value.code == "E0600"
        assert "at most 1 argument" in exc.value.message
    
    def test_input_three_args(self):
        """E0600: input() with 3 arguments fails."""
        source = """
        let s: str = input("a", "b", "c")
        """
        with pytest.raises(SemanticError) as exc:
            analyze(source)
        assert exc.value.code == "E0600"
    
    def test_input_int_prompt(self):
        """E0601: input() prompt must be str, not int."""
        source = """
        let s: str = input(42)
        """
        with pytest.raises(SemanticError) as exc:
            analyze(source)
        assert exc.value.code == "E0601"
        assert "must be str" in exc.value.message
        assert "int" in exc.value.message
    
    def test_input_bool_prompt(self):
        """E0601: input() prompt must be str, not bool."""
        source = """
        let s: str = input(true)
        """
        with pytest.raises(SemanticError) as exc:
            analyze(source)
        assert exc.value.code == "E0601"
        assert "bool" in exc.value.message
    
    def test_input_assigned_to_int(self):
        """E0100: Cannot assign str (from input) to int variable."""
        source = """
        let x: int = input()
        """
        with pytest.raises(SemanticError) as exc:
            analyze(source)
        assert exc.value.code == "E0100"


# =============================================================================
# Code Generation
# =============================================================================

class TestInputCodeGen:
    """Test input() code generation."""
    
    def test_codegen_input_no_args(self):
        """input() generates Python input()."""
        source = """
        let s: str = input()
        """
        python = compile_to_python(source)
        assert "s = input()" in python
    
    def test_codegen_input_with_prompt(self):
        """input("prompt") generates Python input("prompt")."""
        source = """
        let name: str = input("Enter name: ")
        """
        python = compile_to_python(source)
        assert 'name = input("Enter name: ")' in python
    
    def test_codegen_input_in_print(self):
        """input() in print statement generates correctly."""
        source = """
        print("Hello {}", input("Name: "))
        """
        python = compile_to_python(source)
        assert 'print("Hello {}".format(input("Name: ")))' in python
    
    def test_codegen_input_with_variable_prompt(self):
        """input(var) generates Python input(var)."""
        source = """
        let prompt: str = "Enter: "
        let s: str = input(prompt)
        """
        python = compile_to_python(source)
        assert "s = input(prompt)" in python


# =============================================================================
# Integration Scenarios
# =============================================================================

class TestInputIntegration:
    """Integration tests for input()."""
    
    def test_input_basic_program(self):
        """Complete program with input compiles."""
        source = """
        print("=== Greeting Program ===")
        let name: str = input("Enter your name: ")
        print("Hello, {}!", name)
        """
        python = compile_to_python(source)
        assert "input(" in python
        assert "name" in python
    
    def test_input_multiple_inputs(self):
        """Multiple input() calls in one program."""
        source = """
        let first: str = input("First name: ")
        let last: str = input("Last name: ")
        print("Hello, {} {}!", first, last)
        """
        python = compile_to_python(source)
        assert python.count("input(") == 2
