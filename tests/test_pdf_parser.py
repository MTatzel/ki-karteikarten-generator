from pdf_parser.pdf_parser import PDFParser
from fpdf import FPDF
import pytest
import os

@pytest.fixture
def sample_pdf(tmp_path):
    """Erstellt eine gültige Test-PDF mit ausreichend Text für das Chunking."""
    pdf_path = tmp_path / "test.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    text = """
    Überschrift 1
    Dies ist ein langer Absatz, der als Testinhalt dient. Er enthält mehrere Sätze, damit die Chunking-Funktion etwas zum Verarbeiten hat.
    
    Überschrift 2
    Hier beginnt ein neuer Abschnitt mit weiterem Inhalt, um das Chunking sinnvoll zu testen.
    """
    
    pdf.multi_cell(0, 10, txt=text)
    pdf.output(str(pdf_path))
    return str(pdf_path)

@pytest.fixture
def short_pdf(tmp_path):
    """Erstellt eine gültige PDF mit zu wenig Text für das Chunking."""
    pdf_path = tmp_path / "short.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt="Zu kurzer Text.")
    pdf.output(str(pdf_path))
    return str(pdf_path)

@pytest.fixture
def empty_pdf(tmp_path):
    """Erstellt eine leere, aber gültige PDF-Datei."""
    pdf_path = tmp_path / "empty.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.output(str(pdf_path))
    return str(pdf_path)

def test_pdf_parser_full_run(sample_pdf):
    """Testet den kompletten Verarbeitungsablauf des PDF-Parsers."""
    parser = PDFParser(sample_pdf)
    
    # Starte den Parsing-Prozess
    text_chunks = parser.extract_text(start_page=1, end_page=None)

    print(f"DEBUG: Extrahierter Text für 'sample_pdf': {text_chunks}")

    # **Test für normale PDF: Liste wird erwartet**
    if isinstance(text_chunks, list):
        assert len(text_chunks) > 0, "Die Liste sollte mindestens einen Textabschnitt enthalten."
    else:
        assert isinstance(text_chunks, str), f"Die Extraktion sollte eine Zeichenkette oder Liste zurückgeben, aber {type(text_chunks)} wurde zurückgegeben."

    # Falls der Text zu kurz ist, sollte chunk_text nicht aufgerufen werden
    if text_chunks == "PDF zu kurz":
        return  

    chunks = parser.chunk_text(min_tokens=50, max_tokens=300)
    
    assert isinstance(chunks, list), "Das Chunking sollte eine Liste zurückgeben."
    assert len(chunks) > 0, "Es sollten Chunks erstellt werden."
    
    # Sicherstellen, dass keine leeren Chunks existieren
    assert all(len(chunk) > 0 for chunk in chunks), "Kein Chunk sollte leer sein."

def test_pdf_parser_empty_file(empty_pdf):
    """Testet das Verhalten mit einer leeren PDF-Datei."""
    parser = PDFParser(empty_pdf)
    text_chunks = parser.extract_text(start_page=1, end_page=None)

    print(f"DEBUG: Extrahierter Text für 'empty_pdf': {text_chunks}")

    # **Falls die PDF leer ist, muss eine Zeichenkette zurückkommen**
    assert isinstance(text_chunks, str), f"Erwartet wurde eine Zeichenkette, aber {type(text_chunks)} wurde zurückgegeben."
    assert text_chunks == "PDF zu kurz", f"Erwartet wurde 'PDF zu kurz', aber '{text_chunks}' wurde zurückgegeben."

def test_pdf_parser_short_text(short_pdf):
    """Testet das Verhalten mit einer PDF, die zu wenig Text für Chunks enthält."""
    parser = PDFParser(short_pdf)
    text_chunks = parser.extract_text(start_page=1, end_page=None)

    print(f"DEBUG: Extrahierter Text für 'short_pdf': {text_chunks}")

    # **Falls die PDF zu kurz ist, darf entweder "PDF zu kurz" oder eine leere Liste zurückkommen**
    assert isinstance(text_chunks, (str, list)), f"Die Extraktion sollte eine Zeichenkette oder eine Liste zurückgeben, aber {type(text_chunks)} wurde zurückgegeben."
    assert text_chunks in ["PDF zu kurz", []], f"Erwartet wurde 'PDF zu kurz' oder '[]', aber '{text_chunks}' wurde zurückgegeben."

    chunks = parser.chunk_text(min_tokens=50, max_tokens=300)
    assert chunks in ["PDF zu kurz", []], f"Erwartet wurde 'PDF zu kurz' oder '[]', aber '{chunks}' wurde zurückgegeben."
