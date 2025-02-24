from pdf_parser.pdf_parser import PDFParser
from nlp.qna_generator import QnAGenerator

def main():
    # Datei-Pfad zum Testen
    pdf_file = "data/input/beispiel.pdf"

    # Startseite vom Nutzer abfragen
    try:
        start_page = int(input("Ab welcher Seite soll das Parsing starten? (Standard: 1) ") or 1)
    except ValueError:
        print("Ungültige Eingabe! Es wird ab Seite 1 gestartet.")
        start_page = 1

    # PDF-Parser initialisieren und Text ab `start_page` extrahieren
    parser = PDFParser(pdf_file)
    parser.extract_text(start_page)
    chunks = parser.chunk_text()

    # QnA-Generator initialisieren und Fragen generieren
    qna_generator = QnAGenerator()
    qna_pairs = qna_generator.generate_qna_pairs(chunks)

    # Frage-Antwort-Paare in einer TXT-Datei speichern
    qna_generator.save_qna_to_txt(qna_pairs)

if __name__ == "__main__":
    main()
