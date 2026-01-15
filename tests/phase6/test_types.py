"""
Tests for Phase 6.0 — Type System Foundation.

Tests cover:
- New type system classes (QuasarType)
- List type declarations [T]
- List literals [1, 2, 3]
- Homogeneous type validation
- Code generation for lists
"""

import pytest

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.semantic import SemanticAnalyzer
from quasar.semantic.errors import SemanticError
from quasar.codegen import CodeGenerator
from quasar.ast.types import (
    QuasarType,
    PrimitiveType,
    ListType,
    INT,
    FLOAT,
    BOOL,
    STR,
    VOID,
    list_of,
)


# =============================================================================
# Type System Unit Tests
# =============================================================================

class TestTypeSystemClasses:
    """Tests for the new type system classes."""
    
    def test_primitive_type_int(self):
        """INT is a PrimitiveType with name 'int'."""
        assert isinstance(INT, PrimitiveType)
        assert INT.name == "int"
    
    def test_primitive_type_float(self):
        """FLOAT is a PrimitiveType with name 'float'."""
        assert isinstance(FLOAT, PrimitiveType)
        assert FLOAT.name == "float"
    
    def test_primitive_type_bool(self):
        """BOOL is a PrimitiveType with name 'bool'."""
        assert isinstance(BOOL, PrimitiveType)
        assert BOOL.name == "bool"
    
    def test_primitive_type_str(self):
        """STR is a PrimitiveType with name 'str'."""
        assert isinstance(STR, PrimitiveType)
        assert STR.name == "str"
    
    def test_primitive_type_void(self):
        """VOID is a PrimitiveType with name 'void'."""
        assert isinstance(VOID, PrimitiveType)
        assert VOID.name == "void"
    
    def test_primitive_type_equality(self):
        """Primitive types with same name are equal."""
        assert INT == PrimitiveType("int")
        assert FLOAT == PrimitiveType("float")
        assert INT != FLOAT
    
    def test_primitive_type_str_repr(self):
        """Primitive types have correct string representation."""
        assert str(INT) == "int"
        assert str(FLOAT) == "float"
        assert str(BOOL) == "bool"
        assert str(STR) == "str"
    
    def test_list_type_simple(self):
        """ListType wraps element type."""
        list_int = ListType(INT)
        assert isinstance(list_int, ListType)
        assert list_int.element_type == INT
    
    def test_list_type_nested(self):
        """ListType can be nested."""
        list_list_int = ListType(ListType(INT))
        assert isinstance(list_list_int, ListType)
        assert isinstance(list_list_int.element_type, ListType)
        assert list_list_int.element_type.element_type == INT
    
    def test_list_type_equality(self):
        """List types with same element type are equal."""
        assert ListType(INT) == ListType(INT)
        assert ListType(STR) == ListType(STR)
        assert ListType(INT) != ListType(STR)
    
    def test_list_type_nested_equality(self):
        """Nested list types are compared recursively."""
        assert ListType(ListType(INT)) == ListType(ListType(INT))
        assert ListType(ListType(INT)) != ListType(ListType(STR))
    
    def test_list_type_str_repr(self):
        """List types have correct string representation."""
        assert str(ListType(INT)) == "[int]"
        assert str(ListType(STR)) == "[str]"
        assert str(ListType(ListType(INT))) == "[[int]]"
        assert str(ListType(ListType(ListType(BOOL)))) == "[[[bool]]]"
    
    def test_list_of_helper(self):
        """list_of() creates ListType."""
        assert list_of(INT) == ListType(INT)
        assert list_of(list_of(STR)) == ListType(ListType(STR))
    
    def test_type_hashable(self):
        """Types can be used as dict keys."""
        type_dict = {INT: "integer", ListType(INT): "list of int"}
        assert type_dict[INT] == "integer"
        assert type_dict[ListType(INT)] == "list of int"


# =============================================================================
# Parser Tests — List Type Annotations
# =============================================================================

