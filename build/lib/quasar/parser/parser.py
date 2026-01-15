"""
Quasar Parser — Main parser implementation.

This module implements a recursive descent parser that converts
a sequence of tokens into an Abstract Syntax Tree (AST) according
to the Phase 1 grammar specification.

Grammar (Phase 1 FROZEN):

    program     → declaration* EOF

    declaration → var_decl
                | const_decl
                | fn_decl
                | statement

    var_decl    → "let" IDENT ":" type "=" expression
    const_decl  → "const" IDENT ":" type "=" expression
    fn_decl     → "fn" IDENT "(" param_list? ")" "->" type block

    param_list  → param ("," param)*
    param       → IDENT ":" type

    type        → "int" | "float" | "bool" | "str"

    statement   → expr_stmt
                | if_stmt
                | while_stmt
                | return_stmt
                | break_stmt
                | continue_stmt
                | assign_stmt
                | block

    if_stmt     → "if" expression block ("else" block)?
    while_stmt  → "while" expression block
    return_stmt → "return" expression
    break_stmt  → "break"
    continue_stmt → "continue"
    assign_stmt → IDENT "=" expression
    block       → "{" declaration* "}"

    expression  → logic_or
    logic_or    → logic_and ("||" logic_and)*
    logic_and   → equality ("&&" equality)*
    equality    → comparison (("==" | "!=") comparison)*
    comparison  → term (("<" | ">" | "<=" | ">=") term)*
    term        → factor (("+" | "-") factor)*
    factor      → unary (("*" | "/" | "%") unary)*
    unary       → ("!" | "-") unary | call
    call        → primary ("(" arg_list? ")")?
    arg_list    → expression ("," expression)*
    primary     → INT | FLOAT | STRING | "true" | "false" | IDENT | "(" expression ")"

Precedence (lowest to highest):
    1. || (left)
    2. && (left)
    3. == != (left)
    4. < > <= >= (left)
    5. + - (left)
    6. * / % (left)
    7. ! - unary (right)
    8. call () (left)
"""

from quasar.ast.span import Span
from quasar.ast.types import (
    TypeAnnotation,
    QuasarType,
    PrimitiveType,
    ListType,
    INT,
    FLOAT,
    BOOL,
    STR,
)
from quasar.ast.operators import BinaryOp, UnaryOp
from quasar.ast.base import Declaration, Expression, Statement
from quasar.ast.expressions import (
    BinaryExpr,
    UnaryExpr,
    CallExpr,
    Identifier,
    IntLiteral,
    FloatLiteral,
    StringLiteral,
    BoolLiteral,
    ListLiteral,
    IndexExpr,
    RangeExpr,
    FieldInit,
    StructInitExpr,
    MemberAccessExpr,
)
from quasar.ast.statements import (
    Block,
    ExpressionStmt,
    IfStmt,
    WhileStmt,
    ReturnStmt,
    BreakStmt,
    ContinueStmt,
    AssignStmt,
    PrintStmt,
    IndexAssignStmt,
    ForStmt,
    MemberAssignStmt,
)
from quasar.ast.declarations import (
    Param,
    VarDecl,
    ConstDecl,
    FnDecl,
    StructDecl,
    StructField,
)
from quasar.ast.program import Program

from quasar.lexer.token import Token
from quasar.lexer.token_type import TokenType

from quasar.parser.errors import ParserError


