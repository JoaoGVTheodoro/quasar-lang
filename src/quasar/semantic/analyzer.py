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
    ForStmt,
    ReturnStmt,
    BreakStmt,
    ContinueStmt,
    AssignStmt,
    PrintStmt,
    IndexAssignStmt,
    # Expressions
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
    # Types and operators
    TypeAnnotation,
    QuasarType,
    PrimitiveType,
    ListType,
    INT,
    FLOAT,
    BOOL,
    STR,
    VOID,
    is_list,
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
    
    @staticmethod
    def _types_compatible(expected: QuasarType, actual: QuasarType) -> bool:
        """
        Check if actual type is compatible with expected type.
        
        Special case: empty list [void] is compatible with any list type [T].
        """
        if expected == actual:
            return True
        # Empty list ([void]) is compatible with any list type
        if isinstance(expected, ListType) and isinstance(actual, ListType):
            if actual.element_type == VOID:
                return True
        return False
    
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
        elif isinstance(decl, ForStmt):
            self._analyze_for_stmt(decl)
        elif isinstance(decl, ReturnStmt):
            self._analyze_return_stmt(decl)
        elif isinstance(decl, BreakStmt):
            self._analyze_break_stmt(decl)
        elif isinstance(decl, ContinueStmt):
            self._analyze_continue_stmt(decl)
        elif isinstance(decl, PrintStmt):
            self._analyze_print_stmt(decl)
        elif isinstance(decl, AssignStmt):
            self._analyze_assign_stmt(decl)
        elif isinstance(decl, IndexAssignStmt):
            self._analyze_index_assign_stmt(decl)
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
        if not self._types_compatible(decl.type_annotation, init_type):
            raise SemanticError(
                code="E0100",
                message=f"type mismatch: expected {decl.type_annotation}, got {init_type}",
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
        if not self._types_compatible(decl.type_annotation, init_type):
            raise SemanticError(
                code="E0100",
                message=f"type mismatch: expected {decl.type_annotation}, got {init_type}",
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
        if cond_type != BOOL:
            raise SemanticError(
                code="E0101",
                message=f"condition must be bool, got {cond_type}",
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
        if cond_type != BOOL:
            raise SemanticError(
                code="E0101",
                message=f"condition must be bool, got {cond_type}",
                span=stmt.condition.span,
            )
        
        # Enter loop context
        self._loop_depth += 1
        self._analyze_block(stmt.body)
        self._loop_depth -= 1
    
    def _analyze_for_stmt(self, stmt: ForStmt) -> None:
        """
        Analyze for statement (Phase 6.3).
        
        Checks:
        - E0504: Range operands must be int
        - E0505: Iterable must be a range or list
        
        Creates a new scope with the loop variable.
        """
        # Determine the type of the iterable and the loop variable
        iterable = stmt.iterable
        
        if isinstance(iterable, RangeExpr):
            # Range expression: validate both ends are int
            start_type = self._get_expression_type(iterable.start)
            end_type = self._get_expression_type(iterable.end)
            
            if start_type != INT:
                raise SemanticError(
                    code="E0504",
                    message=f"range start must be int, got {start_type}",
                    span=iterable.start.span,
                )
            if end_type != INT:
                raise SemanticError(
                    code="E0504",
                    message=f"range end must be int, got {end_type}",
                    span=iterable.end.span,
                )
            
            # Loop variable is INT
            var_type = INT
        else:
            # Must be a list type
            iter_type = self._get_expression_type(iterable)
            
            if not isinstance(iter_type, ListType):
                raise SemanticError(
                    code="E0505",
                    message=f"cannot iterate over {iter_type}",
                    span=iterable.span,
                )
            
            # Loop variable is the element type of the list
            var_type = iter_type.element_type
        
        # Enter loop context and new scope
        self._loop_depth += 1
        self._symbols.enter_scope()
        
        # Define loop variable in scope (it's mutable like a let variable)
        self._symbols.define(Symbol(
            name=stmt.variable,
            type_annotation=var_type,
            is_const=False,  # Loop variable can be modified
        ))
        
        # Analyze body
        for decl in stmt.body.declarations:
            self._analyze_declaration(decl)
        
        # Exit scope and loop context
        self._symbols.exit_scope()
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
                message=f"return type mismatch: expected {self._current_function_return_type}, got {return_type}",
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
    
    def _analyze_print_stmt(self, stmt: PrintStmt) -> None:
        """
        Analyze print statement (Phase 5 + 5.1 + 5.2).
        
        Checks:
        - All arguments must be valid expressions
        - All argument types must be primitive (int, float, bool, str)
        - sep must be str type if provided
        - end must be str type if provided
        - Format string placeholder count must match argument count (Phase 5.2)
        
        Note: E0400 is reserved for future non-primitive types.
        Currently all types in Quasar are printable, so this check
        always passes for valid expressions.
        """
        # Validate all positional arguments
        for arg in stmt.arguments:
            self._get_expression_type(arg)
        
        # Validate format string placeholders (Phase 5.2)
        # Only applies when: 1) more than one arg, 2) first arg is StringLiteral, 3) has {} placeholder
        if len(stmt.arguments) > 1 and isinstance(stmt.arguments[0], StringLiteral):
            format_str = stmt.arguments[0].value
            # Count real {} placeholders (not escaped {{ or }})
            # Replace escaped braces first, then count
            temp = format_str.replace("{{", "").replace("}}", "")
            placeholder_count = temp.count("{}")
            
            # Only enforce if there's at least one placeholder (format mode)
            # No placeholder = normal mode (multi-arg print, no formatting)
            if placeholder_count > 0:
                arg_count = len(stmt.arguments) - 1  # Exclude format string itself
                
                if placeholder_count > arg_count:
                    raise SemanticError(
                        code="E0410",
                        message=f"format string has {placeholder_count} placeholder(s) but only {arg_count} argument(s) provided",
                        span=stmt.arguments[0].span,
                    )
                
                if placeholder_count < arg_count:
                    raise SemanticError(
                        code="E0411",
                        message=f"format string has {placeholder_count} placeholder(s) but {arg_count} argument(s) provided",
                        span=stmt.arguments[0].span,
                    )
        
        # Validate sep if provided (must be str)
        if stmt.sep is not None:
            sep_type = self._get_expression_type(stmt.sep)
            if sep_type != STR:
                raise SemanticError(
                    code="E0402",
                    message=f"'sep' parameter must be type 'str', got '{sep_type}'",
                    span=stmt.sep.span,
                )
        
        # Validate end if provided (must be str)
        if stmt.end is not None:
            end_type = self._get_expression_type(stmt.end)
            if end_type != STR:
                raise SemanticError(
                    code="E0403",
                    message=f"'end' parameter must be type 'str', got '{end_type}'",
                    span=stmt.end.span,
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
                message=f"type mismatch: expected {symbol.type_annotation}, got {value_type}",
                span=stmt.value.span,
            )
    
    def _analyze_index_assign_stmt(self, stmt: IndexAssignStmt) -> None:
        """
        Analyze index assignment statement (Phase 6.1).
        
        Checks:
        - E0501: Index must be int type
        - E0502: Target must be a list type
        - E0503: Value type must match element type
        """
        # Get the index expression (should be an IndexExpr)
        index_expr = stmt.target
        if not isinstance(index_expr, IndexExpr):
            raise SemanticError(
                code="E0502",
                message="invalid index assignment target",
                span=stmt.target.span,
            )
        
        # Get the type of the expression and validate (E0501, E0502)
        element_type = self._get_index_expr_type(index_expr)
        
        # Check value type matches element type (E0503)
        value_type = self._get_expression_type(stmt.value)
        if value_type != element_type:
            raise SemanticError(
                code="E0503",
                message=f"cannot assign '{value_type}' to list element of type '{element_type}'",
                span=stmt.value.span,
            )
    
    # =========================================================================
    # Expression Type Analysis
    # =========================================================================
    
    def _get_expression_type(self, expr) -> QuasarType:
        """
        Determine the type of an expression.
        
        Also validates the expression for semantic errors.
        """
        if isinstance(expr, IntLiteral):
            return INT
        elif isinstance(expr, FloatLiteral):
            return FLOAT
        elif isinstance(expr, StringLiteral):
            return STR
        elif isinstance(expr, BoolLiteral):
            return BOOL
        elif isinstance(expr, Identifier):
            return self._get_identifier_type(expr)
        elif isinstance(expr, BinaryExpr):
            return self._get_binary_expr_type(expr)
        elif isinstance(expr, UnaryExpr):
            return self._get_unary_expr_type(expr)
        elif isinstance(expr, CallExpr):
            return self._get_call_expr_type(expr)
        elif isinstance(expr, ListLiteral):
            return self._get_list_literal_type(expr)
        elif isinstance(expr, IndexExpr):
            return self._get_index_expr_type(expr)
        elif isinstance(expr, RangeExpr):
            # RangeExpr is validated in _analyze_for_stmt
            # If we get here, it's being used outside a for loop context
            # which is technically valid but the type is "range" (treated as list[int] for now)
            # Validate the operands are int
            start_type = self._get_expression_type(expr.start)
            end_type = self._get_expression_type(expr.end)
            if start_type != INT:
                raise SemanticError(
                    code="E0504",
                    message=f"range start must be int, got {start_type}",
                    span=expr.start.span,
                )
            if end_type != INT:
                raise SemanticError(
                    code="E0504",
                    message=f"range end must be int, got {end_type}",
                    span=expr.end.span,
                )
            # Return a marker type - range is iterable of int
            # We use ListType(INT) as a stand-in since ranges are int iterables
            return ListType(INT)
        else:
            # Should not reach here with valid AST
            raise SemanticError(
                code="E0000",
                message=f"unknown expression type: {type(expr).__name__}",
                span=expr.span,
            )
    
    def _get_list_literal_type(self, expr: ListLiteral) -> ListType:
        """
        Get the type of a list literal expression.
        
        Checks:
        - E0500: All elements must have the same type (homogeneous)
        
        Note: Empty lists require type annotation from context.
        """
        if len(expr.elements) == 0:
            # Empty list - type determined by annotation context
            # This will be resolved in _analyze_var_decl/_analyze_const_decl
            # For now, return a placeholder that will be matched against declared type
            return ListType(VOID)  # Placeholder for empty list
        
        # Get type of first element
        first_type = self._get_expression_type(expr.elements[0])
        
        # Check all other elements have the same type
        for i, elem in enumerate(expr.elements[1:], start=1):
            elem_type = self._get_expression_type(elem)
            if elem_type != first_type:
                raise SemanticError(
                    code="E0500",
                    message=f"heterogeneous list: element {i} has type '{elem_type}' but expected '{first_type}'",
                    span=elem.span,
                )
        
        return ListType(first_type)
    
    def _get_index_expr_type(self, expr: IndexExpr) -> QuasarType:
        """
        Get the type of an index expression (Phase 6.1).
        
        Checks:
        - E0501: Index must be int type
        - E0502: Target must be a list type
        
        Returns: The element type of the list
        """
        # Check index is int (E0501)
        index_type = self._get_expression_type(expr.index)
        if index_type != INT:
            raise SemanticError(
                code="E0501",
                message=f"list index must be 'int', got '{index_type}'",
                span=expr.index.span,
            )
        
        # Check target is a list (E0502)
        target_type = self._get_expression_type(expr.target)
        if not isinstance(target_type, ListType):
            raise SemanticError(
                code="E0502",
                message=f"cannot index into non-list type '{target_type}'",
                span=expr.target.span,
            )
        
        # Return the element type
        return target_type.element_type
    
    def _get_identifier_type(self, expr: Identifier) -> QuasarType:
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
    
    def _get_binary_expr_type(self, expr: BinaryExpr) -> QuasarType:
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
            if left_type != BOOL:
                raise SemanticError(
                    code="E0104",
                    message=f"logical operator requires bool operands, got {left_type}",
                    span=expr.left.span,
                )
            if right_type != BOOL:
                raise SemanticError(
                    code="E0104",
                    message=f"logical operator requires bool operands, got {right_type}",
                    span=expr.right.span,
                )
            return BOOL
        
        # Equality operators: operands must be same type
        if op in (BinaryOp.EQ, BinaryOp.NE):
            if left_type != right_type:
                raise SemanticError(
                    code="E0102",
                    message=f"cannot compare {left_type} with {right_type}",
                    span=expr.span,
                )
            return BOOL
        
        # Comparison operators: numeric types only, same type, no strings
        if op in (BinaryOp.LT, BinaryOp.GT, BinaryOp.LE, BinaryOp.GE):
            # Strings cannot use < > <= >=
            if left_type == STR or right_type == STR:
                raise SemanticError(
                    code="E0103",
                    message="string comparison with '<', '>', '<=', '>=' is not supported",
                    span=expr.span,
                )
            if left_type != right_type:
                raise SemanticError(
                    code="E0102",
                    message=f"cannot compare {left_type} with {right_type}",
                    span=expr.span,
                )
            if left_type not in (INT, FLOAT):
                raise SemanticError(
                    code="E0102",
                    message=f"comparison requires numeric types, got {left_type}",
                    span=expr.span,
                )
            return BOOL
        
        # Arithmetic operators: numeric types (same type) or string concatenation
        if op in (BinaryOp.ADD, BinaryOp.SUB, BinaryOp.MUL, BinaryOp.DIV, BinaryOp.MOD):
            # String concatenation: only ADD is allowed
            if left_type == STR and right_type == STR:
                if op == BinaryOp.ADD:
                    return STR
                else:
                    raise SemanticError(
                        code="E0102",
                        message=f"operator '{op.name}' not supported for strings",
                        span=expr.span,
                    )
            
            # Mixed string and other type
            if left_type == STR or right_type == STR:
                raise SemanticError(
                    code="E0102",
                    message=f"cannot perform arithmetic between {left_type} and {right_type}",
                    span=expr.span,
                )
            
            # Mixed int and float (D-CF-5: PROHIBITED)
            if left_type != right_type:
                raise SemanticError(
                    code="E0102",
                    message=f"cannot mix {left_type} and {right_type} in arithmetic",
                    span=expr.span,
                )
            
            # Bool arithmetic not allowed
            if left_type == BOOL:
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
    
    def _get_unary_expr_type(self, expr: UnaryExpr) -> QuasarType:
        """
        Get the type of a unary expression.
        
        Checks:
        - E0104: NOT requires bool operand
        - NEG requires numeric operand
        """
        operand_type = self._get_expression_type(expr.operand)
        
        if expr.operator == UnaryOp.NOT:
            if operand_type != BOOL:
                raise SemanticError(
                    code="E0104",
                    message=f"logical NOT requires bool operand, got {operand_type}",
                    span=expr.operand.span,
                )
            return BOOL
        
        if expr.operator == UnaryOp.NEG:
            if operand_type not in (INT, FLOAT):
                raise SemanticError(
                    code="E0102",
                    message=f"negation requires numeric type, got {operand_type}",
                    span=expr.operand.span,
                )
            return operand_type
        
        raise SemanticError(
            code="E0000",
            message=f"unknown unary operator: {expr.operator}",
            span=expr.span,
        )
    
    def _get_call_expr_type(self, expr: CallExpr) -> QuasarType:
        """
        Get the type of a function call expression.
        
        Checks:
        - E0001: Function must be declared
        - E0506: push() argument errors
        - E0507: len() argument errors
        
        Built-in functions (len, push) are intercepted here.
        """
        # Intercept built-in functions (Phase 6.2, Phase 7.0, Phase 7.1)
        if expr.callee == "len":
            return self._check_builtin_len(expr)
        if expr.callee == "push":
            return self._check_builtin_push(expr)
        if expr.callee == "input":
            return self._check_builtin_input(expr)
        if expr.callee in {"int", "float", "str", "bool"}:
            return self._check_builtin_cast(expr)
        
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
    
    def _check_builtin_len(self, expr: CallExpr) -> QuasarType:
        """
        Validate built-in len(list) function (Phase 6.2).
        
        Rules:
        - Must have exactly 1 argument
        - Argument must be a list type
        
        Returns: INT
        Errors: E0507 if argument is not a list
        """
        # Check argument count
        if len(expr.arguments) != 1:
            raise SemanticError(
                code="E0507",
                message=f"len() takes exactly 1 argument ({len(expr.arguments)} given)",
                span=expr.span,
            )
        
        # Check argument is a list
        arg_type = self._get_expression_type(expr.arguments[0])
        if not isinstance(arg_type, ListType):
            raise SemanticError(
                code="E0507",
                message=f"len() argument must be a list, got '{arg_type}'",
                span=expr.arguments[0].span,
            )
        
        return INT
    
    def _check_builtin_push(self, expr: CallExpr) -> QuasarType:
        """
        Validate built-in push(list, value) function (Phase 6.2).
        
        Rules:
        - Must have exactly 2 arguments
        - First argument must be a list type
        - Second argument must match the list's element type
        
        Returns: VOID (should only be used as statement)
        Errors: E0506 for type mismatches
        """
        # Check argument count
        if len(expr.arguments) != 2:
            raise SemanticError(
                code="E0506",
                message=f"push() takes exactly 2 arguments ({len(expr.arguments)} given)",
                span=expr.span,
            )
        
        # Check first argument is a list
        list_type = self._get_expression_type(expr.arguments[0])
        if not isinstance(list_type, ListType):
            raise SemanticError(
                code="E0506",
                message=f"push() first argument must be a list, got '{list_type}'",
                span=expr.arguments[0].span,
            )
        
        # Check second argument matches element type
        value_type = self._get_expression_type(expr.arguments[1])
        if not self._types_compatible(list_type.element_type, value_type):
            raise SemanticError(
                code="E0506",
                message=f"push() cannot add '{value_type}' to list of '{list_type.element_type}'",
                span=expr.arguments[1].span,
            )
        
        return VOID
    
    def _check_builtin_input(self, expr: CallExpr) -> QuasarType:
        """
        Validate built-in input() function (Phase 7.0).
        
        Rules:
        - Must have 0 or 1 argument
        - If 1 argument, must be a string (prompt)
        
        Returns: STR
        Errors:
        - E0600: Too many arguments
        - E0601: Argument must be string
        """
        # Check argument count (max 1)
        if len(expr.arguments) > 1:
            raise SemanticError(
                code="E0600",
                message=f"input() takes at most 1 argument ({len(expr.arguments)} given)",
                span=expr.span,
            )
        
        # If there's an argument, it must be a string
        if len(expr.arguments) == 1:
            arg_type = self._get_expression_type(expr.arguments[0])
            if arg_type != STR:
                raise SemanticError(
                    code="E0601",
                    message=f"input() prompt must be str, got '{arg_type}'",
                    span=expr.arguments[0].span,
                )
        
        return STR
    
    def _check_builtin_cast(self, expr: CallExpr) -> QuasarType:
        """
        Validate type casting functions (Phase 7.1).
        
        Functions: int(), float(), str(), bool()
        
        Rules:
        - Must have exactly 1 argument
        - Argument can be any primitive type (permissive)
        
        Returns: The target type (INT, FLOAT, STR, BOOL)
        Errors:
        - E0602: Wrong argument count
        """
        # Check argument count (exactly 1)
        if len(expr.arguments) != 1:
            raise SemanticError(
                code="E0602",
                message=f"{expr.callee}() requires exactly 1 argument ({len(expr.arguments)} given)",
                span=expr.span,
            )
        
        # Validate the argument exists and is a valid expression
        self._get_expression_type(expr.arguments[0])
        
        # Return the target type based on the function name
        return {
            "int": INT,
            "float": FLOAT,
            "str": STR,
            "bool": BOOL,
        }[expr.callee]
