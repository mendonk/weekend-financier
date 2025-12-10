#!/usr/bin/env python3
"""
Entry point for Weekend Financier CLI
"""
import sys
from pathlib import Path

# Add src/ to Python path for src-layout
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from cli import main

if __name__ == "__main__":
    main()

