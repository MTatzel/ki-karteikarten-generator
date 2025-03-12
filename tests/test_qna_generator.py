import sys
import os

# `src`-Ordner zum Suchpfad hinzufügen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import unittest
from unittest.mock import patch
from nlp.qna_generator import QnAGenerator  # Importiere den QnAGenerator


class TestQnAGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = QnAGenerator(api_type="manual")

    def test_generate_qna_openai(self):
        response = """Frage 1: Was ist Informatik?
                      Antwort: Die Wissenschaft der Information.

                      Frage 2: Was ist ein Algorithmus?
                      Antwort: Eine Abfolge von Anweisungen."""

        result = self.generator.extract_qna_pairs(response)
        
        self.assertEqual(len(result), 2)  # Es sollten 2 QnA-Paare sein
        self.assertEqual(result[0]["question"].strip(), "Was ist Informatik?")
        self.assertEqual(result[0]["answer"].strip(), "Die Wissenschaft der Information.")
        self.assertEqual(result[1]["question"].strip(), "Was ist ein Algorithmus?")
        self.assertEqual(result[1]["answer"].strip(), "Eine Abfolge von Anweisungen.")

    def test_generate_qna_manual(self):
        response = """Frage: Was ist eine Schleife?
                      Antwort: Eine wiederholte Anweisung."""

        result = self.generator.extract_qna_pairs(response)
        
        self.assertEqual(len(result), 1)  # Es sollte 1 QnA-Paar sein
        self.assertEqual(result[0]["question"].strip(), "Was ist eine Schleife?")
        self.assertEqual(result[0]["answer"].strip(), "Eine wiederholte Anweisung.")

if __name__ == '__main__':
    unittest.main()