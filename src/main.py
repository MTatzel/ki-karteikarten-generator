from pdf_parser.pdf_parser import PDFParser
from nlp.qna_generator import QnAGenerator
import logging
import tiktoken  # OpenAI Tokenizer
import os
from datetime import datetime

# Logging-Konfiguration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Datei-Pfad zum Testen
    pdf_file = "data/input/beispiel.pdf"

    # PDF-Parser initialisieren und Text extrahieren
    parser = PDFParser(pdf_file)
    extracted_text = parser.extract_text()  # Text explizit speichern
    
    # Überprüfung, ob Text extrahiert wurde
    if not extracted_text:
        logging.error("Kein Text aus dem PDF extrahiert.")
        return
    logging.info("Text wurde erfolgreich aus dem PDF extrahiert.")
    
    # Chunks erstellen
    chunks = parser.chunk_text(min_tokens=200, max_tokens=1000)

    # Überprüfung, ob Chunks erfolgreich erstellt wurden
    if not chunks:
        logging.error("Keine Chunks zum Verarbeiten gefunden.")
        return
    logging.info(f"{len(chunks)} Chunks wurden erfolgreich erstellt.")
    
    # QnA-Generator initialisieren
    qna_generator = QnAGenerator()

    # Tokenizer für Token-Zählung
    enc = tiktoken.get_encoding("cl100k_base")

    # Liste für alle generierten QnA-Paare
    all_qna_pairs = []

    # Dynamische Frage-Antwort-Erstellung für jeden Chunk
    for i, chunk in enumerate(chunks):
        # Anzahl der Fragen dynamisch berechnen (1 Frage pro 150 Tokens, max. 5)
        token_count = len(enc.encode(chunk))
        num_questions = max(1, min(token_count // 150, 5))

        logging.info(f"Generiere {num_questions} Fragen für Chunk {i+1}/{len(chunks)}...")

        # Frage-Antwort-Paare generieren
        qna_pairs = qna_generator.generate_qna_pairs(chunk, num_questions=num_questions)

        # Überprüfung, ob Frage-Antwort-Paare generiert wurden
        if not qna_pairs:
            logging.warning(f"Keine Fragen für Chunk {i+1} generiert.")
            continue

        logging.info(f"{len(qna_pairs)} Fragen für Chunk {i+1} generiert.")
        all_qna_pairs.extend(qna_pairs)

    # Falls keine Fragen generiert wurden, abbrechen
    if not all_qna_pairs:
        logging.warning("Es wurden keine Fragen generiert. Datei wird nicht gespeichert.")
        return

    # Zeitstempel für den Dateinamen generieren
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Speicherorte für TXT & Anki-CSV
    output_dir = "data/output"
    os.makedirs(output_dir, exist_ok=True)
    output_txt = os.path.join(output_dir, f"qna_output_{timestamp}.txt")
    output_anki = os.path.join(output_dir, f"qna_anki_{timestamp}.csv")

    # Frage-Antwort-Paare speichern
    qna_generator.save_qna_to_txt(all_qna_pairs, output_txt)
    qna_generator.save_qna_to_anki(all_qna_pairs, output_anki)

    logging.info(f"Frage-Antwort-Paare erfolgreich gespeichert:\nTXT: {output_txt}\nAnki: {output_anki}")

if __name__ == "__main__":
    main()
