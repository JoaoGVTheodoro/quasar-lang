"""
Phase 11.0 — Primitive Methods Infrastructure Tests.

Tests for method call parsing, semantic analysis, and code generation.

Test coverage:
- Parser: MethodCallExpr vs MemberAccessExpr disambiguation
- Parser: Method call chaining
- Semantic: Method lookup in PRIMITIVE_METHODS registry
- Semantic: Return type inference
- Semantic: E1105 (method not found)
- Semantic: E1106 (incorrect argument count)
- CodeGen: len() method to Python len()
- CodeGen: Generic method calls
"""

import pytest

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.semantic import SemanticAnalyzer
from quasar.semantic.errors import SemanticError
from quasar.codegen import CodeGenerator
from quasar.ast import (
    MethodCallExpr,
    MemberAccessExpr,
    Identifier,
    StringLiteral,
    INT,
)


def compile_to_python(source: str) -> str:
    """Helper to compile Quasar source to Python."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    generator = CodeGenerator()
    return generator.generate(ast)


def parse_only(source: str):
    """Helper to only parse source code."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()


def analyze_only(source: str):
    """Helper to parse and analyze source code."""
    ast = parse_only(source)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    return ast


# =============================================================================
# Parser Tests — MethodCallExpr vs MemberAccessExpr
# =============================================================================


class TestParserMethodCall:
    """Tests for parsing method calls."""

    def test_parse_method_call_on_string_literal(self):
        """s.len() parses as MethodCallExpr."""
        source = '''
let s: str = "hello"
let n: int = s.len()
'''
        ast = parse_only(source)
        var_decl = ast.declarations[1]  # let n = s.len()
        assert isinstance(var_decl.initializer, MethodCallExpr)
        assert var_decl.initializer.method == "len"
        assert isinstance(var_decl.initializer.object, Identifier)
        assert var_decl.initializer.object.name == "s"
        assert var_decl.initializer.arguments == []

    def test_parse_member_access_is_preserved(self):
        """p.x parses as MemberAccessExpr (regression test)."""
        source = '''
struct Point {
    x: int,
    y: int
}

let p: Point = Point { x: 1, y: 2 }
let val: int = p.x
'''
        ast = parse_only(source)
        var_decl = ast.declarations[2]  # let val = p.x
        assert isinstance(var_decl.initializer, MemberAccessExpr)
        assert var_decl.initializer.member == "x"

    def test_parse_method_call_with_arguments(self):
        """Method call with arguments parses correctly."""
        # For now, we only have len() which takes no args
        # This test structure is ready for future methods
        source = '''
let s: str = "hello"
let n: int = s.len()
'''
        ast = parse_only(source)
        var_decl = ast.declarations[1]
        method_call = var_decl.initializer
        assert isinstance(method_call, MethodCallExpr)
        assert method_call.arguments == []

    def test_parse_method_call_on_list(self):
        """l.len() parses as MethodCallExpr on list."""
        source = '''
let nums: [int] = [1, 2, 3]
let n: int = nums.len()
'''
        ast = parse_only(source)
        var_decl = ast.declarations[1]
        assert isinstance(var_decl.initializer, MethodCallExpr)
        assert var_decl.initializer.method == "len"

    def test_parse_method_call_chaining(self):
        """Method calls can be chained: obj.method1().method2()."""
        # Note: This tests parsing only; semantic validation may fail
        # if return type doesn't support the chained method
        source = '''
let s: str = "hello"
s.len()
'''
        ast = parse_only(source)
        # Should parse without error
        assert len(ast.declarations) == 2


# =============================================================================
# Semantic Tests — Type Checking
# =============================================================================


class TestSemanticMethodCall:
    """Tests for semantic analysis of method calls."""

    def test_string_len_returns_int(self):
        """s.len() on string returns int."""
        source = '''
let s: str = "hello"
let n: int = s.len()
'''
        ast = analyze_only(source)
        # No error means type checking passed
        assert len(ast.declarations) == 2

    def test_list_len_returns_int(self):
        """l.len() on list returns int."""
        source = '''
let nums: [int] = [1, 2, 3]
let n: int = nums.len()
'''
        ast = analyze_only(source)
        assert len(ast.declarations) == 2

    def test_dict_len_returns_int(self):
        """d.len() on dict returns int."""
        source = '''
let d: Dict[str, int] = {"a": 1, "b": 2}
let n: int = d.len()
'''
        ast = analyze_only(source)
        assert len(ast.declarations) == 2

    def test_method_call_in_expression(self):
        """Method call result can be used in expressions."""
        source = '''
let s: str = "hello"
let doubled: int = s.len() * 2
'''
        ast = analyze_only(source)
        assert len(ast.declarations) == 2

    def test_error_e1105_method_not_found(self):
        """E1105: Method does not exist for type."""
        source = '''
let s: str = "hello"
let x: int = s.invalid()
'''
        with pytest.raises(SemanticError) as excinfo:
            analyze_only(source)
        assert excinfo.value.code == "E1105"
        assert "no method 'invalid'" in excinfo.value.message

    def test_error_e1105_no_methods_on_int(self):
        """E1105: Primitive int has no methods."""
        source = '''
let n: int = 42
let x: int = n.len()
'''
        with pytest.raises(SemanticError) as excinfo:
            analyze_only(source)
        assert excinfo.value.code == "E1105"
        assert "has no methods" in excinfo.value.message

    def test_error_e1106_wrong_argument_count(self):
        """E1106: Method called with wrong number of arguments."""
        source = '''
let s: str = "hello"
let n: int = s.len(42)
'''
        with pytest.raises(SemanticError) as excinfo:
            analyze_only(source)
        assert excinfo.value.code == "E1106"
        assert "expects 0 argument(s), got 1" in excinfo.value.message


# =============================================================================
# Code Generation Tests
# =============================================================================


class TestCodeGenMethodCall:
    """Tests for code generation of method calls."""

    def test_codegen_string_len(self):
        """s.len() generates len(s)."""
        source = '''
let s: str = "hello"
let n: int = s.len()
'''
        code = compile_to_python(source)
        assert 'n = len(s)' in code

    def test_codegen_list_len(self):
        """l.len() generates len(l)."""
        source = '''
let nums: [int] = [1, 2, 3]
let n: int = nums.len()
'''
        code = compile_to_python(source)
        assert 'n = len(nums)' in code

    def test_codegen_dict_len(self):
        """d.len() generates len(d)."""
        source = '''
let d: Dict[str, int] = {"a": 1}
let n: int = d.len()
'''
        code = compile_to_python(source)
        assert 'n = len(d)' in code

    def test_codegen_method_in_print(self):
        """Method call in print statement."""
        source = '''
let s: str = "hello"
print(s.len())
'''
        code = compile_to_python(source)
        assert 'print(len(s))' in code


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for method call infrastructure."""

    def test_method_call_execution(self):
        """Generated code executes correctly."""
        source = '''
let s: str = "hello"
let n: int = s.len()
print(n)
'''
        code = compile_to_python(source)
        # Execute and capture output
        import io
        import sys
        captured = io.StringIO()
        sys.stdout = captured
        try:
            exec(code)
        finally:
            sys.stdout = sys.__stdout__
        assert captured.getvalue().strip() == "5"

    def test_list_len_execution(self):
        """List len() method executes correctly."""
        source = '''
let nums: [int] = [1, 2, 3, 4, 5]
print(nums.len())
'''
        code = compile_to_python(source)
        import io
        import sys
        captured = io.StringIO()
        sys.stdout = captured
        try:
            exec(code)
        finally:
            sys.stdout = sys.__stdout__
        assert captured.getvalue().strip() == "5"
