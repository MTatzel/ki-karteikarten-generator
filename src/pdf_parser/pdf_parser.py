import fitz  # PyMuPDF
import os

class PDFParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.raw_text = ""
        self.chunks = []

    def extract_text(self, start_page=1):
        """
        Extrahiert den Text aus dem PDF und rekonstruiert Absätze
        Ab der angegebenen `start_page`
        """
        # Prüfen, ob die Datei existiert
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Die Datei '{self.file_path}' wurde nicht gefunden.")
        
        # PDF öffnen und Seiten durchlaufen
        pdf = fitz.open(self.file_path)
        num_pages = len(pdf)
        
        # Überprüfen, ob die Startseite gültig ist
        if start_page < 1 or start_page > num_pages:
            raise ValueError(f"Ungültige Startseite: {start_page}. Das PDF hat {num_pages} Seiten.")
        
        print(f"Starte Parsing ab Seite {start_page} von insgesamt {num_pages} Seiten.")
        
        text = ""
        for page_num in range(start_page - 1, num_pages):
            page = pdf.load_page(page_num)
            page_dict = page.get_text("dict")
            blocks = page_dict["blocks"]
            
            # Absätze aus den Blöcken rekonstruiert
            for block in blocks:
                if block["type"] == 0:  # Nur Textblöcke (type 0) verarbeiten
                    lines = block["lines"]
                    paragraph = []
                    for line in lines:
                        span_texts = [span["text"].strip() for span in line["spans"]]
                        # Zeilen zusammenführen und als Absatz speichern
                        paragraph.append(" ".join(span_texts))
                    
                    # Absatz speichern, falls nicht leer
                    full_paragraph = " ".join(paragraph).strip()
                    if full_paragraph:
                        text += full_paragraph + "\n\n"  # Absatzweise speichern
        
        # Gesamten Text speichern und zurückgeben
        self.raw_text = text
        return self.raw_text

    def chunk_text(self, min_words=200):
        """
        Teilt den Text in Absätze und kombiniert kleine Absätze zu sinnvollen Chunks
        """
        if not self.raw_text:
            raise ValueError("Es wurde noch kein Text extrahiert. Bitte zuerst `extract_text()` ausführen.")
        
        paragraphs = self.raw_text.split("\n\n")  # Absätze anhand von Leerzeilen trennen
        current_chunk = []
        chunk_word_count = 0
        
        for para in paragraphs:
            words = para.split()
            word_count = len(words)
            
            # Absatz nur übernehmen, wenn er nicht leer ist
            if word_count == 0:
                continue
            
            # Absatz zum aktuellen Chunk hinzufügen
            current_chunk.append(para)
            chunk_word_count += word_count
            
            # Wenn Mindestanzahl an Wörtern erreicht ist, Chunk speichern
            if chunk_word_count >= min_words:
                self.chunks.append("\n\n".join(current_chunk))
                current_chunk = []  # Chunk zurücksetzen
                chunk_word_count = 0
        
        # Restliche Absätze als letzten Chunk speichern
        if current_chunk:
            self.chunks.append("\n\n".join(current_chunk))
        
        print(f"{len(self.chunks)} Chunks wurden erstellt.")
        return self.chunks
    
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
        
        print(f"Chunks wurden in '{output_file}' gespeichert.")
