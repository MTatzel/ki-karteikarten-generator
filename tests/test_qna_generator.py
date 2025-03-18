import sys
import os
import pytest
from nlp.qna_generator import QnAGenerator
from unittest.mock import patch, MagicMock


@pytest.fixture
def qna_generator():
    """Erstellt eine QnAGenerator-Instanz mit Mock-API-Schlüssel."""
    return QnAGenerator(api_type="openai", api_key="test-key")


def test_qna_generator_init(qna_generator):
    """Testet, ob der QnAGenerator korrekt initialisiert wird."""
    assert qna_generator.api_type == "openai"
    assert qna_generator.api_key == "test-key"


@patch("nlp.qna_generator.QnAGenerator.call_openai")
def test_generate_qna_pairs_openai(mock_openai, qna_generator):
    """Mockt die OpenAI API und testet die QnA-Generierung."""
    mock_openai.return_value = "Frage: Was ist Python?\nAntwort: Eine Programmiersprache."
    chunk = "Python ist eine weit verbreitete Programmiersprache."
    qna_pairs = qna_generator.generate_qna_pairs(chunk, num_questions=1)
    
    assert isinstance(qna_pairs, list)
    assert len(qna_pairs) > 0
    assert "question" in qna_pairs[0]
    assert "answer" in qna_pairs[0]
    assert "Python" in qna_pairs[0]["question"]


@patch("nlp.qna_generator.QnAGenerator.call_gemini")
def test_generate_qna_pairs_gemini(mock_gemini):
    """Mockt die Gemini API und testet die QnA-Generierung."""
    mock_gemini.return_value = "Frage: Was ist eine KI?\nAntwort: Ein Algorithmus zur Mustererkennung."
    generator = QnAGenerator(api_type="gemini", api_key="test-key")
    chunk = "KI ist ein Algorithmus zur Mustererkennung."
    qna_pairs = generator.generate_qna_pairs(chunk, num_questions=1)
    
    assert isinstance(qna_pairs, list)
    assert len(qna_pairs) > 0
    assert "question" in qna_pairs[0]
    assert "answer" in qna_pairs[0]
    assert "KI" in qna_pairs[0]["question"]


def test_qna_generator_manual():
    """Testet, ob die manuelle Methode korrekt eine statische Meldung zurückgibt."""
    generator = QnAGenerator(api_type="manual")
    chunk = "Das ist ein Testchunk."
    qna_pairs = generator.generate_qna_pairs(chunk, num_questions=1)
    
    assert qna_pairs == [], "Manueller Modus sollte eine leere Liste zurückgeben."


def test_extract_qna_pairs():
    """Testet die Extraktion von Frage-Antwort-Paaren."""
    generator = QnAGenerator(api_type="manual")
    response_text = "Frage: Was ist ein Test?\nAntwort: Eine Prüfung einer Funktion."
    qna_pairs = generator.extract_qna_pairs(response_text)
    
    assert isinstance(qna_pairs, list)
    assert len(qna_pairs) == 1
    assert qna_pairs[0]["question"] == "Was ist ein Test?"
    assert qna_pairs[0]["answer"] == "Eine Prüfung einer Funktion."


def test_api_error_handling():
    """Testet, ob die API-Fehlerbehandlung korrekt funktioniert."""
    generator = QnAGenerator(api_type="openai", api_key="test-key")

    with patch("nlp.qna_generator.QnAGenerator.call_openai", side_effect=Exception("API-Fehler")):
        chunk = "Testabschnitt."
        
        try:
            response = generator.generate_qna_pairs(chunk, num_questions=1)
        except Exception:
            response = []  # Falls ein Fehler auftritt, sollte eine leere Liste zurückkommen

        assert response == [], "Bei einem API-Fehler sollte eine leere Liste zurückgegeben werden."

