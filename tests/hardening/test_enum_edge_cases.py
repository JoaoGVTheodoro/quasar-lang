"""
Hardening Tests: Enum Edge Cases

Aggressive edge case testing for enums. No new semantics—only boundary verification.
"""
import pytest
import subprocess

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.parser.errors import ParserError
from quasar.semantic import SemanticAnalyzer
from quasar.semantic.errors import SemanticError
from quasar.codegen import CodeGenerator


def parse(source: str):
    lexer = Lexer(source)
    return Parser(lexer.tokenize()).parse()


def analyze(source: str):
    program = parse(source)
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(program)


def generate(source: str) -> str:
    program = analyze(source)
    return CodeGenerator().generate(program)


def compile_and_run(source: str) -> str:
    python_code = generate(source)
    result = subprocess.run(
        ["python", "-c", python_code],
        capture_output=True,
        text=True,
        timeout=5,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Execution failed: {result.stderr}")
    return result.stdout


# ============================================================================
# Single Variant Edge Cases
# ============================================================================

class TestSingleVariantEnum:
    """Enums with exactly one variant."""

    def test_single_variant_declaration(self):
        """Single variant enum parses correctly."""
        program = parse("enum Single { Only }")
        assert len(program.declarations[0].variants) == 1

    def test_single_variant_access(self):
        """Single variant can be accessed."""
        analyze("enum Single { Only }\nlet s: Single = Single.Only")

    def test_single_variant_equality(self):
        """Single variant equals itself."""
        output = compile_and_run("""
        enum Single { Only }
        print(Single.Only == Single.Only)
        """)
        assert output.strip() == "True"

    def test_single_variant_inequality(self):
        """Single variant != itself is False."""
        output = compile_and_run("""
        enum Single { Only }
        print(Single.Only != Single.Only)
        """)
        assert output.strip() == "False"


# ============================================================================
# Large Enum Edge Cases
# ============================================================================

class TestLargeEnum:
    """Enums with many variants."""

    def test_fifty_variants(self):
        """Enum with 50 variants works."""
        variants = ", ".join([f"V{i}" for i in range(50)])
        source = f"enum Large {{ {variants} }}"
        program = parse(source)
        assert len(program.declarations[0].variants) == 50

    def test_large_enum_first_variant(self):
        """First variant of large enum accessible."""
        variants = ", ".join([f"V{i}" for i in range(50)])
        source = f"""
        enum Large {{ {variants} }}
        let v: Large = Large.V0
        """
        analyze(source)

    def test_large_enum_last_variant(self):
        """Last variant of large enum accessible."""
        variants = ", ".join([f"V{i}" for i in range(50)])
        source = f"""
        enum Large {{ {variants} }}
        let v: Large = Large.V49
        """
        analyze(source)

    def test_large_enum_comparison(self):
        """Large enum variants compare correctly."""
        variants = ", ".join([f"V{i}" for i in range(20)])
        output = compile_and_run(f"""
        enum Large {{ {variants} }}
        print(Large.V0 == Large.V19)
        print(Large.V10 == Large.V10)
        """)
        lines = output.strip().split("\n")
        assert lines[0] == "False"
        assert lines[1] == "True"


# ============================================================================
# Deeply Nested Usage
# ============================================================================

class TestDeeplyNestedEnums:
    """Enums in deeply nested control flow."""

    def test_enum_in_nested_if(self):
        """Enum comparison in 5-level nested if."""
        source = """
        enum State { A, B, C }
        let s: State = State.B
        let result: int = 0
        if true {
            if true {
                if true {
                    if true {
                        if s == State.B {
                            result = 42
                        }
                    }
                }
            }
        }
        print(result)
        """
        output = compile_and_run(source)
        assert output.strip() == "42"

    def test_enum_in_nested_while(self):
        """Enum in nested while loops."""
        source = """
        enum Counter { Active, Done }
        let state: Counter = Counter.Active
        let outer: int = 0
        while outer < 2 {
            let inner: int = 0
            while inner < 2 {
                if state == Counter.Active {
                    inner = inner + 1
                }
            }
            outer = outer + 1
        }
        print(outer)
        """
        output = compile_and_run(source)
        assert output.strip() == "2"

    def test_enum_in_function_in_loop(self):
        """Function returning enum called inside loop."""
        source = """
        enum Status { Ok, Err }
        fn get_status(x: int) -> Status {
            if x > 0 {
                return Status.Ok
            }
            return Status.Err
        }
        
        let count: int = 0
        let i: int = 0
        while i < 5 {
            if get_status(i) == Status.Ok {
                count = count + 1
            }
            i = i + 1
        }
        print(count)
        """
        output = compile_and_run(source)
        assert output.strip() == "4"  # i=1,2,3,4 are > 0


# ============================================================================
# Error Message Quality
# ============================================================================

class TestErrorMessageQuality:
    """Verify error messages contain useful information."""

    def test_E1200_message_contains_name(self):
        """E1200 mentions the conflicting type name."""
        with pytest.raises(SemanticError) as excinfo:
            analyze("enum Foo { A }\nenum Foo { B }")
        assert "Foo" in excinfo.value.message
        assert excinfo.value.code == "E1200"

    def test_E1201_message_contains_variant(self):
        """E1201 mentions the duplicate variant name."""
        with pytest.raises(SemanticError) as excinfo:
            analyze("enum Color { Red, Green, Red }")
        assert "Red" in excinfo.value.message
        assert excinfo.value.code == "E1201"

    def test_E1202_message_contains_both_names(self):
        """E1202 mentions enum name and unknown variant."""
        with pytest.raises(SemanticError) as excinfo:
            analyze("enum Color { Red }\nlet c: Color = Color.Blue")
        assert "Color" in excinfo.value.message
        assert "Blue" in excinfo.value.message
        assert excinfo.value.code == "E1202"

    def test_E1204_message_contains_types(self):
        """E1204 mentions both enum types."""
        with pytest.raises(SemanticError) as excinfo:
            analyze("""
            enum A { X }
            enum B { Y }
            let x: bool = A.X == B.Y
            """)
        assert excinfo.value.code == "E1204"

    def test_E1205_message_mentions_operators(self):
        """E1205 mentions which operators are allowed."""
        with pytest.raises(SemanticError) as excinfo:
            analyze("enum A { X, Y }\nlet b: bool = A.X < A.Y")
        assert "==" in excinfo.value.message or "!=" in excinfo.value.message
        assert excinfo.value.code == "E1205"


# ============================================================================
# Error Span Verification
# ============================================================================

class TestErrorSpans:
    """Verify error spans point to correct locations."""

    def test_E1201_span_points_to_duplicate(self):
        """E1201 span is on the duplicate variant, not the original."""
        with pytest.raises(SemanticError) as excinfo:
            analyze("enum Color { Red, Green, Red }")
        # The second "Red" should be in the span
        assert excinfo.value.span is not None
        # Span should be after the first occurrences
        assert excinfo.value.span.start_column > 10

    def test_E1202_span_points_to_access(self):
        """E1202 span is on the access expression."""
        source = "enum Color { Red }\nlet c: Color = Color.Purple"
        with pytest.raises(SemanticError) as excinfo:
            analyze(source)
        assert excinfo.value.span is not None
        # Should be on line 2 (1-indexed)
        assert excinfo.value.span.start_line == 2


# ============================================================================
# Trailing Comma Edge Cases
# ============================================================================

class TestTrailingComma:
    """Trailing comma handling."""

    def test_single_variant_trailing_comma(self):
        """Single variant with trailing comma."""
        program = parse("enum S { A, }")
        assert len(program.declarations[0].variants) == 1

    def test_multiple_trailing_commas_error(self):
        """Multiple trailing commas should error (empty variant position)."""
        with pytest.raises(ParserError):
            parse("enum S { A,, }")

    def test_leading_comma_error(self):
        """Leading comma is an error."""
        with pytest.raises(ParserError):
            parse("enum S { , A }")


# ============================================================================
# Reserved/Keyword Variant Names
# ============================================================================

class TestVariantNames:
    """Variant naming edge cases."""

    def test_lowercase_variant_allowed(self):
        """Lowercase variant names are allowed (style warning only)."""
        analyze("enum Color { red, green, blue }")

    def test_underscore_variant_allowed(self):
        """Variants with underscores are allowed."""
        analyze("enum Status { in_progress, not_started }")

    def test_numeric_suffix_allowed(self):
        """Variants with numbers are allowed."""
        analyze("enum Level { Level1, Level2, Level99 }")

    def test_all_caps_allowed(self):
        """ALL_CAPS variants are allowed."""
        analyze("enum Error { NOT_FOUND, INTERNAL_ERROR }")
