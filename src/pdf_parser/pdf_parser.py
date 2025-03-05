import fitz  # PyMuPDF
import re
import os
import logging
from statistics import mean
import tiktoken  # OpenAI Tokenizer

class PDFParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.raw_text = ""
        self.chunks = []

    def analyze_average_font_size(self):
        """
        Berechnet die durchschnittliche Schriftgröße im PDF, um Überschriften zu erkennen
        """
        document = fitz.open(self.file_path)
        font_sizes = []

        # Alle Seiten durchgehen, um die durchschnittliche Schriftgröße zu berechnen
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            blocks = page.get_text("dict")["blocks"]

            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            font_sizes.append(span["size"])

        # Durchschnittliche Schriftgröße berechnen
        avg_font_size = mean(font_sizes) if font_sizes else 0
        return avg_font_size

    def extract_text(self, start_page=1, end_page=None):
        """
        Extrahiert den Text aus dem PDF und rekonstruiert Absätze
        - Mehrzeilige Überschriften werden flexibler erkannt
        - Fließtext direkt nach Überschrift wird immer als zugehöriger Absatz erkannt
        - Seitenumbrüche werden ignoriert, um Sätze zusammenzuhalten
        """
        if not os.path.exists(self.file_path):
            logging.error(f"Die Datei '{self.file_path}' wurde nicht gefunden.")
            raise FileNotFoundError(f"Die Datei '{self.file_path}' wurde nicht gefunden.")

        pdf = fitz.open(self.file_path)
        num_pages = len(pdf)

        if start_page < 1 or start_page > num_pages:
            raise ValueError(f"Ungültige Startseite: {start_page}. Das PDF hat {num_pages} Seiten.")

        if end_page is None or end_page > num_pages:
            end_page = num_pages

        logging.info(f"Starte Parsing ab Seite {start_page} bis Seite {end_page} von insgesamt {num_pages} Seiten.")

        # Durchschnittliche Schriftgröße berechnen
        avg_font_size = self.analyze_average_font_size()
        current_chunk = []
        text = ""
        potential_heading = []

        for page_num in range(start_page - 1, end_page):
            page = pdf.load_page(page_num)
            blocks = page.get_text("dict")["blocks"]

            # Textblöcke durchgehen
            for i, block in enumerate(blocks):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            font_size = span["size"]
                            is_bold = "Bold" in span["font"]
                            text_content = span["text"].strip()

                            # Überschriftskriterien:
                            # 1. Schriftgröße größer als Durchschnitt + Toleranz
                            # 2. Oder: Fett und gleiche Größe wie Durchschnitt
                            if (font_size > avg_font_size + 1) or (is_bold and font_size >= avg_font_size):
                                # Prüfen, ob es sich um eine mehrzeilige Überschrift handelt
                                if potential_heading:
                                    # Zusammenfassen, wenn gleiche Schriftgröße und kein Punkt am Ende
                                    potential_heading.append(text_content)
                                    continue
                                else:
                                    # Speichern des vorherigen Chunks (falls vorhanden)
                                    if current_chunk:
                                        self.chunks.append(" ".join(current_chunk))
                                        current_chunk = []

                                    # Start einer neuen potenziellen Überschrift
                                    potential_heading = [text_content]
                                    continue

                            # Wenn potenzielle Überschrift vorhanden, prüfen ob danach Fließtext folgt
                            if potential_heading:
                                # Mehrzeilige Überschrift zusammenfassen
                                combined_heading = " ".join(potential_heading)
                                # Immer als Überschrift speichern, unabhängig vom Fließtext
                                current_chunk.append(combined_heading)
                                current_chunk.append(text_content)
                                potential_heading = []
                            else:
                                # Normaler Fließtext
                                current_chunk.append(text_content)

        # Restliche Absätze als letzten Chunk speichern
        if current_chunk:
            self.chunks.append(" ".join(current_chunk))

        # Setze self.raw_text für Kompatibilität mit chunk_text()
        self.raw_text = "\n\n".join(self.chunks)

        # DEBUG: Ausgabe des extrahierten Textes und self.raw_text
        logging.debug(f"Extrahierter Text: {self.raw_text[:500]}...")  # Nur die ersten 500 Zeichen

        print(f"{len(self.chunks)} Chunks wurden erstellt.")
        self.save_chunks_to_txt()
        return self.chunks


    def chunk_text(self, min_tokens=200, max_tokens=1000):
        """
        Chunks basierend auf Überschriften erstellen
        - Startet einen neuen Chunk bei jeder Überschrift
        - Chunks gehen bis zur nächsten Überschrift
        - Token-Limits werden berücksichtigt, aber Absätze werden nie getrennt
        """
        if not self.raw_text:
            raise ValueError("Es wurde noch kein Text extrahiert. Bitte zuerst `extract_text()` ausführen.")

        paragraphs = self.raw_text.split("\n\n")
        current_chunk = []
        enc = tiktoken.get_encoding("cl100k_base")

        i = 0
        while i < len(paragraphs):
            para = paragraphs[i].strip()

            # Token-Zählung für den aktuellen Chunk
            current_text = " ".join(current_chunk)
            token_count = len(enc.encode(current_text))

            # Chunk nur am Ende eines vollständigen Absatzes speichern
            # Nie mitten im Absatz oder Satz
            if token_count > max_tokens:
                self.chunks.append(current_text)
                current_chunk = []

            i += 1

        # Restliche Absätze als letzten Chunk speichern
        if current_chunk:
            self.chunks.append(" ".join(current_chunk))

        logging.info(f"{len(self.chunks)} Chunks vor der Optimierung.")
        self.merge_small_chunks() 
        logging.info(f"{len(self.chunks)} Chunks nach der Optimierung.")

        print(f"{len(self.chunks)} Chunks wurden erstellt.")
        self.save_chunks_to_txt()
        return self.chunks
    
    def merge_small_chunks(self, min_tokens=50):
        """
        Geht alle Chunks durch und fügt zu kleine Chunks zum nächsten oder vorherigen hinzu
        """
        enc = tiktoken.get_encoding("cl100k_base")
        merged_chunks = []

        i = 0
        while i < len(self.chunks):
            current_chunk = self.chunks[i]
            token_count = len(enc.encode(current_chunk))

            if token_count < min_tokens:
                # Wenn es nicht der letzte Chunk ist, an den nächsten anhängen
                if i + 1 < len(self.chunks):
                    self.chunks[i + 1] = current_chunk + " " + self.chunks[i + 1]
                # Falls es der letzte Chunk ist, an den vorherigen anhängen
                elif i > 0:
                    merged_chunks[-1] += " " + current_chunk
            else:
                merged_chunks.append(current_chunk)

            i += 1

        self.chunks = merged_chunks

    def save_chunks_to_txt(self, output_file="data/output/chunks.txt"):
        """
        Speichert alle Chunks in einer TXT-Datei
        Überschreibt die Datei bei jedem Durchlauf
        """
        # Verzeichnis erstellen, falls es noch nicht existiert
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Datei öffnen und vorher leeren (Modus "w" = write)
        with open(output_file, "w", encoding="utf-8") as file:
            for i, chunk in enumerate(self.chunks):
                file.write(f"Chunk {i+1}:\n")
                file.write(chunk)
                file.write("\n" + "-"*40 + "\n\n")  # Trennlinie zwischen den Chunks

        logging.info(f"Chunks wurden in '{output_file}' gespeichert.")
