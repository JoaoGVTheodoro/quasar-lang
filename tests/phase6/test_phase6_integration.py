"""
Phase 6.4 Integration Tests — Final Validation

End-to-End tests combining all Phase 6 features:
- Lists ([T], ListLiteral, IndexExpr)
- Built-in functions (len, push)
- For loops and ranges
- Print formatting
- Control flow (if/else, break, continue)

These tests simulate real programs to ensure all features work together.
"""

import pytest
from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.semantic import SemanticAnalyzer
from quasar.codegen import CodeGenerator


# =============================================================================
# Helper Functions
# =============================================================================


def compile_to_python(source: str) -> str:
    """Compile Quasar source to Python code."""
    tokens = Lexer(source, "<test>").tokenize()
    ast = Parser(tokens).parse()
    analyzed = SemanticAnalyzer().analyze(ast)
    return CodeGenerator().generate(analyzed)


def run_quasar(source: str) -> str:
    """Compile and execute Quasar code, return stdout."""
    import io
    import sys
    
    python_code = compile_to_python(source)
    
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    try:
        exec(python_code, {})
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout
    
    return output


# =============================================================================
# Scenario 1: Accumulation Algorithm (Sum)
# =============================================================================


class TestScenario1Accumulation:
    """Test accumulation patterns with lists and loops."""
    
    def test_sum_list_basic(self) -> None:
        """Sum elements of a list."""
        output = run_quasar("""
        let nums: [int] = [10, 20, 30]
        let total: int = 0
        for n in nums {
            total = total + n
        }
        print(total)
        """)
        assert output.strip() == "60"
    
    def test_sum_with_format_print(self) -> None:
        """Sum with formatted output."""
        output = run_quasar("""
        let nums: [int] = [10, 20, 30]
        let total: int = 0
        for n in nums {
            total = total + n
        }
        print("Total: {}", total)
        """)
        assert output.strip() == "Total: 60"
    
    def test_sum_using_index(self) -> None:
        """Sum using index-based iteration."""
        output = run_quasar("""
        let nums: [int] = [5, 10, 15, 20]
        let total: int = 0
        for i in 0..len(nums) {
            total = total + nums[i]
        }
        print("Sum = {}", total)
        """)
        assert output.strip() == "Sum = 50"
    
    def test_average_calculation(self) -> None:
        """Calculate average of list elements."""
        output = run_quasar("""
        let values: [int] = [10, 20, 30, 40]
        let sum: int = 0
        for v in values {
            sum = sum + v
        }
        let avg: int = sum / len(values)
        print("Average: {}", avg)
        """)
        # Note: Python division returns float, so 100/4 = 25.0
        assert output.strip() == "Average: 25.0"
    
    def test_product_accumulation(self) -> None:
        """Multiply all elements together."""
        output = run_quasar("""
        let nums: [int] = [2, 3, 4]
        let product: int = 1
        for n in nums {
            product = product * n
        }
        print(product)
        """)
        assert output.strip() == "24"


# =============================================================================
# Scenario 2: Filtering with Logic and Push
# =============================================================================


class TestScenario2Filtering:
    """Test filtering patterns using conditionals and push."""
    
    def test_filter_greater_than(self) -> None:
        """Filter numbers greater than threshold."""
        output = run_quasar("""
        let numbers: [int] = [1, 5, 10, 15, 2]
        let large: [int] = []
        for n in numbers {
            if n > 5 {
                push(large, n)
            }
        }
        print(len(large))
        print(large[0])
        print(large[1])
        """)
        assert output.strip() == "2\n10\n15"
    
    def test_filter_even_numbers(self) -> None:
        """Filter even numbers from list."""
        output = run_quasar("""
        let nums: [int] = [1, 2, 3, 4, 5, 6]
        let evens: [int] = []
        for n in nums {
            if n % 2 == 0 {
                push(evens, n)
            }
        }
        for e in evens {
            print(e)
        }
        """)
        assert output.strip() == "2\n4\n6"
    
    def test_filter_odd_numbers(self) -> None:
        """Filter odd numbers from list."""
        output = run_quasar("""
        let nums: [int] = [1, 2, 3, 4, 5]
        let odds: [int] = []
        for n in nums {
            if n % 2 != 0 {
                push(odds, n)
            }
        }
        print(len(odds))
        """)
        assert output.strip() == "3"
    
    def test_filter_with_multiple_conditions(self) -> None:
        """Filter with compound conditions."""
        output = run_quasar("""
        let nums: [int] = [1, 5, 10, 15, 20, 25]
        let result: [int] = []
        for n in nums {
            if n > 5 && n < 25 {
                push(result, n)
            }
        }
        print(len(result))
        print(result[0])
        print(result[1])
        print(result[2])
        """)
        assert output.strip() == "3\n10\n15\n20"
    
    def test_partition_numbers(self) -> None:
        """Partition numbers into two lists."""
        output = run_quasar("""
        let nums: [int] = [3, 8, 1, 9, 4]
        let small: [int] = []
        let big: [int] = []
        for n in nums {
            if n < 5 {
                push(small, n)
            } else {
                push(big, n)
            }
        }
        print("Small:", len(small))
        print("Big:", len(big))
        """)
        assert output.strip() == "Small: 3\nBig: 2"


