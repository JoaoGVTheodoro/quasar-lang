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
    StructDecl,
    StructField,
    ImportDecl,
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
    MemberAssignStmt,
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
    FieldInit,
    StructInitExpr,
    MemberAccessExpr,
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
        
        # Add imports if necessary
        if any(isinstance(d, StructDecl) for d in program.declarations):
            self._lines.append("from dataclasses import dataclass")
            self._lines.append("")
        
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
        elif isinstance(decl, StructDecl):
            self._generate_struct_decl(decl)
        elif isinstance(decl, ImportDecl):
            self._generate_import_decl(decl)
        elif isinstance(decl, ExpressionStmt):
            self._generate_expression_stmt(decl)
        elif isinstance(decl, IfStmt):
            self._generate_if_stmt(decl)
        elif isinstance(decl, WhileStmt):
            self._generate_while_stmt(decl)
        elif isinstance(decl, ForStmt):
            self._generate_for_stmt(decl)
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
        elif isinstance(decl, IndexAssignStmt):
            self._generate_index_assign_stmt(decl)
        elif isinstance(decl, MemberAssignStmt):
            self._generate_member_assign_stmt(decl)
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
    def _generate_for_stmt(self, stmt: ForStmt) -> None:
        """Generate: for var in iterable:\n    body (Phase 6.3)"""
        iterable = self._generate_expression(stmt.iterable)
        self._emit(f"for {stmt.variable} in {iterable}:")
        
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
    
    def _generate_index_assign_stmt(self, stmt: IndexAssignStmt) -> None:
        """Generate: target[index] = expr (Phase 6.1)"""
        target = self._generate_expression(stmt.target)
        value = self._generate_expression(stmt.value)
        self._emit(f"{target} = {value}")
    
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
        elif isinstance(expr, ListLiteral):
            return self._generate_list_literal(expr)
        elif isinstance(expr, IndexExpr):
            return self._generate_index_expr(expr)
        elif isinstance(expr, RangeExpr):
            return self._generate_range_expr(expr)
        elif isinstance(expr, StructInitExpr):
            return self._generate_struct_init_expr(expr)
        elif isinstance(expr, MemberAccessExpr):
            return self._generate_member_access_expr(expr)
        else:
            return ""
    
    def _generate_binary_expr(self, expr: BinaryExpr) -> str:
        """Generate binary expression with defensive parentheses.
        
        Always wraps result in parentheses to preserve operator precedence.
        Python handles redundant parentheses gracefully.
        """
        left = self._generate_expression(expr.left)
        right = self._generate_expression(expr.right)
        op = self._binary_op_to_python(expr.operator)
        return f"({left} {op} {right})"
    
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
        """Generate function call.
        
        Intercepts built-in functions (Phase 6.2, Phase 7.0, Phase 7.1):
        - len(x) → len(x) (Python native)
        - push(x, v) → x.append(v)
        - input() / input(prompt) → input() / input(prompt)
        - int/float/str/bool(x) → int/float/str/bool(x)
        """
        # Built-in: Type casting functions (Phase 7.1)
        if expr.callee in {"int", "float", "str", "bool"}:
            arg = self._generate_expression(expr.arguments[0])
            return f"{expr.callee}({arg})"
        
        # Built-in: input() → input() (Phase 7.0)
        if expr.callee == "input":
            if len(expr.arguments) == 0:
                return "input()"
            else:
                prompt = self._generate_expression(expr.arguments[0])
                return f"input({prompt})"
        
        # Built-in: len(x) → len(x)
        if expr.callee == "len":
            arg = self._generate_expression(expr.arguments[0])
            return f"len({arg})"
        
        # Built-in: push(x, v) → x.append(v)
        if expr.callee == "push":
            list_arg = self._generate_expression(expr.arguments[0])
            value_arg = self._generate_expression(expr.arguments[1])
            return f"{list_arg}.append({value_arg})"
        
        # Regular function call
        args = ", ".join(self._generate_expression(arg) for arg in expr.arguments)
        return f"{expr.callee}({args})"
    
    def _generate_list_literal(self, expr: ListLiteral) -> str:
        """Generate list literal: [a, b, c]"""
        elements = ", ".join(self._generate_expression(el) for el in expr.elements)
        return f"[{elements}]"
    
    def _generate_index_expr(self, expr: IndexExpr) -> str:
        """Generate index access: target[index] (Phase 6.1)"""
        target = self._generate_expression(expr.target)
        index = self._generate_expression(expr.index)
        return f"{target}[{index}]"
    
    def _generate_range_expr(self, expr: RangeExpr) -> str:
        """Generate range: start..end → range(start, end) (Phase 6.3)"""
        start = self._generate_expression(expr.start)
        end = self._generate_expression(expr.end)
        return f"range({start}, {end})"
    
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

    def _generate_struct_decl(self, decl: StructDecl) -> None:
        """
        Generate:
        @dataclass
        class Name:
            field: type
        """
        self._emit("@dataclass")
        self._emit(f"class {decl.name}:")
        
        self._indent_level += 1
        
        if not decl.fields:
            self._emit("pass")
        else:
            for field in decl.fields:
                type_str = self._type_to_python(field.type_annotation)
                self._emit(f"{field.name}: {type_str}")
        
        self._indent_level -= 1

    def _type_to_python(self, type_ann) -> str:
        """Convert Quasar type annotation to Python type string."""
        from quasar.ast.types import ListType, PrimitiveType
        
        if isinstance(type_ann, PrimitiveType):
            return type_ann.name
            
        if isinstance(type_ann, ListType):
            elem = self._type_to_python(type_ann.element_type)
            return f"list[{elem}]"
            
        return "any"

    def _generate_struct_init_expr(self, expr: StructInitExpr) -> str:
        """
        Generate struct instantiation.
        
        Quasar: Point { x: 1, y: 2 }
        Python: Point(x=1, y=2)
        """
        args = ", ".join(
            f"{f.name}={self._generate_expression(f.value)}"
            for f in expr.fields
        )
        return f"{expr.struct_name}({args})"

    def _generate_member_access_expr(self, expr: MemberAccessExpr) -> str:
        """Generate member access: obj.field"""
        obj = self._generate_expression(expr.object)
        return f"{obj}.{expr.member}"

    def _generate_member_assign_stmt(self, stmt: MemberAssignStmt) -> None:
        """Generate member assignment: obj.field = value"""
        obj = self._generate_expression(stmt.object)
        value = self._generate_expression(stmt.value)
        self._emit(f"{obj}.{stmt.member} = {value}")

    def _generate_import_decl(self, decl: ImportDecl) -> None:
        """Generate import statement (Phase 9)."""
        if decl.is_local:
            # Local .qsr file: strip .qsr extension and convert to Python import
            module_path = decl.module
            if module_path.endswith(".qsr"):
                module_path = module_path[:-4]
            # Remove leading ./
            if module_path.startswith("./"):
                module_path = module_path[2:]
            # Replace / with . for Python import
            module_path = module_path.replace("/", ".")
            self._emit(f"import {module_path}")
        else:
            # Python stdlib import
            self._emit(f"import {decl.module}")
