"""
Parser tests — Declaration parsing.

Tests that declaration statements produce correct AST nodes.
"""

import pytest

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.ast import (
    Program,
    VarDecl,
    ConstDecl,
    FnDecl,
    Param,
    Block,
    TypeAnnotation,
    IntLiteral,
    FloatLiteral,
    StringLiteral,
    BoolLiteral,
)


def parse(source: str) -> Program:
    """Helper to parse source into a Program AST."""
    lexer = Lexer(source, "test.qsr")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()


class TestVarDecl:
    """Test variable declaration parsing."""
    
    def test_var_decl_int(self) -> None:
        """let x: int = 0 should produce VarDecl with INT type."""
        prog = parse("let x: int = 0")
        assert len(prog.declarations) == 1
        decl = prog.declarations[0]
        assert isinstance(decl, VarDecl)
        assert decl.name == "x"
        assert decl.type_annotation == TypeAnnotation.INT
        assert isinstance(decl.initializer, IntLiteral)
        assert decl.initializer.value == 0
    
    def test_var_decl_float(self) -> None:
        """let y: float = 3.14 should produce VarDecl with FLOAT type."""
        prog = parse("let y: float = 3.14")
        decl = prog.declarations[0]
        assert isinstance(decl, VarDecl)
        assert decl.type_annotation == TypeAnnotation.FLOAT
        assert isinstance(decl.initializer, FloatLiteral)
        assert decl.initializer.value == 3.14
    
    def test_var_decl_bool(self) -> None:
        """let flag: bool = true should produce VarDecl with BOOL type."""
        prog = parse("let flag: bool = true")
        decl = prog.declarations[0]
        assert isinstance(decl, VarDecl)
        assert decl.type_annotation == TypeAnnotation.BOOL
        assert isinstance(decl.initializer, BoolLiteral)
        assert decl.initializer.value is True
    
    def test_var_decl_str(self) -> None:
        """let s: str = "hello" should produce VarDecl with STR type."""
        prog = parse('let s: str = "hello"')
        decl = prog.declarations[0]
        assert isinstance(decl, VarDecl)
        assert decl.type_annotation == TypeAnnotation.STR
        assert isinstance(decl.initializer, StringLiteral)
        assert decl.initializer.value == "hello"


class TestConstDecl:
    """Test constant declaration parsing."""
    
    def test_const_decl(self) -> None:
        """const PI: float = 3.14 should produce ConstDecl."""
        prog = parse("const PI: float = 3.14")
        decl = prog.declarations[0]
        assert isinstance(decl, ConstDecl)
        assert decl.name == "PI"
        assert decl.type_annotation == TypeAnnotation.FLOAT
        assert isinstance(decl.initializer, FloatLiteral)


class TestFnDecl:
    """Test function declaration parsing."""
    
    def test_fn_decl_no_params_with_return(self) -> None:
        """fn foo() -> int { return 0 } should produce FnDecl with return type."""
        prog = parse("fn foo() -> int { return 0 }")
        decl = prog.declarations[0]
        assert isinstance(decl, FnDecl)
        assert decl.name == "foo"
        assert decl.params == []
        assert decl.return_type == TypeAnnotation.INT
        assert isinstance(decl.body, Block)
    
    def test_fn_decl_one_param(self) -> None:
        """fn f(x: int) -> int { return x } should produce FnDecl with one param."""
        prog = parse("fn f(x: int) -> int { return x }")
        decl = prog.declarations[0]
        assert len(decl.params) == 1
        param = decl.params[0]
        assert isinstance(param, Param)
        assert param.name == "x"
        assert param.type_annotation == TypeAnnotation.INT
    
    def test_fn_decl_multiple_params(self) -> None:
        """fn f(a: int, b: float, c: bool) -> int { return a } should have three params."""
        prog = parse("fn f(a: int, b: float, c: bool) -> int { return a }")
        decl = prog.declarations[0]
        assert len(decl.params) == 3
        assert decl.params[0].name == "a"
        assert decl.params[0].type_annotation == TypeAnnotation.INT
        assert decl.params[1].name == "b"
        assert decl.params[1].type_annotation == TypeAnnotation.FLOAT
        assert decl.params[2].name == "c"
        assert decl.params[2].type_annotation == TypeAnnotation.BOOL
    
    def test_fn_decl_with_return_type(self) -> None:
        """fn add(a: int, b: int) -> int { return 0 } should have return type."""
        prog = parse("fn add(a: int, b: int) -> int { return 0 }")
        decl = prog.declarations[0]
        assert decl.return_type == TypeAnnotation.INT
    
    def test_fn_decl_all_return_types(self) -> None:
        """Functions can return any of the four types."""
        for type_str, type_enum in [
            ("int", TypeAnnotation.INT),
            ("float", TypeAnnotation.FLOAT),
            ("bool", TypeAnnotation.BOOL),
            ("str", TypeAnnotation.STR),
        ]:
            prog = parse(f"fn f() -> {type_str} {{ return x }}")
            decl = prog.declarations[0]
            assert decl.return_type == type_enum


class TestMultipleDeclarations:
    """Test programs with multiple declarations."""
    
    def test_multiple_var_decls(self) -> None:
        """Multiple variable declarations should be parsed in order."""
        prog = parse("let a: int = 1\nlet b: int = 2\nlet c: int = 3")
        assert len(prog.declarations) == 3
        names = [d.name for d in prog.declarations]
        assert names == ["a", "b", "c"]
    
    def test_mixed_declarations(self) -> None:
        """Mixed declaration types should all be parsed."""
        source = """
let x: int = 1
const Y: int = 2
fn f() -> int { return 0 }
let z: int = 3
"""
        prog = parse(source)
        assert len(prog.declarations) == 4
        assert isinstance(prog.declarations[0], VarDecl)
        assert isinstance(prog.declarations[1], ConstDecl)
        assert isinstance(prog.declarations[2], FnDecl)
        assert isinstance(prog.declarations[3], VarDecl)
