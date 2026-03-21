# conftest.py — adiciona src/ ao path do pytest para importações sem Django project
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))