def parse(source: str):
    """Helper to parse source code."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()


class TestParserListTypes:
    """Tests for parsing list type annotations."""
    
    def test_parse_list_int_type(self):
        """let x: [int] = [1]"""
        ast = parse("let x: [int] = [1]")
        decl = ast.declarations[0]
        assert decl.type_annotation == ListType(INT)
    
    def test_parse_list_str_type(self):
        """let x: [str] = ['a']"""
        ast = parse('let x: [str] = ["a"]')
        decl = ast.declarations[0]
        assert decl.type_annotation == ListType(STR)
    
    def test_parse_list_float_type(self):
        """let x: [float] = [1.0]"""
        ast = parse("let x: [float] = [1.0]")
        decl = ast.declarations[0]
        assert decl.type_annotation == ListType(FLOAT)
    
    def test_parse_list_bool_type(self):
        """let x: [bool] = [true]"""
        ast = parse("let x: [bool] = [true]")
        decl = ast.declarations[0]
        assert decl.type_annotation == ListType(BOOL)
    
    def test_parse_nested_list_type(self):
        """let x: [[int]] = [[1]]"""
        ast = parse("let x: [[int]] = [[1]]")
        decl = ast.declarations[0]
        assert decl.type_annotation == ListType(ListType(INT))
    
    def test_parse_triple_nested_list(self):
        """let x: [[[str]]] = [[['a']]]"""
        ast = parse('let x: [[[str]]] = [[["a"]]]')
        decl = ast.declarations[0]
        assert decl.type_annotation == ListType(ListType(ListType(STR)))


# =============================================================================
# Parser Tests — List Literals
# =============================================================================

class TestParserListLiterals:
    """Tests for parsing list literal expressions."""
    
    def test_parse_empty_list(self):
        """let x: [int] = []"""
        ast = parse("let x: [int] = []")
        decl = ast.declarations[0]
        from quasar.ast import ListLiteral
        assert isinstance(decl.initializer, ListLiteral)
        assert len(decl.initializer.elements) == 0
    
    def test_parse_single_element_list(self):
        """let x: [int] = [1]"""
        ast = parse("let x: [int] = [1]")
        decl = ast.declarations[0]
        from quasar.ast import ListLiteral, IntLiteral
        assert isinstance(decl.initializer, ListLiteral)
        assert len(decl.initializer.elements) == 1
        assert isinstance(decl.initializer.elements[0], IntLiteral)
    
    def test_parse_multi_element_list(self):
        """let x: [int] = [1, 2, 3]"""
        ast = parse("let x: [int] = [1, 2, 3]")
        decl = ast.declarations[0]
        from quasar.ast import ListLiteral
        assert isinstance(decl.initializer, ListLiteral)
        assert len(decl.initializer.elements) == 3
    
    def test_parse_list_with_trailing_comma(self):
        """let x: [int] = [1, 2, 3,]"""
        ast = parse("let x: [int] = [1, 2, 3,]")
        decl = ast.declarations[0]
        from quasar.ast import ListLiteral
        assert isinstance(decl.initializer, ListLiteral)
        assert len(decl.initializer.elements) == 3
    
    def test_parse_nested_list_literal(self):
        """let x: [[int]] = [[1, 2], [3, 4]]"""
        ast = parse("let x: [[int]] = [[1, 2], [3, 4]]")
        decl = ast.declarations[0]
        from quasar.ast import ListLiteral
        assert isinstance(decl.initializer, ListLiteral)
        assert len(decl.initializer.elements) == 2
        assert isinstance(decl.initializer.elements[0], ListLiteral)
    
    def test_parse_list_with_expressions(self):
        """let x: [int] = [1 + 2, 3 * 4]"""
        ast = parse("let x: [int] = [1 + 2, 3 * 4]")
        decl = ast.declarations[0]
        from quasar.ast import ListLiteral, BinaryExpr
        assert isinstance(decl.initializer, ListLiteral)
        assert isinstance(decl.initializer.elements[0], BinaryExpr)


# =============================================================================
# Semantic Tests — List Type Validation
# =============================================================================

def analyze(source: str):
    """Helper to analyze source code."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(ast)


