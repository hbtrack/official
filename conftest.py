# conftest.py — configura path e Django para o pytest
import sys
import pathlib

# Adiciona src/ e raiz (config/) ao sys.path
_ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT))