# =============================================================================
# Scenario 3: Matrix and Nested Loops
# =============================================================================


class TestScenario3Matrix:
    """Test matrix operations with nested loops."""
    
    def test_matrix_print_cells(self) -> None:
        """Print each cell of a 2x2 matrix."""
        output = run_quasar("""
        let matrix: [[int]] = [[1, 2], [3, 4]]
        for row in matrix {
            for cell in row {
                print(cell)
            }
        }
        """)
        assert output.strip() == "1\n2\n3\n4"
    
    def test_matrix_sum_all(self) -> None:
        """Sum all elements in a matrix."""
        output = run_quasar("""
        let matrix: [[int]] = [[1, 2, 3], [4, 5, 6]]
        let total: int = 0
        for row in matrix {
            for cell in row {
                total = total + cell
            }
        }
        print(total)
        """)
        assert output.strip() == "21"
    
    def test_matrix_index_access(self) -> None:
        """Access matrix elements by index."""
        output = run_quasar("""
        let m: [[int]] = [[10, 20], [30, 40]]
        print(m[0][0])
        print(m[0][1])
        print(m[1][0])
        print(m[1][1])
        """)
        assert output.strip() == "10\n20\n30\n40"
    
    def test_matrix_row_sums(self) -> None:
        """Calculate sum of each row."""
        output = run_quasar("""
        let matrix: [[int]] = [[1, 2, 3], [4, 5, 6]]
        for i in 0..len(matrix) {
            let row_sum: int = 0
            for j in 0..len(matrix[i]) {
                row_sum = row_sum + matrix[i][j]
            }
            print("Row {}: {}", i, row_sum)
        }
        """)
        assert output.strip() == "Row 0: 6\nRow 1: 15"
    
    def test_matrix_3x3(self) -> None:
        """Work with a 3x3 matrix."""
        output = run_quasar("""
        let grid: [[int]] = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        let diagonal: int = grid[0][0] + grid[1][1] + grid[2][2]
        print("Diagonal sum: {}", diagonal)
        """)
        assert output.strip() == "Diagonal sum: 15"


# =============================================================================
# Scenario 4: Fibonacci Generator
# =============================================================================


class TestScenario4Fibonacci:
    """Test Fibonacci sequence generation."""
    
    def test_fibonacci_10_terms(self) -> None:
        """Generate first 10 Fibonacci numbers."""
        output = run_quasar("""
        let fib: [int] = [0, 1]
        for i in 2..10 {
            let next: int = fib[i - 1] + fib[i - 2]
            push(fib, next)
        }
        print(len(fib))
        print(fib[9])
        """)
        # fib = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
        assert output.strip() == "10\n34"
    
    def test_fibonacci_print_sequence(self) -> None:
        """Print Fibonacci sequence."""
        output = run_quasar("""
        let fib: [int] = [0, 1]
        for i in 2..8 {
            let next: int = fib[i - 1] + fib[i - 2]
            push(fib, next)
        }
        for n in fib {
            print(n)
        }
        """)
        # [0, 1, 1, 2, 3, 5, 8, 13]
        assert output.strip() == "0\n1\n1\n2\n3\n5\n8\n13"
    
    def test_fibonacci_sum(self) -> None:
        """Sum of first N Fibonacci numbers."""
        output = run_quasar("""
        let fib: [int] = [0, 1]
        for i in 2..10 {
            push(fib, fib[i - 1] + fib[i - 2])
        }
        let sum: int = 0
        for n in fib {
            sum = sum + n
        }
        print(sum)
        """)
        # 0+1+1+2+3+5+8+13+21+34 = 88
        assert output.strip() == "88"
    
    def test_fibonacci_find_first_over_100(self) -> None:
        """Find first Fibonacci number over 100."""
        output = run_quasar("""
        let fib: [int] = [0, 1]
        for i in 2..20 {
            push(fib, fib[i - 1] + fib[i - 2])
            if fib[i] > 100 {
                print("Found: {}", fib[i])
                break
            }
        }
        """)
        # First fib > 100 is 144 (at index 12)
        assert output.strip() == "Found: 144"


# =============================================================================
# Additional Integration Scenarios
# =============================================================================