class TestSemanticListValidation:
    """Tests for semantic validation of lists."""
    
    def test_homogeneous_int_list(self):
        """[1, 2, 3] is valid (all int)."""
        analyze("let x: [int] = [1, 2, 3]")
    
    def test_homogeneous_str_list(self):
        """['a', 'b'] is valid (all str)."""
        analyze('let x: [str] = ["a", "b"]')
    
    def test_homogeneous_bool_list(self):
        """[true, false] is valid (all bool)."""
        analyze("let x: [bool] = [true, false]")
    
    def test_homogeneous_float_list(self):
        """[1.0, 2.5] is valid (all float)."""
        analyze("let x: [float] = [1.0, 2.5]")
    
    def test_empty_list_with_annotation(self):
        """[] with type annotation is valid."""
        analyze("let x: [int] = []")
    
    def test_heterogeneous_list_error_E0500(self):
        """[1, 'a'] should raise E0500."""
        with pytest.raises(SemanticError) as exc_info:
            analyze('let x: [int] = [1, "a"]')
        assert exc_info.value.code == "E0500"
    
    def test_heterogeneous_list_int_bool_error(self):
        """[1, true] should raise E0500."""
        with pytest.raises(SemanticError) as exc_info:
            analyze("let x: [int] = [1, true]")
        assert exc_info.value.code == "E0500"
    
    def test_type_mismatch_list_element(self):
        """let x: [int] = ['a'] should raise type mismatch."""
        with pytest.raises(SemanticError) as exc_info:
            analyze('let x: [int] = ["a"]')
        assert exc_info.value.code == "E0100"
    
    def test_nested_list_type_check(self):
        """[[1, 2], [3, 4]] with [[int]] is valid."""
        analyze("let x: [[int]] = [[1, 2], [3, 4]]")
    
    def test_nested_heterogeneous_error(self):
        """[[1], ['a']] should raise error."""
        with pytest.raises(SemanticError) as exc_info:
            analyze('let x: [[int]] = [[1], ["a"]]')
        # Either E0500 (heterogeneous) or E0100 (type mismatch)
        assert exc_info.value.code in ("E0500", "E0100")


# =============================================================================
# CodeGen Tests — List Generation
# =============================================================================

def generate(source: str) -> str:
    """Helper to generate Python code."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    generator = CodeGenerator()
    return generator.generate(ast)


class TestCodeGenLists:
    """Tests for list code generation."""
    
    def test_codegen_empty_list(self):
        """let x: [int] = [] -> x = []"""
        code = generate("let x: [int] = []")
        assert "x = []" in code
    
    def test_codegen_int_list(self):
        """let x: [int] = [1, 2, 3] -> x = [1, 2, 3]"""
        code = generate("let x: [int] = [1, 2, 3]")
        assert "x = [1, 2, 3]" in code
    
    def test_codegen_str_list(self):
        """let x: [str] = ['a', 'b'] -> x = ['a', 'b']"""
        code = generate('let x: [str] = ["a", "b"]')
        assert 'x = ["a", "b"]' in code
    
    def test_codegen_bool_list(self):
        """let x: [bool] = [true, false] -> x = [True, False]"""
        code = generate("let x: [bool] = [true, false]")
        assert "x = [True, False]" in code
    
    def test_codegen_nested_list(self):
        """let x: [[int]] = [[1], [2]] -> x = [[1], [2]]"""
        code = generate("let x: [[int]] = [[1], [2]]")
        assert "x = [[1], [2]]" in code
    
    def test_codegen_list_with_expressions(self):
        """let x: [int] = [1+2, 3*4] -> x = [1 + 2, 3 * 4]"""
        code = generate("let x: [int] = [1 + 2, 3 * 4]")
        assert "[1 + 2, 3 * 4]" in code


# =============================================================================
# Backward Compatibility Tests
# =============================================================================

class TestBackwardCompatibility:
    """Ensure existing code still works."""
    
    def test_primitive_int_still_works(self):
        """let x: int = 1 still works."""
        analyze("let x: int = 1")
    
    def test_primitive_str_still_works(self):
        """let x: str = 'a' still works."""
        analyze('let x: str = "hello"')
    
    def test_function_with_primitives(self):
        """Functions with primitive types still work."""
        source = """fn add(a: int, b: int) -> int {
    return a + b
}"""
        analyze(source)
    
    def test_print_still_works(self):
        """Print statements still work."""
        analyze('print("hello")')
        analyze('print("{}", 42)')
