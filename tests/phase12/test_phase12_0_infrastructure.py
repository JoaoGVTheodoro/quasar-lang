"""
Phase 12.0 Tests: Enum Infrastructure (Lexer + Parser)

Tests for enum keyword tokenization and parsing of enum declarations.
"""
import pytest
from quasar.lexer.lexer import Lexer
from quasar.lexer.token_type import TokenType
from quasar.parser.parser import Parser
from quasar.parser.errors import ParserError
from quasar.ast import EnumDecl, EnumVariant


def tokenize(source: str):
    """Tokenize source and return token list."""
    lexer = Lexer(source)
    return lexer.tokenize()


def parse(source: str):
    """Parse source and return AST."""
    lexer = Lexer(source)
    parser = Parser(lexer.tokenize())
    return parser.parse()


# ============================================================================
# Lexer Tests
# ============================================================================

def test_enum_keyword_token():
    """The 'enum' keyword is tokenized correctly."""
    tokens = tokenize("enum")
    assert tokens[0].type == TokenType.ENUM


def test_enum_decl_tokens():
    """Full enum declaration tokenizes correctly."""
    tokens = tokenize("enum Color { Red, Green, Blue }")
    types = [t.type for t in tokens]
    assert TokenType.ENUM in types
    assert TokenType.IDENTIFIER in types
    assert TokenType.LBRACE in types
    assert TokenType.RBRACE in types
    assert TokenType.COMMA in types


def test_enum_access_tokens():
    """Color.Red tokenizes as IDENTIFIER DOT IDENTIFIER."""
    tokens = tokenize("Color.Red")
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].lexeme == "Color"
    assert tokens[1].type == TokenType.DOT
    assert tokens[2].type == TokenType.IDENTIFIER
    assert tokens[2].lexeme == "Red"


# ============================================================================
# Parser Tests
# ============================================================================

def test_parse_simple_enum():
    """Parse a simple enum declaration."""
    program = parse("enum Color { Red }")
    assert len(program.declarations) == 1
    decl = program.declarations[0]
    assert isinstance(decl, EnumDecl)
    assert decl.name == "Color"
    assert len(decl.variants) == 1
    assert decl.variants[0].name == "Red"


def test_parse_enum_multiple_variants():
    """Parse enum with multiple variants."""
    program = parse("enum Status { Pending, Active, Completed, Failed }")
    decl = program.declarations[0]
    assert decl.name == "Status"
    assert len(decl.variants) == 4
    names = [v.name for v in decl.variants]
    assert names == ["Pending", "Active", "Completed", "Failed"]


def test_parse_enum_trailing_comma():
    """Trailing comma is allowed."""
    program = parse("enum Color { Red, Green, Blue, }")
    decl = program.declarations[0]
    assert len(decl.variants) == 3


def test_parse_enum_no_trailing_comma():
    """No trailing comma works correctly."""
    program = parse("enum Light { On, Off }")
    decl = program.declarations[0]
    assert len(decl.variants) == 2


def test_parse_enum_variant_spans():
    """Each variant has a valid span."""
    program = parse("enum Color { Red, Green }")
    decl = program.declarations[0]
    for variant in decl.variants:
        assert isinstance(variant, EnumVariant)
        assert variant.span is not None


def test_parse_error_empty_enum():
    """Empty enum raises parser error."""
    with pytest.raises(ParserError) as excinfo:
        parse("enum Empty { }")
    assert "at least one variant" in str(excinfo.value).lower()


def test_parse_error_missing_lbrace():
    """Missing '{' raises parser error."""
    with pytest.raises(ParserError):
        parse("enum Color Red }")


def test_parse_error_missing_rbrace():
    """Missing '}' raises parser error."""
    with pytest.raises(ParserError):
        parse("enum Color { Red")


def test_parse_error_missing_name():
    """Missing enum name raises parser error."""
    with pytest.raises(ParserError):
        parse("enum { Red }")
