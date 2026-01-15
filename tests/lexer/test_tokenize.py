"""
Lexer tests — Token type verification.

Tests that valid Quasar source code produces the correct token types.
"""

import pytest

from quasar.lexer import Lexer, Token, TokenType


class TestKeywords:
    """Test keyword tokenization."""
    
    @pytest.mark.parametrize("source,expected", [
        ("let", TokenType.LET),
        ("const", TokenType.CONST),
        ("fn", TokenType.FN),
        ("return", TokenType.RETURN),
        ("if", TokenType.IF),
        ("else", TokenType.ELSE),
        ("while", TokenType.WHILE),
        ("break", TokenType.BREAK),
        ("continue", TokenType.CONTINUE),
        ("true", TokenType.TRUE),
        ("false", TokenType.FALSE),
    ])
    def test_language_keywords(self, source: str, expected: TokenType) -> None:
        """Each language keyword should produce the correct token type."""
        lexer = Lexer(source, "test.qsr")
        tokens = lexer.tokenize()
        assert tokens[0].type == expected
        assert tokens[0].lexeme == source
    
    @pytest.mark.parametrize("source,expected", [
        ("int", TokenType.INT),
        ("float", TokenType.FLOAT),
        ("bool", TokenType.BOOL),
        ("str", TokenType.STR),
    ])
    def test_type_keywords(self, source: str, expected: TokenType) -> None:
        """Each type keyword should produce the correct token type."""
        lexer = Lexer(source, "test.qsr")
        tokens = lexer.tokenize()
        assert tokens[0].type == expected


class TestOperators:
    """Test operator tokenization."""
    
    @pytest.mark.parametrize("source,expected", [
        ("+", TokenType.PLUS),
        ("-", TokenType.MINUS),
        ("*", TokenType.STAR),
        ("/", TokenType.SLASH),
        ("%", TokenType.PERCENT),
    ])
    def test_arithmetic_operators(self, source: str, expected: TokenType) -> None:
        """Arithmetic operators should produce correct token types."""
        lexer = Lexer(source, "test.qsr")
        tokens = lexer.tokenize()
        assert tokens[0].type == expected
    
    @pytest.mark.parametrize("source,expected", [
        ("==", TokenType.EQUAL_EQUAL),
        ("!=", TokenType.BANG_EQUAL),
        ("<", TokenType.LESS),
        (">", TokenType.GREATER),
        ("<=", TokenType.LESS_EQUAL),
        (">=", TokenType.GREATER_EQUAL),
    ])
    def test_comparison_operators(self, source: str, expected: TokenType) -> None:
        """Comparison operators should produce correct token types."""
        lexer = Lexer(source, "test.qsr")
        tokens = lexer.tokenize()
        assert tokens[0].type == expected
    
    @pytest.mark.parametrize("source,expected", [
        ("&&", TokenType.AND_AND),
        ("||", TokenType.OR_OR),
        ("!", TokenType.BANG),
    ])
    def test_logical_operators(self, source: str, expected: TokenType) -> None:
        """Logical operators should produce correct token types."""
        lexer = Lexer(source, "test.qsr")
        tokens = lexer.tokenize()
        assert tokens[0].type == expected
    
    def test_assignment_operator(self) -> None:
        """Assignment operator should produce EQUAL token."""
        lexer = Lexer("=", "test.qsr")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.EQUAL
    
    def test_arrow_operator(self) -> None:
        """Arrow operator should produce ARROW token."""
        lexer = Lexer("->", "test.qsr")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.ARROW


class TestPunctuation:
    """Test punctuation tokenization."""
    
    @pytest.mark.parametrize("source,expected", [
        ("(", TokenType.LPAREN),
        (")", TokenType.RPAREN),
        ("{", TokenType.LBRACE),
        ("}", TokenType.RBRACE),
        (":", TokenType.COLON),
        (",", TokenType.COMMA),
    ])
    def test_punctuation(self, source: str, expected: TokenType) -> None:
        """Punctuation should produce correct token types."""
        lexer = Lexer(source, "test.qsr")
        tokens = lexer.tokenize()
        assert tokens[0].type == expected


