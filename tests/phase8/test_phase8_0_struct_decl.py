
import pytest
from quasar.parser.parser import Parser
from quasar.lexer.lexer import Lexer
from quasar.semantic.analyzer import SemanticAnalyzer
from quasar.codegen.generator import CodeGenerator
from quasar.parser.errors import ParserError
from quasar.semantic.errors import SemanticError

def parse(source):
    lexer = Lexer(source)
    parser = Parser(lexer.tokenize())
    return parser.parse()

def analyze(source):
    program = parse(source)
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(program)

def generate(source):
    program = analyze(source)
    generator = CodeGenerator()
    return generator.generate(program)

def test_struct_decl_valid():
    source = """
    struct Point {
        x: int,
        y: int
    }
    """
    program = analyze(source)
    assert len(program.declarations) == 1
    decl = program.declarations[0]
    assert decl.name == "Point"
    assert len(decl.fields) == 2
    assert decl.fields[0].name == "x"
    assert decl.fields[0].type_annotation.name == "int"

def test_struct_decl_mixed_types():
    source = """
    struct User {
        name: str,
        age: int,
        active: bool,
        scores: [int]
    }
    """
    program = analyze(source)
    decl = program.declarations[0]
    assert len(decl.fields) == 4
    assert decl.fields[0].name == "name"
    assert decl.fields[3].name == "scores"

def test_struct_decl_empty():
    source = "struct Empty {}"
    program = analyze(source)
    decl = program.declarations[0]
    assert len(decl.fields) == 0

def test_struct_duplicate_name_error():
    source = """
    struct Point { x: int }
    struct Point { y: int }
    """
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E0800"

def test_struct_duplicate_field_error():
    source = """
    struct Point {
        x: int,
        x: int
    }
    """
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E0801"

def test_codegen_struct():
    source = """
    struct Point {
        x: int,
        y: int
    }
    """
    code = generate(source)
    assert "from dataclasses import dataclass" in code
    assert "@dataclass" in code
    assert "class Point:" in code
    assert "x: int" in code
    assert "y: int" in code

def test_codegen_struct_empty():
    source = "struct Empty {}"
    code = generate(source)
    assert "class Empty:" in code
    assert "pass" in code

def test_codegen_struct_list_field():
    source = "struct Data { values: [int] }"
    code = generate(source)
    assert "values: list[int]" in code
