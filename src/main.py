from pdf_parser.pdf_parser import PDFParser
from nlp.qna_generator import QnAGenerator
import logging

# Logging-Konfiguration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Datei-Pfad zum Testen
    pdf_file = "data/input/beispiel.pdf"

    # Start- und Endseite vom Nutzer abfragen
    try:
        start_page = int(input("Ab welcher Seite soll das Parsing starten? (Standard: 1) ") or 1)
        end_page = input("Bis zu welcher Seite? (Leer lassen für bis Ende) ")
        end_page = int(end_page) if end_page else None
    except ValueError:
        logging.warning("Ungültige Eingabe! Es wird ab Seite 1 gestartet.")
        start_page = 1
        end_page = None

    # PDF-Parser initialisieren und Text ab `start_page` bis `end_page` extrahieren und Chunks erstellen
    parser = PDFParser(pdf_file)
    chunks = parser.extract_text(start_page, end_page)

    # Überprüfung, ob Chunks erfolgreich erstellt wurden
    if not chunks:
        logging.error("Keine Chunks zum Verarbeiten gefunden.")
        return
    logging.info(f"{len(chunks)} Chunks wurden erfolgreich erstellt.")
    
    # QnA-Generator initialisieren und Fragen generieren
    qna_generator = QnAGenerator()
    qna_pairs = qna_generator.generate_qna_pairs(chunks)
    
    # Überprüfung, ob Frage-Antwort-Paare generiert wurden
    if not qna_pairs:
        logging.error("Keine Fragen und Antworten generiert.")
        return
    logging.info(f"{len(qna_pairs)} Frage-Antwort-Paare generiert.")
    
    # Frage-Antwort-Paare in einer TXT-Datei speichern
    qna_generator.save_qna_to_txt(qna_pairs)
    logging.info("Frage-Antwort-Paare erfolgreich gespeichert.")

if __name__ == "__main__":
    main()