class TestAdditionalIntegration:
    """Additional integration tests for edge cases and combinations."""
    
    def test_nested_list_building(self) -> None:
        """Build a list of lists dynamically."""
        output = run_quasar("""
        let rows: [[int]] = []
        push(rows, [1, 2])
        push(rows, [3, 4])
        push(rows, [5, 6])
        print(len(rows))
        print(rows[2][1])
        """)
        assert output.strip() == "3\n6"
    
    def test_count_occurrences(self) -> None:
        """Count occurrences of a value."""
        output = run_quasar("""
        let nums: [int] = [1, 2, 2, 3, 2, 4, 2]
        let count: int = 0
        for n in nums {
            if n == 2 {
                count = count + 1
            }
        }
        print("Count of 2: {}", count)
        """)
        assert output.strip() == "Count of 2: 4"
    
    def test_find_max(self) -> None:
        """Find maximum element in list."""
        output = run_quasar("""
        let nums: [int] = [3, 7, 2, 9, 1, 5]
        let max: int = nums[0]
        for n in nums {
            if n > max {
                max = n
            }
        }
        print("Max: {}", max)
        """)
        assert output.strip() == "Max: 9"
    
    def test_find_min(self) -> None:
        """Find minimum element in list."""
        output = run_quasar("""
        let nums: [int] = [5, 2, 8, 1, 9]
        let min: int = nums[0]
        for n in nums {
            if n < min {
                min = n
            }
        }
        print("Min: {}", min)
        """)
        assert output.strip() == "Min: 1"
    
    def test_reverse_list(self) -> None:
        """Create reversed copy of list."""
        output = run_quasar("""
        let original: [int] = [1, 2, 3, 4, 5]
        let reversed: [int] = []
        for i in 0..len(original) {
            let idx: int = len(original) - 1 - i
            push(reversed, original[idx])
        }
        for n in reversed {
            print(n)
        }
        """)
        assert output.strip() == "5\n4\n3\n2\n1"
    
    def test_copy_list(self) -> None:
        """Create a copy of a list."""
        output = run_quasar("""
        let src: [int] = [10, 20, 30]
        let dst: [int] = []
        for n in src {
            push(dst, n)
        }
        print(len(dst))
        print(dst[0])
        print(dst[1])
        print(dst[2])
        """)
        assert output.strip() == "3\n10\n20\n30"
    
    def test_string_list_operations(self) -> None:
        """Work with string lists."""
        output = run_quasar("""
        let names: [str] = ["Alice", "Bob", "Charlie"]
        for name in names {
            print("Hello, {}!", name)
        }
        """)
        assert output.strip() == "Hello, Alice!\nHello, Bob!\nHello, Charlie!"
    
    def test_mixed_control_flow(self) -> None:
        """Complex control flow with loops and conditions."""
        output = run_quasar("""
        let nums: [int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        let sum_even: int = 0
        let sum_odd: int = 0
        for n in nums {
            if n % 2 == 0 {
                sum_even = sum_even + n
            } else {
                sum_odd = sum_odd + n
            }
        }
        print("Even sum: {}", sum_even)
        print("Odd sum: {}", sum_odd)
        """)
        assert output.strip() == "Even sum: 30\nOdd sum: 25"
    
    def test_early_exit_with_break(self) -> None:
        """Early loop exit with break."""
        output = run_quasar("""
        let nums: [int] = [1, 2, 3, 4, 5]
        let sum: int = 0
        for n in nums {
            if n == 4 {
                break
            }
            sum = sum + n
        }
        print(sum)
        """)
        # 1 + 2 + 3 = 6
        assert output.strip() == "6"
    
    def test_skip_with_continue(self) -> None:
        """Skip iterations with continue."""
        output = run_quasar("""
        let sum: int = 0
        for i in 1..10 {
            if i % 3 == 0 {
                continue
            }
            sum = sum + i
        }
        print(sum)
        """)
        # Skip 3, 6, 9: 1+2+4+5+7+8 = 27
        assert output.strip() == "27"
    
    def test_prime_check_simple(self) -> None:
        """Simple prime number check."""
        output = run_quasar("""
        let n: int = 17
        let is_prime: bool = true
        for i in 2..n {
            if n % i == 0 {
                is_prime = false
                break
            }
        }
        if is_prime {
            print("{} is prime", n)
        } else {
            print("{} is not prime", n)
        }
        """)
        assert output.strip() == "17 is prime"
    
    def test_factorial_iterative(self) -> None:
        """Calculate factorial iteratively."""
        output = run_quasar("""
        let n: int = 5
        let result: int = 1
        for i in 1..n + 1 {
            result = result * i
        }
        print("{}! = {}", n, result)
        """)
        # 5! = 120
        assert output.strip() == "5! = 120"
    
    def test_triangular_numbers(self) -> None:
        """Generate triangular numbers."""
        output = run_quasar("""
        let triangular: [int] = []
        for n in 1..6 {
            let sum: int = 0
            for i in 1..n + 1 {
                sum = sum + i
            }
            push(triangular, sum)
        }
        for t in triangular {
            print(t)
        }
        """)
        # T(1)=1, T(2)=3, T(3)=6, T(4)=10, T(5)=15
        assert output.strip() == "1\n3\n6\n10\n15"
    
    def test_two_sum_simple(self) -> None:
        """Find two numbers that sum to target."""
        output = run_quasar("""
        let nums: [int] = [2, 7, 11, 15]
        let target: int = 9
        let found: bool = false
        for i in 0..len(nums) {
            for j in 0..len(nums) {
                if i != j && nums[i] + nums[j] == target {
                    print("Found: {} + {}", nums[i], nums[j])
                    found = true
                    break
                }
            }
            if found {
                break
            }
        }
        """)
        assert output.strip() == "Found: 2 + 7"
