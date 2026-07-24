import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

import main


class TestBuscaArquivos(unittest.TestCase):
    def test_case_insensitive_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            pasta = Path(tmp)
            arquivo = pasta / "Relatorio.pdf"
            arquivo.write_text("teste", encoding="utf-8")

            resultado = main.encontrar_mais_proximo("relatorio", [str(arquivo)])

            self.assertEqual(Path(resultado).name, arquivo.name)

    def test_listar_locais_de_busca_includes_home(self):
        locais = main.listar_locais_de_busca()

        self.assertTrue(locais)
        self.assertIn(str(Path.home()), locais)


if __name__ == "__main__":
    unittest.main()