class Parser:
    """
    Recursive descent parser for Quasar.
    
    Converts a sequence of tokens into an AST.
    
    Usage:
        parser = Parser(tokens)
        program = parser.parse()
    """
    
    def __init__(self, tokens: list[Token]) -> None:
        """
        Initialize the parser.
        
        Args:
            tokens: List of tokens from the lexer.
        """
        self._tokens = tokens
        self._current = 0
    
    def parse(self) -> Program:
        """
        Parse the token stream into a Program AST.
        
        Returns:
            The root Program node.
        
        Raises:
            ParserError: If there is a syntax error.
        """
        declarations: list[Declaration] = []
        
        start_span = self._peek().span
        
        while not self._is_at_end():
            decl = self._declaration()
            declarations.append(decl)
        
        end_span = self._previous().span
        
        return Program(
            declarations=declarations,
            span=self._merge_spans(start_span, end_span),
        )
    
    # =========================================================================
    # Token navigation
    # =========================================================================
    
    def _peek(self) -> Token:
        """Return current token without consuming it."""
        return self._tokens[self._current]
    
    def _peek_next(self) -> Token:
        """Return next token without consuming current one (lookahead)."""
        if self._current + 1 >= len(self._tokens):
            return self._tokens[-1]  # Return EOF
        return self._tokens[self._current + 1]

    def _peek_n(self, n: int) -> Token:
        """Return token n positions ahead without consuming (extended lookahead)."""
        if self._current + n >= len(self._tokens):
            return self._tokens[-1]  # Return EOF
        return self._tokens[self._current + n]
    
    def _previous(self) -> Token:
        """Return the most recently consumed token."""
        return self._tokens[self._current - 1]
    
    def _is_at_end(self) -> bool:
        """Check if we've reached EOF."""
        return self._peek().type == TokenType.EOF
    
    def _advance(self) -> Token:
        """Consume and return the current token."""
        if not self._is_at_end():
            self._current += 1
        return self._previous()
    
    def _check(self, *types: TokenType) -> bool:
        """Check if current token is of any given type."""
        if self._is_at_end():
            return False
        return self._peek().type in types
    
    def _match(self, *types: TokenType) -> bool:
        """
        If current token matches any of the types, consume it.
        
        Returns:
            True if matched and consumed, False otherwise.
        """
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False
    
    def _consume(self, token_type: TokenType, message: str) -> Token:
        """
        Consume current token if it matches, otherwise error.
        
        Args:
            token_type: Expected token type.
            message: Error message if token doesn't match.
        
        Returns:
            The consumed token.
        
        Raises:
            ParserError: If token doesn't match.
        """
        if self._check(token_type):
            return self._advance()
        
        raise ParserError(
            message=message,
            span=self._peek().span,
        )
    
    def _error(self, message: str) -> ParserError:
        """Create a parser error at current position."""
        return ParserError(message=message, span=self._peek().span)
    
    def _merge_spans(self, start: Span, end: Span) -> Span:
        """Create a span covering from start to end."""
        return Span(
            start_line=start.start_line,
            start_column=start.start_column,
            end_line=end.end_line,
            end_column=end.end_column,
            file=start.file,
        )
    
    # =========================================================================
    # Declarations
    # =========================================================================
    
    def _declaration(self) -> Declaration:
        """
        Parse a declaration.
        
        declaration → var_decl | const_decl | fn_decl | statement
        """
        if self._check(TokenType.LET):
            return self._var_decl()
        if self._check(TokenType.CONST):
            return self._const_decl()
        if self._check(TokenType.FN):
            return self._fn_decl()
        if self._check(TokenType.STRUCT):
            return self._struct_decl()
        return self._statement()
    
    def _var_decl(self) -> VarDecl:
        """
        Parse a variable declaration.
        
        var_decl → "let" IDENT ":" type "=" expression
        """
        start = self._advance()  # consume 'let'
        
        name_token = self._consume(TokenType.IDENTIFIER, "expected variable name after 'let'")
        name = name_token.lexeme
        
        self._consume(TokenType.COLON, "expected ':' after variable name")
        
        type_ann = self._type_annotation()
        
        self._consume(TokenType.EQUAL, "expected '=' in variable declaration")
        
        initializer = self._expression()
        
        return VarDecl(
            name=name,
            type_annotation=type_ann,
            initializer=initializer,
            span=self._merge_spans(start.span, initializer.span),
        )
    
    def _const_decl(self) -> ConstDecl:
        """
        Parse a constant declaration.
        
        const_decl → "const" IDENT ":" type "=" expression
        """
        start = self._advance()  # consume 'const'
        
        name_token = self._consume(TokenType.IDENTIFIER, "expected constant name after 'const'")
        name = name_token.lexeme
        
        self._consume(TokenType.COLON, "expected ':' after constant name")
        
        type_ann = self._type_annotation()
        
        self._consume(TokenType.EQUAL, "expected '=' in constant declaration")
        
        initializer = self._expression()
        
        return ConstDecl(
            name=name,
            type_annotation=type_ann,
            initializer=initializer,
            span=self._merge_spans(start.span, initializer.span),
        )
    
    def _fn_decl(self) -> FnDecl:
        """
        Parse a function declaration.
        
        fn_decl → "fn" IDENT "(" param_list? ")" "->" type block
        """
        start = self._advance()  # consume 'fn'
        
        name_token = self._consume(TokenType.IDENTIFIER, "expected function name after 'fn'")
        name = name_token.lexeme
        
        self._consume(TokenType.LPAREN, "expected '(' after function name")
        
        params: list[Param] = []
        if not self._check(TokenType.RPAREN):
            params = self._param_list()
        
        self._consume(TokenType.RPAREN, "expected ')' after parameters")
        
        self._consume(TokenType.ARROW, "expected '->' after parameters")
        
        return_type = self._type_annotation()
        
        body = self._block()
        
        return FnDecl(
            name=name,
            params=params,
            return_type=return_type,
            body=body,
            span=self._merge_spans(start.span, body.span),
        )
    
    def _param_list(self) -> list[Param]:
        """
        Parse a parameter list.
        
        param_list → param ("," param)*
        """
        params: list[Param] = [self._param()]
        
        while self._match(TokenType.COMMA):
            params.append(self._param())
        
        return params
    
    def _param(self) -> Param:
        """
        Parse a single parameter.
        
        param → IDENT ":" type
        """
        name_token = self._consume(TokenType.IDENTIFIER, "expected parameter name")
        name = name_token.lexeme
        start = name_token.span
        
        self._consume(TokenType.COLON, "expected ':' after parameter name")
        
        type_ann = self._type_annotation()
        type_span = self._previous().span
        
        return Param(
            name=name,
            type_annotation=type_ann,
            span=self._merge_spans(start, type_span),
        )
    
    def _type_annotation(self) -> "QuasarType":
        """
        Parse a type annotation.
        
        type → primitive_type | list_type | struct_type
        primitive_type → "int" | "float" | "bool" | "str"
        list_type → "[" type "]"
        struct_type → IDENTIFIER
        """
        # List type: [T]
        if self._match(TokenType.LBRACKET):
            element_type = self._type_annotation()
            self._consume(TokenType.RBRACKET, "expected ']' after list element type")
            return ListType(element_type)
        
        # Primitive types
        if self._match(TokenType.INT):
            return INT
        if self._match(TokenType.FLOAT):
            return FLOAT
        if self._match(TokenType.BOOL):
            return BOOL
        if self._match(TokenType.STR):
            return STR
        
        # Custom struct type (identifier)
        if self._match(TokenType.IDENTIFIER):
            token = self._previous()
            # Use PrimitiveType as a stand-in for struct types
            # The semantic analyzer will validate this is a real struct
            return PrimitiveType(token.lexeme)
        
        raise self._error("expected type name")
    
    # =========================================================================
    # Statements
    # =========================================================================
    
    def _statement(self) -> Statement:
        """
        Parse a statement.
        
        statement → if_stmt | while_stmt | for_stmt | return_stmt | break_stmt
                  | continue_stmt | print_stmt | block | assign_stmt 
                  | index_assign_stmt | expr_stmt
        """
        if self._check(TokenType.IF):
            return self._if_stmt()
        if self._check(TokenType.WHILE):
            return self._while_stmt()
        if self._check(TokenType.FOR):
            return self._for_stmt()
        if self._check(TokenType.RETURN):
            return self._return_stmt()
        if self._check(TokenType.BREAK):
            return self._break_stmt()
        if self._check(TokenType.CONTINUE):
            return self._continue_stmt()
        if self._check(TokenType.PRINT):
            return self._print_stmt()
        if self._check(TokenType.LBRACE):
            return self._block()
        
        # Assignments and expression statements share the same start
        # Parse as expression first, then check for '=' to determine type
        return self._assign_or_expr_stmt()
    
    def _assign_or_expr_stmt(self) -> Statement:
        """
        Parse either an assignment statement or expression statement.
        
        Handles:
        - IDENT "=" expr         → AssignStmt
        - IDENT "[" expr "]" "=" expr → IndexAssignStmt (Phase 6.1)
        - otherwise              → ExpressionStmt
        
        Strategy: Parse expression first, then check if followed by "=".
        """
        # Parse the left-hand side as an expression
        expr = self._expression()
        
        # Check if this is an assignment
        if self._match(TokenType.EQUAL):
            value = self._expression()
            
            if isinstance(expr, Identifier):
                # Simple variable assignment
                return AssignStmt(
                    target=expr.name,
                    value=value,
                    span=self._merge_spans(expr.span, value.span),
                )
            elif isinstance(expr, IndexExpr):
                # Index assignment (Phase 6.1)
                return IndexAssignStmt(
                    target=expr,
                    value=value,
                    span=self._merge_spans(expr.span, value.span),
                )
            elif isinstance(expr, MemberAccessExpr):
                # Member assignment (Phase 8.2)
                return MemberAssignStmt(
                    object=expr.object,
                    member=expr.member,
                    value=value,
                    span=self._merge_spans(expr.span, value.span),
                )
            else:
                raise ParserError(
                    message="invalid assignment target",
                    span=expr.span,
                )
        
        # Otherwise it's an expression statement
        return ExpressionStmt(
            expression=expr,
            span=expr.span,
        )
    
    def _if_stmt(self) -> IfStmt:
        """
        Parse an if statement.
        
        if_stmt → "if" expression block ("else" block)?
        """
        start = self._advance()  # consume 'if'
        
        condition = self._expression()
        
        then_block = self._block()
        
        else_block: Block | None = None
        if self._match(TokenType.ELSE):
            else_block = self._block()
        
        end_span = else_block.span if else_block else then_block.span
        
        return IfStmt(
            condition=condition,
            then_block=then_block,
            else_block=else_block,
            span=self._merge_spans(start.span, end_span),
        )
    
    def _while_stmt(self) -> WhileStmt:
        """
        Parse a while statement.
        
        while_stmt → "while" expression block
        """
        start = self._advance()  # consume 'while'
        
        condition = self._expression()
        
        body = self._block()
        
        return WhileStmt(
            condition=condition,
            body=body,
            span=self._merge_spans(start.span, body.span),
        )
    
    def _for_stmt(self) -> ForStmt:
        """
        Parse a for statement (Phase 6.3).
        
        for_stmt → "for" IDENT "in" expression block
        
        The expression can be:
        - A range: 0..10, start..end
        - A list: [1, 2, 3], my_list
        """
        start = self._advance()  # consume 'for'
        
        # Parse iteration variable
        var_token = self._consume(TokenType.IDENTIFIER, "expected variable name after 'for'")
        variable = var_token.lexeme
        
        # Parse 'in' keyword
        self._consume(TokenType.IN, "expected 'in' after variable name")
        
        # Parse iterable expression (could be range or list)
        iterable = self._expression()
        
        # Parse body
        body = self._block()
        
        return ForStmt(
            variable=variable,
            iterable=iterable,
            body=body,
            span=self._merge_spans(start.span, body.span),
        )
    
    def _return_stmt(self) -> ReturnStmt:
        """
        Parse a return statement.
        
        return_stmt → "return" expression
        """
        start = self._advance()  # consume 'return'
        
        value = self._expression()
        
        return ReturnStmt(
            value=value,
            span=self._merge_spans(start.span, value.span),
        )
    
    def _break_stmt(self) -> BreakStmt:
        """
        Parse a break statement.
        
        break_stmt → "break"
        """
        token = self._advance()  # consume 'break'
        return BreakStmt(span=token.span)
    
    def _continue_stmt(self) -> ContinueStmt:
        """
        Parse a continue statement.
        
        continue_stmt → "continue"
        """
        token = self._advance()  # consume 'continue'
        return ContinueStmt(span=token.span)
    
    def _print_stmt(self) -> PrintStmt:
        """
        Parse a print statement (Phase 5 + 5.1).
        
        print_stmt → "print" "(" expression ("," expression)* print_kwargs? ")"
        print_kwargs → ("," print_kwarg)+
        print_kwarg → ("sep" | "end") "=" expression
        
        For backward compatibility, single-argument print still works.
        """
        start = self._advance()  # consume 'print'
        self._consume(TokenType.LPAREN, "expected '(' after 'print'")
        
        # Parse first argument (required)
        arguments: list = [self._expression()]
        sep_expr = None
        end_expr = None
        
        # Parse additional arguments and keyword parameters
        while self._match(TokenType.COMMA):
            # Check for keyword parameters (sep= or end=)
            if self._check(TokenType.SEP):
                self._advance()  # consume 'sep'
                self._consume(TokenType.EQUAL, "expected '=' after 'sep'")
                sep_expr = self._expression()
            elif self._check(TokenType.END):
                self._advance()  # consume 'end'
                self._consume(TokenType.EQUAL, "expected '=' after 'end'")
                end_expr = self._expression()
            else:
                # Regular positional argument
                arguments.append(self._expression())
        
        end_token = self._consume(TokenType.RPAREN, "expected ')' after print arguments")
        
        return PrintStmt(
            arguments=arguments,
            sep=sep_expr,
            end=end_expr,
            span=self._merge_spans(start.span, end_token.span),
        )
    
    def _block(self) -> Block:
        """
        Parse a block.
        
        block → "{" declaration* "}"
        """
        start = self._consume(TokenType.LBRACE, "expected '{'")
        
        declarations: list[Declaration] = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            declarations.append(self._declaration())
        
        end = self._consume(TokenType.RBRACE, "expected '}' after block")
        
        return Block(
            declarations=declarations,
            span=self._merge_spans(start.span, end.span),
        )
    
    def _expr_stmt(self) -> ExpressionStmt:
        """
        Parse an expression statement.
        
        expr_stmt → expression
        """
        expr = self._expression()
        return ExpressionStmt(
            expression=expr,
            span=expr.span,
        )
    
    # =========================================================================
    # Expressions (precedence climbing)
    # =========================================================================
    
    def _expression(self) -> Expression:
        """
        Parse an expression.
        
        expression → range_expr
        range_expr → logic_or (".." logic_or)?
        
        Range has lowest precedence and is NOT left-associative
        (you can't write a..b..c).
        """
        return self._range_expr()
    
    def _range_expr(self) -> Expression:
        """
        Parse range expression (Phase 6.3).
        
        range_expr → logic_or (".." logic_or)?
        
        Precedence: 0 (lowest)
        Not associative (a..b..c is invalid)
        """
        left = self._logic_or()
        
        if self._match(TokenType.DOTDOT):
            right = self._logic_or()
            return RangeExpr(
                start=left,
                end=right,
                span=self._merge_spans(left.span, right.span),
            )
        
        return left
    
    def _logic_or(self) -> Expression:
        """
        Parse logical OR expression.
        
        logic_or → logic_and ("||" logic_and)*
        
        Precedence: 1 (lowest)
        Associativity: left
        """
        expr = self._logic_and()
        
        while self._match(TokenType.OR_OR):
            operator = BinaryOp.OR
            right = self._logic_and()
            expr = BinaryExpr(
                left=expr,
                operator=operator,
                right=right,
                span=self._merge_spans(expr.span, right.span),
            )
        
        return expr
    
    def _logic_and(self) -> Expression:
        """
        Parse logical AND expression.
        
        logic_and → equality ("&&" equality)*
        
        Precedence: 2
        Associativity: left
        """
        expr = self._equality()
        
        while self._match(TokenType.AND_AND):
            operator = BinaryOp.AND
            right = self._equality()
            expr = BinaryExpr(
                left=expr,
                operator=operator,
                right=right,
                span=self._merge_spans(expr.span, right.span),
            )
        
        return expr
    
    def _equality(self) -> Expression:
        """
        Parse equality expression.
        
        equality → comparison (("==" | "!=") comparison)*
        
        Precedence: 3
        Associativity: left
        """
        expr = self._comparison()
        
        while self._match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            op_token = self._previous()
            operator = BinaryOp.EQ if op_token.type == TokenType.EQUAL_EQUAL else BinaryOp.NE
            right = self._comparison()
            expr = BinaryExpr(
                left=expr,
                operator=operator,
                right=right,
                span=self._merge_spans(expr.span, right.span),
            )
        
        return expr
    
    def _comparison(self) -> Expression:
        """
        Parse comparison expression.
        
        comparison → term (("<" | ">" | "<=" | ">=") term)*
        
        Precedence: 4
        Associativity: left
        """
        expr = self._term()
        
        while self._match(TokenType.LESS, TokenType.GREATER, 
                          TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL):
            op_token = self._previous()
            operator = {
                TokenType.LESS: BinaryOp.LT,
                TokenType.GREATER: BinaryOp.GT,
                TokenType.LESS_EQUAL: BinaryOp.LE,
                TokenType.GREATER_EQUAL: BinaryOp.GE,
            }[op_token.type]
            right = self._term()
            expr = BinaryExpr(
                left=expr,
                operator=operator,
                right=right,
                span=self._merge_spans(expr.span, right.span),
            )
        
        return expr
    
    def _term(self) -> Expression:
        """
        Parse term expression (addition/subtraction).
        
        term → factor (("+" | "-") factor)*
        
        Precedence: 5
        Associativity: left
        """
        expr = self._factor()
        
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op_token = self._previous()
            operator = BinaryOp.ADD if op_token.type == TokenType.PLUS else BinaryOp.SUB
            right = self._factor()
            expr = BinaryExpr(
                left=expr,
                operator=operator,
                right=right,
                span=self._merge_spans(expr.span, right.span),
            )
        
        return expr
    
    def _factor(self) -> Expression:
        """
        Parse factor expression (multiplication/division/modulo).
        
        factor → unary (("*" | "/" | "%") unary)*
        
        Precedence: 6
        Associativity: left
        """
        expr = self._unary()
        
        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op_token = self._previous()
            operator = {
                TokenType.STAR: BinaryOp.MUL,
                TokenType.SLASH: BinaryOp.DIV,
                TokenType.PERCENT: BinaryOp.MOD,
            }[op_token.type]
            right = self._unary()
            expr = BinaryExpr(
                left=expr,
                operator=operator,
                right=right,
                span=self._merge_spans(expr.span, right.span),
            )
        
        return expr
    
    def _unary(self) -> Expression:
        """
        Parse unary expression.
        
        unary → ("!" | "-") unary | call
        
        Precedence: 7
        Associativity: right
        """
        if self._match(TokenType.BANG, TokenType.MINUS):
            op_token = self._previous()
            operator = UnaryOp.NOT if op_token.type == TokenType.BANG else UnaryOp.NEG
            operand = self._unary()  # Right associative
            return UnaryExpr(
                operator=operator,
                operand=operand,
                span=self._merge_spans(op_token.span, operand.span),
            )
        
        return self._call()
    
    def _call(self) -> Expression:
        """
        Parse call and index expression.
        
        call → primary ( "(" arg_list? ")" | "[" expression "]" )*
        
        Precedence: 8
        Associativity: left
        
        Handles both function calls and index access (Phase 6.1).
        Supports chaining: matrix[0][1], list[0] + 1, etc.
        """
        expr = self._primary()
        
        while True:
            if self._match(TokenType.LPAREN):
                # Function call
                # Must be an identifier for a function call
                if not isinstance(expr, Identifier):
                    raise ParserError(
                        message="can only call functions",
                        span=expr.span,
                    )
                
                arguments: list[Expression] = []
                if not self._check(TokenType.RPAREN):
                    arguments = self._arg_list()
                
                end = self._consume(TokenType.RPAREN, "expected ')' after arguments")
                
                expr = CallExpr(
                    callee=expr.name,
                    arguments=arguments,
                    span=self._merge_spans(expr.span, end.span),
                )
            elif self._match(TokenType.LBRACKET):
                # Index access (Phase 6.1)
                index = self._expression()
                end = self._consume(TokenType.RBRACKET, "expected ']' after index")
                
                expr = IndexExpr(
                    target=expr,
                    index=index,
                    span=self._merge_spans(expr.span, end.span),
                )
            elif self._match(TokenType.DOT):
                # Member access (Phase 8.2)
                member_token = self._consume(TokenType.IDENTIFIER, "expected field name after '.'")
                
                expr = MemberAccessExpr(
                    object=expr,
                    member=member_token.lexeme,
                    span=self._merge_spans(expr.span, member_token.span),
                )
            else:
                break
        
        return expr
    
    def _arg_list(self) -> list[Expression]:
        """
        Parse argument list.
        
        arg_list → expression ("," expression)*
        """
        args: list[Expression] = [self._expression()]
        
        while self._match(TokenType.COMMA):
            args.append(self._expression())
        
        return args
    
    def _primary(self) -> Expression:
        """
        Parse primary expression.
        
        primary → INT | FLOAT | STRING | "true" | "false" | IDENT 
                | "(" expression ")" | list_literal
        
        list_literal → "[" (expression ("," expression)* ","?)? "]"
        
        Precedence: 9 (highest)
        """
        # Integer literal
        if self._match(TokenType.INT_LITERAL):
            token = self._previous()
            return IntLiteral(
                value=token.literal,  # type: ignore
                span=token.span,
            )
        
        # Float literal
        if self._match(TokenType.FLOAT_LITERAL):
            token = self._previous()
            return FloatLiteral(
                value=token.literal,  # type: ignore
                span=token.span,
            )
        
        # String literal
        if self._match(TokenType.STRING_LITERAL):
            token = self._previous()
            return StringLiteral(
                value=token.literal,  # type: ignore
                span=token.span,
            )
        
        # Boolean literals
        if self._match(TokenType.TRUE):
            token = self._previous()
            return BoolLiteral(
                value=True,
                span=token.span,
            )
        
        if self._match(TokenType.FALSE):
            token = self._previous()
            return BoolLiteral(
                value=False,
                span=token.span,
            )
        
        # Identifier or struct init
        if self._match(TokenType.IDENTIFIER):
            token = self._previous()
            # Check if this is a struct instantiation: Identifier { field: expr }
            # Must distinguish from Identifier followed by a block (e.g., in for..in expr { body })
            # Lookahead: struct init requires pattern: Identifier { Identifier : ...
            # Empty structs like `Identifier { }` are ambiguous with blocks - require at least one field
            if self._check(TokenType.LBRACE):
                # Look ahead to disambiguate - only match: { IDENT :
                next_token = self._peek_next()  # Token after {
                if next_token.type == TokenType.IDENTIFIER:
                    # Check if pattern is: { IDENT :
                    if self._peek_n(2).type == TokenType.COLON:
                        return self._struct_init(token)
            return Identifier(
                name=token.lexeme,
                span=token.span,
            )
        
        # Type keywords as function calls (Phase 7.1)
        # Allow int(), float(), str(), bool() as casting functions
        if self._check(TokenType.INT, TokenType.FLOAT, TokenType.STR, TokenType.BOOL):
            if self._peek_next().type == TokenType.LPAREN:
                # Consume the type keyword as an identifier
                token = self._advance()
                return Identifier(
                    name=token.lexeme,
                    span=token.span,
                )
        
        # Grouped expression
        if self._match(TokenType.LPAREN):
            start = self._previous()
            expr = self._expression()
            self._consume(TokenType.RPAREN, "expected ')' after expression")
            # Note: We don't create GroupExpr (D2.1) - parentheses are resolved here
            # But we preserve the span to cover the parentheses
            # Actually, per D2.1, we just return the inner expression
            return expr
        
        # List literal (Phase 6.0)
        if self._match(TokenType.LBRACKET):
            return self._list_literal()
        
        # Error: unexpected token
        raise self._error(f"expected expression, got '{self._peek().lexeme}'")
    
    def _list_literal(self) -> ListLiteral:
        """
        Parse a list literal expression.
        
        list_literal → "[" (expression ("," expression)* ","?)? "]"
        
        Called after "[" has been consumed.
        """
        start = self._previous()  # The "[" token
        elements: list[Expression] = []
        
        # Check for empty list
        if not self._check(TokenType.RBRACKET):
            # Parse first element
            elements.append(self._expression())
            
            # Parse remaining elements
            while self._match(TokenType.COMMA):
                # Allow trailing comma
                if self._check(TokenType.RBRACKET):
                    break
                elements.append(self._expression())
        
        self._consume(TokenType.RBRACKET, "expected ']' after list elements")
        end = self._previous()
        
        return ListLiteral(
            elements=elements,
            span=self._merge_spans(start.span, end.span),
        )

    def _struct_decl(self) -> StructDecl:
        """
        Parse a struct declaration.
        
        struct_decl → "struct" IDENT "{" (struct_fields)? "}"
        """
        start = self._advance()  # consume 'struct'
        
        name_token = self._consume(TokenType.IDENTIFIER, "expected struct name after 'struct'")
        name = name_token.lexeme
        
        self._consume(TokenType.LBRACE, "expected '{' after struct name")
        
        fields: list[StructField] = []
        if not self._check(TokenType.RBRACE):
            fields = self._struct_fields()
        
        end = self._consume(TokenType.RBRACE, "expected '}' after struct fields")
        
        return StructDecl(
            name=name,
            fields=fields,
            span=self._merge_spans(start.span, end.span),
        )
    
    def _struct_fields(self) -> list[StructField]:
        """
        Parse struct fields.
        
        (struct_field ("," struct_field)* ","?)?
        struct_field → IDENTIFIER ":" type
        """
        fields: list[StructField] = []
        
        # Parse first field
        fields.append(self._struct_field())
        
        # Parse subsequent fields
        while self._match(TokenType.COMMA):
            # Allow trailing comma
            if self._check(TokenType.RBRACE):
                break
            fields.append(self._struct_field())
        
        return fields
    
    def _struct_field(self) -> StructField:
        """
        Parse a single struct field.
        
        IDENTIFIER ":" type
        """
        name_token = self._consume(TokenType.IDENTIFIER, "expected field name")
        name = name_token.lexeme
        start = name_token.span
        
        self._consume(TokenType.COLON, "expected ':' after field name")
        
        type_ann = self._type_annotation()
        type_span = self._previous().span
        
        return StructField(
            name=name,
            type_annotation=type_ann,
            span=self._merge_spans(start, type_span),
        )

    def _struct_init(self, name_token: Token) -> StructInitExpr:
        """
        Parse struct instantiation expression.
        
        struct_init → IDENTIFIER "{" (field_init ("," field_init)* ","?)? "}"
        field_init → IDENTIFIER ":" expression
        
        Called after IDENTIFIER has been consumed and we've detected "{".
        """
        self._consume(TokenType.LBRACE, "expected '{' after struct name")
        
        fields: list[FieldInit] = []
        if not self._check(TokenType.RBRACE):
            fields = self._struct_init_fields()
        
        end = self._consume(TokenType.RBRACE, "expected '}' after struct fields")
        
        return StructInitExpr(
            struct_name=name_token.lexeme,
            fields=fields,
            span=self._merge_spans(name_token.span, end.span),
        )

    def _struct_init_fields(self) -> list[FieldInit]:
        """
        Parse field initializations.
        
        (field_init ("," field_init)* ","?)?
        """
        fields: list[FieldInit] = []
        
        # Parse first field
        fields.append(self._field_init())
        
        # Parse subsequent fields
        while self._match(TokenType.COMMA):
            # Allow trailing comma
            if self._check(TokenType.RBRACE):
                break
            fields.append(self._field_init())
        
        return fields

    def _field_init(self) -> FieldInit:
        """
        Parse a single field initialization.
        
        IDENTIFIER ":" expression
        """
        name_token = self._consume(TokenType.IDENTIFIER, "expected field name")
        name = name_token.lexeme
        start = name_token.span
        
        self._consume(TokenType.COLON, "expected ':' after field name")
        
        value = self._expression()
        
        return FieldInit(
            name=name,
            value=value,
            span=self._merge_spans(start, value.span),
        )