class TestLiterals:
    """Test literal tokenization."""
    
    @pytest.mark.parametrize("source,expected_value", [
        ("0", 0),
        ("42", 42),
        ("1000000", 1000000),
    ])
    def test_int_literals(self, source: str, expected_value: int) -> None:
        """Integer literals should have correct type and value."""
        lexer = Lexer(source, "test.qsr")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.INT_LITERAL
        assert tokens[0].literal == expected_value
    
    @pytest.mark.parametrize("source,expected_value", [
        ("3.14", 3.14),
        ("0.5", 0.5),
        ("100.0", 100.0),
    ])
    def test_float_literals(self, source: str, expected_value: float) -> None:
        """Float literals should have correct type and value."""
        lexer = Lexer(source, "test.qsr")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.FLOAT_LITERAL
        assert tokens[0].literal == expected_value
    
    @pytest.mark.parametrize("source,expected_value", [
        ('""', ""),
        ('"hello"', "hello"),
        ('"hello world"', "hello world"),
    ])
    def test_string_literals(self, source: str, expected_value: str) -> None:
        """String literals should have correct type and value."""
        lexer = Lexer(source, "test.qsr")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.STRING_LITERAL
        assert tokens[0].literal == expected_value
    
    def test_true_literal(self) -> None:
        """true should have boolean literal value True."""
        lexer = Lexer("true", "test.qsr")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TRUE
        assert tokens[0].literal is True
    
    def test_false_literal(self) -> None:
        """false should have boolean literal value False."""
        lexer = Lexer("false", "test.qsr")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.FALSE
        assert tokens[0].literal is False


class TestIdentifiers:
    """Test identifier tokenization."""
    
    @pytest.mark.parametrize("source", [
        "x",
        "myVar",
        "_private",
        "camelCase",
        "snake_case",
        "PascalCase",
        "var123",
        "_",
    ])
    def test_valid_identifiers(self, source: str) -> None:
        """Valid identifiers should produce IDENTIFIER tokens."""
        lexer = Lexer(source, "test.qsr")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].lexeme == source


class TestComments:
    """Test comment handling."""
    
    def test_comment_discarded(self) -> None:
        """Comments should be discarded, not producing tokens."""
        lexer = Lexer("# this is a comment", "test.qsr")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF
    
    def test_inline_comment(self) -> None:
        """Inline comments should be discarded after code."""
        lexer = Lexer("let x: int = 1  # comment", "test.qsr")
        tokens = lexer.tokenize()
        # Should have: LET, IDENTIFIER, COLON, INT, EQUAL, INT_LITERAL, EOF
        assert len(tokens) == 7
        assert tokens[-1].type == TokenType.EOF
    
    def test_multiline_with_comments(self) -> None:
        """Comments on multiple lines should all be discarded."""
        source = """# comment 1
let x: int = 1
# comment 2"""
        lexer = Lexer(source, "test.qsr")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens]
        assert TokenType.EOF in types
        # No comment tokens should exist


class TestWhitespace:
    """Test whitespace handling."""
    
    def test_spaces_ignored(self) -> None:
        """Spaces between tokens should be ignored."""
        lexer = Lexer("let    x   :   int", "test.qsr")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens[:-1]]
        assert types == [TokenType.LET, TokenType.IDENTIFIER, TokenType.COLON, TokenType.INT]
    
    def test_tabs_ignored(self) -> None:
        """Tabs should be ignored."""
        lexer = Lexer("let\tx:\tint", "test.qsr")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.LET
    
    def test_newlines_ignored(self) -> None:
        """Newlines should be ignored."""
        lexer = Lexer("let\nx:\nint", "test.qsr")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens[:-1]]
        assert types == [TokenType.LET, TokenType.IDENTIFIER, TokenType.COLON, TokenType.INT]


class TestCompleteStatements:
    """Test tokenization of complete statements."""
    
    def test_variable_declaration(self) -> None:
        """Variable declaration should produce correct token sequence."""
        lexer = Lexer("let x: int = 42", "test.qsr")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens]
        expected = [
            TokenType.LET,
            TokenType.IDENTIFIER,
            TokenType.COLON,
            TokenType.INT,
            TokenType.EQUAL,
            TokenType.INT_LITERAL,
            TokenType.EOF,
        ]
        assert types == expected
    
    def test_function_declaration(self) -> None:
        """Function declaration should produce correct token sequence."""
        source = "fn add(a: int, b: int) -> int { return a + b }"
        lexer = Lexer(source, "test.qsr")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens]
        expected = [
            TokenType.FN,
            TokenType.IDENTIFIER,  # add
            TokenType.LPAREN,
            TokenType.IDENTIFIER,  # a
            TokenType.COLON,
            TokenType.INT,
            TokenType.COMMA,
            TokenType.IDENTIFIER,  # b
            TokenType.COLON,
            TokenType.INT,
            TokenType.RPAREN,
            TokenType.ARROW,
            TokenType.INT,
            TokenType.LBRACE,
            TokenType.RETURN,
            TokenType.IDENTIFIER,  # a
            TokenType.PLUS,
            TokenType.IDENTIFIER,  # b
            TokenType.RBRACE,
            TokenType.EOF,
        ]
        assert types == expected
