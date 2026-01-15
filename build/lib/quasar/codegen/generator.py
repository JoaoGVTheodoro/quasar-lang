"""
Code generator for Quasar.

Transpiles Quasar AST to Python source code.
"""

from typing import List

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
    PrintStmt,
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
    BinaryOp,
    UnaryOp,
)


class CodeGenerator:
    """
    Generates Python source code from a Quasar AST.
    
    The input AST is assumed to have passed semantic analysis.
    Output is valid, deterministic Python 3.10+ code.
    
    Uses visitor pattern to traverse the AST and generate code.
    """
    
    # Indentation unit (4 spaces)
    INDENT = "    "
    
    def __init__(self) -> None:
        """Initialize the code generator."""
        self._indent_level = 0
        self._lines: List[str] = []
    
    def generate(self, program: Program) -> str:
        """
        Generate Python code from a Quasar AST.
        
        Args:
            program: A semantically valid Quasar Program AST.
            
        Returns:
            Python source code as a string.
        """
        self._indent_level = 0
        self._lines = []
        
        for i, decl in enumerate(program.declarations):
            # Add blank line between top-level functions
            if i > 0 and isinstance(decl, FnDecl):
                prev = program.declarations[i - 1]
                if isinstance(prev, FnDecl):
                    self._lines.append("")
            
            self._generate_declaration(decl)
        
        return "\n".join(self._lines)
    
    # =========================================================================
    # Indentation Helpers
    # =========================================================================
    
    def _indent(self) -> str:
        """Return current indentation string."""
        return self.INDENT * self._indent_level
    
    def _emit(self, line: str) -> None:
        """Emit a line with current indentation."""
        self._lines.append(f"{self._indent()}{line}")
    
    def _emit_raw(self, line: str) -> None:
        """Emit a line without indentation."""
        self._lines.append(line)
    
    # =========================================================================
    # Declaration Generation
    # =========================================================================
    
    def _generate_declaration(self, decl) -> None:
        """Dispatch declaration generation based on type."""
        if isinstance(decl, VarDecl):
            self._generate_var_decl(decl)
        elif isinstance(decl, ConstDecl):
            self._generate_const_decl(decl)
        elif isinstance(decl, FnDecl):
            self._generate_fn_decl(decl)
        elif isinstance(decl, ExpressionStmt):
            self._generate_expression_stmt(decl)
        elif isinstance(decl, IfStmt):
            self._generate_if_stmt(decl)
        elif isinstance(decl, WhileStmt):
            self._generate_while_stmt(decl)
        elif isinstance(decl, ReturnStmt):
            self._generate_return_stmt(decl)
        elif isinstance(decl, BreakStmt):
            self._generate_break_stmt(decl)
        elif isinstance(decl, ContinueStmt):
            self._generate_continue_stmt(decl)
        elif isinstance(decl, PrintStmt):
            self._generate_print_stmt(decl)
        elif isinstance(decl, AssignStmt):
            self._generate_assign_stmt(decl)
        elif isinstance(decl, Block):
            self._generate_block(decl)
    
    def _generate_var_decl(self, decl: VarDecl) -> None:
        """Generate: name = expr"""
        expr = self._generate_expression(decl.initializer)
        self._emit(f"{decl.name} = {expr}")
    
    def _generate_const_decl(self, decl: ConstDecl) -> None:
        """Generate: NAME = expr (same as var in Python)"""
        expr = self._generate_expression(decl.initializer)
        self._emit(f"{decl.name} = {expr}")
    
    def _generate_fn_decl(self, decl: FnDecl) -> None:
        """Generate: def name(params):\\n    body"""
        params = ", ".join(p.name for p in decl.params)
        self._emit(f"def {decl.name}({params}):")
        
        self._indent_level += 1
        for stmt in decl.body.declarations:
            self._generate_declaration(stmt)
        self._indent_level -= 1
    
    # =========================================================================
    # Statement Generation
    # =========================================================================
    
    def _generate_block(self, block: Block) -> None:
        """Generate block contents (used for nested blocks)."""
        for decl in block.declarations:
            self._generate_declaration(decl)
    
    def _generate_expression_stmt(self, stmt: ExpressionStmt) -> None:
        """Generate expression as statement."""
        expr = self._generate_expression(stmt.expression)
        self._emit(expr)
    
    def _generate_if_stmt(self, stmt: IfStmt) -> None:
        """Generate: if cond:\\n    then\\nelse:\\n    else"""
        cond = self._generate_expression(stmt.condition)
        self._emit(f"if {cond}:")
        
        self._indent_level += 1
        for decl in stmt.then_block.declarations:
            self._generate_declaration(decl)
        self._indent_level -= 1
        
        if stmt.else_block is not None:
            self._emit("else:")
            self._indent_level += 1
            for decl in stmt.else_block.declarations:
                self._generate_declaration(decl)
            self._indent_level -= 1
    
    def _generate_while_stmt(self, stmt: WhileStmt) -> None:
        """Generate: while cond:\\n    body"""
        cond = self._generate_expression(stmt.condition)
        self._emit(f"while {cond}:")
        
        self._indent_level += 1
        for decl in stmt.body.declarations:
            self._generate_declaration(decl)
        self._indent_level -= 1
    
    def _generate_return_stmt(self, stmt: ReturnStmt) -> None:
        """Generate: return expr"""
        expr = self._generate_expression(stmt.value)
        self._emit(f"return {expr}")
    
    def _generate_break_stmt(self, stmt: BreakStmt) -> None:
        """Generate: break"""
        self._emit("break")
    
    def _generate_continue_stmt(self, stmt: ContinueStmt) -> None:
        """Generate: continue"""
        self._emit("continue")
    
    def _generate_print_stmt(self, stmt: PrintStmt) -> None:
        """
        Generate: print(args, sep=..., end=...) (Phase 5 + 5.1 + 5.2)
        
        Phase 5.2: Format mode detection
        If args[0] is StringLiteral AND contains {} (not escaped) AND len(args) > 1:
            Generate: print("template".format(arg1, arg2, ...), end=end_val)
        Else:
            Generate: print(arg0, arg1, ..., sep=sep_val, end=end_val)
        """
        # Check for format mode (Phase 5.2)
        use_format_mode = False
        if len(stmt.arguments) > 1 and isinstance(stmt.arguments[0], StringLiteral):
            format_str = stmt.arguments[0].value
            # Count real {} placeholders (not escaped {{ or }})
            temp = format_str.replace("{{", "").replace("}}", "")
            if temp.count("{}") > 0:
                use_format_mode = True
        
        if use_format_mode:
            # Format mode: print("template".format(args...), end=...)
            template = self._generate_expression(stmt.arguments[0])
            format_args = [self._generate_expression(arg) for arg in stmt.arguments[1:]]
            format_call = f"{template}.format({', '.join(format_args)})"
            
            # Build print call (sep is ignored in format mode)
            if stmt.end is not None:
                end_val = self._generate_expression(stmt.end)
                self._emit(f"print({format_call}, end={end_val})")
            else:
                self._emit(f"print({format_call})")
        else:
            # Normal mode: print(args, sep=..., end=...)
            args = [self._generate_expression(arg) for arg in stmt.arguments]
            parts = ", ".join(args)
            
            # Add sep if present
            if stmt.sep is not None:
                sep_val = self._generate_expression(stmt.sep)
                parts += f", sep={sep_val}"
            
            # Add end if present
            if stmt.end is not None:
                end_val = self._generate_expression(stmt.end)
                parts += f", end={end_val}"
            
            self._emit(f"print({parts})")
    
    def _generate_assign_stmt(self, stmt: AssignStmt) -> None:
        """Generate: target = expr"""
        expr = self._generate_expression(stmt.value)
        self._emit(f"{stmt.target} = {expr}")
    
    # =========================================================================
    # Expression Generation
    # =========================================================================
    
    def _generate_expression(self, expr) -> str:
        """Generate expression and return as string."""
        if isinstance(expr, IntLiteral):
            return str(expr.value)
        elif isinstance(expr, FloatLiteral):
            return str(expr.value)
        elif isinstance(expr, StringLiteral):
            return f'"{expr.value}"'
        elif isinstance(expr, BoolLiteral):
            return "True" if expr.value else "False"
        elif isinstance(expr, Identifier):
            return expr.name
        elif isinstance(expr, BinaryExpr):
            return self._generate_binary_expr(expr)
        elif isinstance(expr, UnaryExpr):
            return self._generate_unary_expr(expr)
        elif isinstance(expr, CallExpr):
            return self._generate_call_expr(expr)
        else:
            return ""
    
    def _generate_binary_expr(self, expr: BinaryExpr) -> str:
        """Generate binary expression."""
        left = self._generate_expression(expr.left)
        right = self._generate_expression(expr.right)
        op = self._binary_op_to_python(expr.operator)
        return f"{left} {op} {right}"
    
    def _generate_unary_expr(self, expr: UnaryExpr) -> str:
        """Generate unary expression."""
        operand = self._generate_expression(expr.operand)
        
        if expr.operator == UnaryOp.NEG:
            return f"-{operand}"
        elif expr.operator == UnaryOp.NOT:
            return f"not {operand}"
        else:
            return operand
    
    def _generate_call_expr(self, expr: CallExpr) -> str:
        """Generate function call."""
        args = ", ".join(self._generate_expression(arg) for arg in expr.arguments)
        return f"{expr.callee}({args})"
    
    def _binary_op_to_python(self, op: BinaryOp) -> str:
        """Convert Quasar binary operator to Python operator."""
        mapping = {
            # Arithmetic
            BinaryOp.ADD: "+",
            BinaryOp.SUB: "-",
            BinaryOp.MUL: "*",
            BinaryOp.DIV: "/",
            BinaryOp.MOD: "%",
            # Comparison
            BinaryOp.EQ: "==",
            BinaryOp.NE: "!=",
            BinaryOp.LT: "<",
            BinaryOp.GT: ">",
            BinaryOp.LE: "<=",
            BinaryOp.GE: ">=",
            # Logical (Quasar && || → Python and or)
            BinaryOp.AND: "and",
            BinaryOp.OR: "or",
        }
        return mapping.get(op, str(op))
