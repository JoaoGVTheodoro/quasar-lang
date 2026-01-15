"""
Quasar entry point.

Allows running the compiler as a module:
    python -m quasar compile <file.qsr>
    python -m quasar run <file.qsr>
    python -m quasar check <file.qsr>
"""

import sys
from quasar.cli import main

if __name__ == "__main__":
    sys.exit(main())
