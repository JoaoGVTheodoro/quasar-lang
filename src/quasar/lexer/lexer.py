"""
Quasar Lexer — Main lexer implementation.

This module implements the Lexer class that converts Quasar source
code into a sequence of tokens according to the Phase 1 lexical specification.
"""

from quasar.ast.span import Span
from quasar.lexer.errors import LexerError
from quasar.lexer.token import Token
from quasar.lexer.token_type import KEYWORDS, TokenType


class Lexer:
    """
    Lexical analyzer for Quasar source code.
    
    Converts source text into a sequence of tokens.
    
    Usage:
        lexer = Lexer(source, filename)
        tokens = lexer.tokenize()
    
    Attributes:
        source: The source code to tokenize.
        filename: The name of the source file (for error reporting).
    """
    
    def __init__(self, source: str, filename: str = "<stdin>") -> None:
        """
        Initialize the lexer.
        
        Args:
            source: The source code to tokenize.
            filename: The name of the source file.
        """
        self._source = source
        self._filename = filename
        
        # Current position in source
        self._start = 0      # Start of current token
        self._current = 0    # Current character position
        self._line = 1       # Current line number (1-indexed)
        self._column = 1     # Current column number (1-indexed)
        
        # Position at start of current token
        self._start_line = 1
        self._start_column = 1
        
        # Collected tokens
        self._tokens: list[Token] = []
        
        # Collected errors
        self._errors: list[LexerError] = []
    
    def tokenize(self) -> list[Token]:
        """
        Tokenize the entire source code.
        
        Returns:
            A list of tokens, ending with EOF.
        
        Raises:
            LexerError: If there are lexical errors (first error is raised).
        """
        while not self._is_at_end():
            # Mark the start of the next token
            self._start = self._current
            self._start_line = self._line
            self._start_column = self._column
            
            self._scan_token()
        
        # Add EOF token
        self._tokens.append(Token(
            type=TokenType.EOF,
            lexeme="",
            literal=None,
            span=Span(
                start_line=self._line,
                start_column=self._column,
                end_line=self._line,
                end_column=self._column,
                file=self._filename,
            ),
        ))
        
        # If there were errors, raise the first one
        if self._errors:
            raise self._errors[0]
        
        return self._tokens
    
    def _is_at_end(self) -> bool:
        """Check if we've reached the end of source."""
        return self._current >= len(self._source)
    
    def _peek(self) -> str:
        """Look at current character without consuming it."""
        if self._is_at_end():
            return "\0"
        return self._source[self._current]
    
    def _peek_next(self) -> str:
        """Look at next character without consuming it."""
        if self._current + 1 >= len(self._source):
            return "\0"
        return self._source[self._current + 1]
    
    def _advance(self) -> str:
        """Consume and return the current character."""
        char = self._source[self._current]
        self._current += 1
        
        if char == "\n":
            self._line += 1
            self._column = 1
        else:
            self._column += 1
        
        return char
    
    def _match(self, expected: str) -> bool:
        """
        Consume current character if it matches expected.
        
        Returns:
            True if matched and consumed, False otherwise.
        """
        if self._is_at_end():
            return False
        if self._source[self._current] != expected:
            return False
        
        self._advance()
        return True
    
    def _make_span(self) -> Span:
        """Create a Span for the current token."""
        return Span(
            start_line=self._start_line,
            start_column=self._start_column,
            end_line=self._line,
            end_column=self._column - 1 if self._column > 1 else 1,
            file=self._filename,
        )
    
    def _add_token(self, token_type: TokenType, literal: int | float | str | bool | None = None) -> None:
        """Add a token to the list."""
        lexeme = self._source[self._start:self._current]
        self._tokens.append(Token(
            type=token_type,
            lexeme=lexeme,
            literal=literal,
            span=self._make_span(),
        ))
    
    def _error(self, message: str) -> None:
        """Record a lexical error."""
        self._errors.append(LexerError(
            message=message,
            span=self._make_span(),
        ))
    
    def _scan_token(self) -> None:
        """Scan a single token."""
        char = self._advance()
        
        match char:
            # Single-character tokens
            case "+":
                self._add_token(TokenType.PLUS)
            case "*":
                self._add_token(TokenType.STAR)
            case "/":
                self._add_token(TokenType.SLASH)
            case "%":
                self._add_token(TokenType.PERCENT)
            case "(":
                self._add_token(TokenType.LPAREN)
            case ")":
                self._add_token(TokenType.RPAREN)
            case "{":
                self._add_token(TokenType.LBRACE)
            case "}":
                self._add_token(TokenType.RBRACE)
            case ":":
                self._add_token(TokenType.COLON)
            case ",":
                self._add_token(TokenType.COMMA)
            
            # One or two character tokens
            case "-":
                if self._match(">"):
                    self._add_token(TokenType.ARROW)
                else:
                    self._add_token(TokenType.MINUS)
            
            case "=":
                if self._match("="):
                    self._add_token(TokenType.EQUAL_EQUAL)
                else:
                    self._add_token(TokenType.EQUAL)
            
            case "!":
                if self._match("="):
                    self._add_token(TokenType.BANG_EQUAL)
                else:
                    self._add_token(TokenType.BANG)
            
            case "<":
                if self._match("="):
                    self._add_token(TokenType.LESS_EQUAL)
                else:
                    self._add_token(TokenType.LESS)
            
            case ">":
                if self._match("="):
                    self._add_token(TokenType.GREATER_EQUAL)
                else:
                    self._add_token(TokenType.GREATER)
            
            case "&":
                if self._match("&"):
                    self._add_token(TokenType.AND_AND)
                else:
                    self._error(f"unexpected character '&'; did you mean '&&'?")
            
            case "|":
                if self._match("|"):
                    self._add_token(TokenType.OR_OR)
                else:
                    self._error(f"unexpected character '|'; did you mean '||'?")
            
            # Comment (discard until end of line)
            case "#":
                while self._peek() != "\n" and not self._is_at_end():
                    self._advance()
            
            # Whitespace (ignore)
            case " " | "\t" | "\r" | "\n":
                pass
            
            # String literal
            case '"':
                self._scan_string()
            
            # Number literal
            case _ if char.isdigit():
                self._scan_number()
            
            # Identifier or keyword
            case _ if char.isalpha() or char == "_":
                self._scan_identifier()
            
            # Unknown character
            case _:
                self._error(f"unexpected character '{char}'")
    
    def _scan_string(self) -> None:
        """Scan a string literal."""
        start_line = self._start_line
        start_column = self._start_column
        
        # Consume characters until closing quote or end of input
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == "\n":
                # Strings cannot span multiple lines (no escape sequences)
                self._error("unterminated string literal")
                return
            self._advance()
        
        if self._is_at_end():
            self._error("unterminated string literal")
            return
        
        # Consume the closing quote
        self._advance()
        
        # Extract the string value (without quotes)
        value = self._source[self._start + 1:self._current - 1]
        self._add_token(TokenType.STRING_LITERAL, value)
    
    def _scan_number(self) -> None:
        """Scan an integer or float literal."""
        # Consume all digits
        while self._peek().isdigit():
            self._advance()
        
        # Check for decimal point
        if self._peek() == "." and self._peek_next().isdigit():
            # Consume the dot
            self._advance()
            
            # Consume fractional digits
            while self._peek().isdigit():
                self._advance()
            
            # It's a float
            value = float(self._source[self._start:self._current])
            self._add_token(TokenType.FLOAT_LITERAL, value)
        else:
            # It's an integer
            value = int(self._source[self._start:self._current])
            self._add_token(TokenType.INT_LITERAL, value)
    
    def _scan_identifier(self) -> None:
        """Scan an identifier or keyword."""
        # Consume alphanumeric characters and underscores
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()
        
        # Check if it's a keyword
        text = self._source[self._start:self._current]
        token_type = KEYWORDS.get(text)
        
        if token_type is not None:
            # It's a keyword
            # For true/false, also set the literal value
            if token_type == TokenType.TRUE:
                self._add_token(token_type, True)
            elif token_type == TokenType.FALSE:
                self._add_token(token_type, False)
            else:
                self._add_token(token_type)
        else:
            # It's an identifier
            self._add_token(TokenType.IDENTIFIER)
