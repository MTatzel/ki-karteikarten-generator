import fitz  # PyMuPDF
import os

class PDFParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.raw_text = ""
        self.chunks = []

    def extract_text(self):
        """
        Extrahiert den Text aus dem PDF und speichert ihn in `self.raw_text`
        """
        # Prüfen, ob die Datei existiert
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Die Datei '{self.file_path}' wurde nicht gefunden.")
        
        # PDF öffnen und Seiten durchlaufen
        pdf = fitz.open(self.file_path)
        text = ""
        for page in pdf:
            text += page.get_text("text")
        
        # Gesamten Text speichern und zurückgeben
        self.raw_text = text
        return self.raw_text

    def chunk_text(self, max_words=250):
        """
        Teilt den Text in Abschnitte (Chunks) mit `max_words` Wörtern pro Chunk
        """
        if not self.raw_text:
            raise ValueError("Es wurde noch kein Text extrahiert. Bitte zuerst `extract_text()` ausführen.")
        
        words = self.raw_text.split()
        chunk = []
        chunk_count = 0
        
        for word in words:
            chunk.append(word)
            if len(chunk) >= max_words:
                self.chunks.append(" ".join(chunk))
                chunk = []
                chunk_count += 1
        
        # Restliche Wörter als letzter Chunk
        if chunk:
            self.chunks.append(" ".join(chunk))
        
        print(f"{chunk_count+1} Chunks mit maximal {max_words} Wörtern wurden erstellt.")
        return self.chunks
