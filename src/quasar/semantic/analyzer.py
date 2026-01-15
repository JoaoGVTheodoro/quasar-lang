"""
Semantic analyzer for Quasar.

Performs semantic analysis on a Quasar AST, including:
- Scope resolution (variable declaration and usage)
- Type checking (type compatibility, no implicit coercion)
- Control flow validation (break/continue only in loops, return validation)
"""

from typing import Optional

from quasar.ast import (
    # Program
    Program,
    # Declarations
    VarDecl,
    ConstDecl,
    FnDecl,
    Param,
    # Statements
    Block,
    ExpressionStmt,
    IfStmt,
    WhileStmt,
    ReturnStmt,
    BreakStmt,
    ContinueStmt,
    AssignStmt,
    # Expressions
    BinaryExpr,
    UnaryExpr,
    CallExpr,
    Identifier,
    IntLiteral,
    FloatLiteral,
    StringLiteral,
    BoolLiteral,
    # Types and operators
    TypeAnnotation,
    BinaryOp,
    UnaryOp,
    Span,
)
from quasar.semantic.errors import SemanticError
from quasar.semantic.symbols import Symbol, SymbolTable


class SemanticAnalyzer:
    """
    Performs semantic analysis on a Quasar AST.
    
    Validates:
    - Scope rules (declaration before use, no redeclaration in same scope)
    - Type rules (type compatibility, no implicit coercion)
    - Control flow rules (break/continue only in loops, return validation)
    """
    
    def __init__(self) -> None:
        """Initialize the semantic analyzer."""
        self._symbols = SymbolTable()
        self._loop_depth = 0  # Track nesting in while loops
        self._current_function_return_type: Optional[TypeAnnotation] = None
    
    def analyze(self, program: Program) -> Program:
        """
        Analyze a program and return it if valid.
        
        Raises SemanticError if any semantic violation is found.
        """
        for decl in program.declarations:
            self._analyze_declaration(decl)
        return program
    
    # =========================================================================
    # Declaration Analysis
    # =========================================================================
    
    def _analyze_declaration(self, decl) -> None:
        """Dispatch declaration analysis based on type."""
        if isinstance(decl, VarDecl):
            self._analyze_var_decl(decl)
        elif isinstance(decl, ConstDecl):
            self._analyze_const_decl(decl)
        elif isinstance(decl, FnDecl):
            self._analyze_fn_decl(decl)
        elif isinstance(decl, ExpressionStmt):
            self._analyze_expression_stmt(decl)
        elif isinstance(decl, IfStmt):
            self._analyze_if_stmt(decl)
        elif isinstance(decl, WhileStmt):
            self._analyze_while_stmt(decl)
        elif isinstance(decl, ReturnStmt):
            self._analyze_return_stmt(decl)
        elif isinstance(decl, BreakStmt):
            self._analyze_break_stmt(decl)
        elif isinstance(decl, ContinueStmt):
            self._analyze_continue_stmt(decl)
        elif isinstance(decl, AssignStmt):
            self._analyze_assign_stmt(decl)
        elif isinstance(decl, Block):
            self._analyze_block(decl)
    
    def _analyze_var_decl(self, decl: VarDecl) -> None:
        """
        Analyze variable declaration.
        
        Checks:
        - E0002: No redeclaration in same scope
        - E0100: Initializer type matches declared type
        """
        # Check initializer type
        init_type = self._get_expression_type(decl.initializer)
        if init_type != decl.type_annotation:
            raise SemanticError(
                code="E0100",
                message=f"type mismatch: expected {decl.type_annotation.name.lower()}, got {init_type.name.lower()}",
                span=decl.initializer.span,
            )
        
        # Try to define in current scope
        symbol = Symbol(
            name=decl.name,
            type_annotation=decl.type_annotation,
            is_const=False,
        )
        if not self._symbols.define(symbol):
            raise SemanticError(
                code="E0002",
                message=f"redeclaration of '{decl.name}' in the same scope",
                span=decl.span,
            )
    
    def _analyze_const_decl(self, decl: ConstDecl) -> None:
        """
        Analyze constant declaration.
        
        Checks:
        - E0002: No redeclaration in same scope
        - E0100: Initializer type matches declared type
        """
        # Check initializer type
        init_type = self._get_expression_type(decl.initializer)
        if init_type != decl.type_annotation:
            raise SemanticError(
                code="E0100",
                message=f"type mismatch: expected {decl.type_annotation.name.lower()}, got {init_type.name.lower()}",
                span=decl.initializer.span,
            )
        
        # Try to define in current scope
        symbol = Symbol(
            name=decl.name,
            type_annotation=decl.type_annotation,
            is_const=True,
        )
        if not self._symbols.define(symbol):
            raise SemanticError(
                code="E0002",
                message=f"redeclaration of '{decl.name}' in the same scope",
                span=decl.span,
            )
    
    def _analyze_fn_decl(self, decl: FnDecl) -> None:
        """
        Analyze function declaration.
        
        Checks:
        - E0002: No redeclaration of function name
        - Parameters and body in new scope
        """
        # Register function in current scope
        symbol = Symbol(
            name=decl.name,
            type_annotation=decl.return_type,
            is_const=True,  # Functions cannot be reassigned
            is_function=True,
        )
        if not self._symbols.define(symbol):
            raise SemanticError(
                code="E0002",
                message=f"redeclaration of '{decl.name}' in the same scope",
                span=decl.span,
            )
        
        # Enter function scope
        self._symbols.enter_scope()
        
        # Save and set current function return type
        prev_return_type = self._current_function_return_type
        self._current_function_return_type = decl.return_type
        
        # Define parameters in function scope
        for param in decl.params:
            param_symbol = Symbol(
                name=param.name,
                type_annotation=param.type_annotation,
                is_const=False,
            )
            # Parameters should not conflict in same scope
            if not self._symbols.define(param_symbol):
                raise SemanticError(
                    code="E0002",
                    message=f"redeclaration of parameter '{param.name}'",
                    span=param.span,
                )
        
        # Analyze function body (without entering another scope - Block will do it)
        # But Block creates its own scope, so we need to analyze declarations directly
        for stmt in decl.body.declarations:
            self._analyze_declaration(stmt)
        
        # Restore previous context
        self._current_function_return_type = prev_return_type
        self._symbols.exit_scope()
    
    # =========================================================================
    # Statement Analysis
    # =========================================================================
    
    def _analyze_block(self, block: Block) -> None:
        """Analyze a block, creating a new scope."""
        self._symbols.enter_scope()
        for decl in block.declarations:
            self._analyze_declaration(decl)
        self._symbols.exit_scope()
    
    def _analyze_expression_stmt(self, stmt: ExpressionStmt) -> None:
        """Analyze an expression statement."""
        self._get_expression_type(stmt.expression)
    
    def _analyze_if_stmt(self, stmt: IfStmt) -> None:
        """
        Analyze if statement.
        
        Checks:
        - E0101: Condition must be boolean
        """
        cond_type = self._get_expression_type(stmt.condition)
        if cond_type != TypeAnnotation.BOOL:
            raise SemanticError(
                code="E0101",
                message=f"condition must be bool, got {cond_type.name.lower()}",
                span=stmt.condition.span,
            )
        
        # Analyze then block
        self._analyze_block(stmt.then_block)
        
        # Analyze else block if present
        if stmt.else_block is not None:
            self._analyze_block(stmt.else_block)
    
    def _analyze_while_stmt(self, stmt: WhileStmt) -> None:
        """
        Analyze while statement.
        
        Checks:
        - E0101: Condition must be boolean
        """
        cond_type = self._get_expression_type(stmt.condition)
        if cond_type != TypeAnnotation.BOOL:
            raise SemanticError(
                code="E0101",
                message=f"condition must be bool, got {cond_type.name.lower()}",
                span=stmt.condition.span,
            )
        
        # Enter loop context
        self._loop_depth += 1
        self._analyze_block(stmt.body)
        self._loop_depth -= 1
    
    def _analyze_return_stmt(self, stmt: ReturnStmt) -> None:
        """
        Analyze return statement.
        
        Checks:
        - E0302: Return type must match function return type
        """
        if self._current_function_return_type is None:
            # Not inside a function - shouldn't happen with valid parse
            return
        
        return_type = self._get_expression_type(stmt.value)
        if return_type != self._current_function_return_type:
            raise SemanticError(
                code="E0302",
                message=f"return type mismatch: expected {self._current_function_return_type.name.lower()}, got {return_type.name.lower()}",
                span=stmt.value.span,
            )
    
    def _analyze_break_stmt(self, stmt: BreakStmt) -> None:
        """
        Analyze break statement.
        
        Checks:
        - E0200: break must be inside a loop
        """
        if self._loop_depth == 0:
            raise SemanticError(
                code="E0200",
                message="'break' outside of loop",
                span=stmt.span,
            )
    
    def _analyze_continue_stmt(self, stmt: ContinueStmt) -> None:
        """
        Analyze continue statement.
        
        Checks:
        - E0201: continue must be inside a loop
        """
        if self._loop_depth == 0:
            raise SemanticError(
                code="E0201",
                message="'continue' outside of loop",
                span=stmt.span,
            )
    
    def _analyze_assign_stmt(self, stmt: AssignStmt) -> None:
        """
        Analyze assignment statement.
        
        Checks:
        - E0001: Target must be declared
        - E0003: Target must not be const
        - E0100: Value type must match target type
        """
        symbol = self._symbols.lookup(stmt.target)
        if symbol is None:
            raise SemanticError(
                code="E0001",
                message=f"use of undeclared identifier '{stmt.target}'",
                span=stmt.span,
            )
        
        if symbol.is_const:
            raise SemanticError(
                code="E0003",
                message=f"cannot assign to constant '{stmt.target}'",
                span=stmt.span,
            )
        
        value_type = self._get_expression_type(stmt.value)
        if value_type != symbol.type_annotation:
            raise SemanticError(
                code="E0100",
                message=f"type mismatch: expected {symbol.type_annotation.name.lower()}, got {value_type.name.lower()}",
                span=stmt.value.span,
            )
    
    # =========================================================================
    # Expression Type Analysis
    # =========================================================================
    
    def _get_expression_type(self, expr) -> TypeAnnotation:
        """
        Determine the type of an expression.
        
        Also validates the expression for semantic errors.
        """
        if isinstance(expr, IntLiteral):
            return TypeAnnotation.INT
        elif isinstance(expr, FloatLiteral):
            return TypeAnnotation.FLOAT
        elif isinstance(expr, StringLiteral):
            return TypeAnnotation.STR
        elif isinstance(expr, BoolLiteral):
            return TypeAnnotation.BOOL
        elif isinstance(expr, Identifier):
            return self._get_identifier_type(expr)
        elif isinstance(expr, BinaryExpr):
            return self._get_binary_expr_type(expr)
        elif isinstance(expr, UnaryExpr):
            return self._get_unary_expr_type(expr)
        elif isinstance(expr, CallExpr):
            return self._get_call_expr_type(expr)
        else:
            # Should not reach here with valid AST
            raise SemanticError(
                code="E0000",
                message=f"unknown expression type: {type(expr).__name__}",
                span=expr.span,
            )
    
    def _get_identifier_type(self, expr: Identifier) -> TypeAnnotation:
        """
        Get the type of an identifier.
        
        Checks:
        - E0001: Identifier must be declared
        """
        symbol = self._symbols.lookup(expr.name)
        if symbol is None:
            raise SemanticError(
                code="E0001",
                message=f"use of undeclared identifier '{expr.name}'",
                span=expr.span,
            )
        return symbol.type_annotation
    
    def _get_binary_expr_type(self, expr: BinaryExpr) -> TypeAnnotation:
        """
        Get the type of a binary expression.
        
        Checks:
        - E0102: Operands must be compatible for arithmetic/concatenation
        - E0103: Operands must be compatible for comparison
        - E0104: Operands must be bool for logical operators
        """
        left_type = self._get_expression_type(expr.left)
        right_type = self._get_expression_type(expr.right)
        op = expr.operator
        
        # Logical operators: both operands must be bool
        if op in (BinaryOp.AND, BinaryOp.OR):
            if left_type != TypeAnnotation.BOOL:
                raise SemanticError(
                    code="E0104",
                    message=f"logical operator requires bool operands, got {left_type.name.lower()}",
                    span=expr.left.span,
                )
            if right_type != TypeAnnotation.BOOL:
                raise SemanticError(
                    code="E0104",
                    message=f"logical operator requires bool operands, got {right_type.name.lower()}",
                    span=expr.right.span,
                )
            return TypeAnnotation.BOOL
        
        # Equality operators: operands must be same type
        if op in (BinaryOp.EQ, BinaryOp.NE):
            if left_type != right_type:
                raise SemanticError(
                    code="E0102",
                    message=f"cannot compare {left_type.name.lower()} with {right_type.name.lower()}",
                    span=expr.span,
                )
            return TypeAnnotation.BOOL
        
        # Comparison operators: numeric types only, same type, no strings
        if op in (BinaryOp.LT, BinaryOp.GT, BinaryOp.LE, BinaryOp.GE):
            # Strings cannot use < > <= >=
            if left_type == TypeAnnotation.STR or right_type == TypeAnnotation.STR:
                raise SemanticError(
                    code="E0103",
                    message="string comparison with '<', '>', '<=', '>=' is not supported",
                    span=expr.span,
                )
            if left_type != right_type:
                raise SemanticError(
                    code="E0102",
                    message=f"cannot compare {left_type.name.lower()} with {right_type.name.lower()}",
                    span=expr.span,
                )
            if left_type not in (TypeAnnotation.INT, TypeAnnotation.FLOAT):
                raise SemanticError(
                    code="E0102",
                    message=f"comparison requires numeric types, got {left_type.name.lower()}",
                    span=expr.span,
                )
            return TypeAnnotation.BOOL
        
        # Arithmetic operators: numeric types (same type) or string concatenation
        if op in (BinaryOp.ADD, BinaryOp.SUB, BinaryOp.MUL, BinaryOp.DIV, BinaryOp.MOD):
            # String concatenation: only ADD is allowed
            if left_type == TypeAnnotation.STR and right_type == TypeAnnotation.STR:
                if op == BinaryOp.ADD:
                    return TypeAnnotation.STR
                else:
                    raise SemanticError(
                        code="E0102",
                        message=f"operator '{op.name}' not supported for strings",
                        span=expr.span,
                    )
            
            # Mixed string and other type
            if left_type == TypeAnnotation.STR or right_type == TypeAnnotation.STR:
                raise SemanticError(
                    code="E0102",
                    message=f"cannot perform arithmetic between {left_type.name.lower()} and {right_type.name.lower()}",
                    span=expr.span,
                )
            
            # Mixed int and float (D-CF-5: PROHIBITED)
            if left_type != right_type:
                raise SemanticError(
                    code="E0102",
                    message=f"cannot mix {left_type.name.lower()} and {right_type.name.lower()} in arithmetic",
                    span=expr.span,
                )
            
            # Bool arithmetic not allowed
            if left_type == TypeAnnotation.BOOL:
                raise SemanticError(
                    code="E0102",
                    message="arithmetic operators not supported for bool",
                    span=expr.span,
                )
            
            return left_type
        
        # Should not reach here
        raise SemanticError(
            code="E0000",
            message=f"unknown binary operator: {op}",
            span=expr.span,
        )
    
    def _get_unary_expr_type(self, expr: UnaryExpr) -> TypeAnnotation:
        """
        Get the type of a unary expression.
        
        Checks:
        - E0104: NOT requires bool operand
        - NEG requires numeric operand
        """
        operand_type = self._get_expression_type(expr.operand)
        
        if expr.operator == UnaryOp.NOT:
            if operand_type != TypeAnnotation.BOOL:
                raise SemanticError(
                    code="E0104",
                    message=f"logical NOT requires bool operand, got {operand_type.name.lower()}",
                    span=expr.operand.span,
                )
            return TypeAnnotation.BOOL
        
        if expr.operator == UnaryOp.NEG:
            if operand_type not in (TypeAnnotation.INT, TypeAnnotation.FLOAT):
                raise SemanticError(
                    code="E0102",
                    message=f"negation requires numeric type, got {operand_type.name.lower()}",
                    span=expr.operand.span,
                )
            return operand_type
        
        raise SemanticError(
            code="E0000",
            message=f"unknown unary operator: {expr.operator}",
            span=expr.span,
        )
    
    def _get_call_expr_type(self, expr: CallExpr) -> TypeAnnotation:
        """
        Get the type of a function call expression.
        
        Checks:
        - E0001: Function must be declared
        """
        symbol = self._symbols.lookup(expr.callee)
        if symbol is None:
            raise SemanticError(
                code="E0001",
                message=f"use of undeclared function '{expr.callee}'",
                span=expr.span,
            )
        
        # Validate arguments (get their types to check for errors)
        for arg in expr.arguments:
            self._get_expression_type(arg)
        
        return symbol.type_annotation
