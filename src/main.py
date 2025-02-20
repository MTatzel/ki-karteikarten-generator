from pdf_parser.pdf_parser import PDFParser

def main():
    # Datei-Pfad zum Testen
    pdf_file = "data/input/beispiel.pdf"  # Stelle sicher, dass hier eine Test-PDF liegt!

    # PDF-Parser initialisieren und Text extrahieren
    parser = PDFParser(pdf_file)
    text = parser.extract_text()
    print("\nExtrahierter Text:")
    print(text[:500])  # Nur die ersten 500 Zeichen anzeigen

    # Text in Chunks teilen
    chunks = parser.chunk_text()
    print("\nErste 3 Chunks:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\nChunk {i+1}:")
        print(chunk)

if __name__ == "__main__":
    main()
