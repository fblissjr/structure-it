"""ELT pipeline modules.

Three-layer architecture:
- Raw (Bronze): data/raw/ - original source files
- Staged (Silver): data/staged/ - transformed, ready to load
- Final (Gold): DuckDB - queryable database

Scripts:
- transform.py: Raw -> Staged (markdown conversion + Gemini extraction)
- load.py: Staged -> DuckDB (insert/update/merge)
"""
