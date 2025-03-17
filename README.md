# Karteikarten-Generator

## Projektbeschreibung
Der Karteikarten-Generator ist eine Anwendung zur automatischen Erstellung von Frage-Antwort-Karten aus PDF-Dokumenten. Die Software nutzt NLP-Modelle wie OpenAI oder Google Gemini, um relevante Fragen und Antworten aus Textabschnitten zu extrahieren und sie in verschiedenen Formaten zu speichern.

## Funktionen
- PDF-Analyse und Textextraktion
- Automatische Erstellung von Frage-Antwort-Karten
- Unterstützung für OpenAI und Gemini APIs
- Manuelle Bearbeitung der generierten Inhalte
- Exportmöglichkeiten in CSV, TXT und PDF

## Systemarchitektur
Das System besteht aus mehreren Komponenten:
- **GUI (Stepper-Interface)** – Steuert die Benutzerinteraktion
- **PDF-Parser** – Analysiert und zerlegt PDF-Dokumente in Textabschnitte
- **QnA-Generator** – Erstellt Frage-Antwort-Paare mithilfe von KI
- **Externe API** – Anbindung an OpenAI/Gemini für NLP-Prozesse

Die detaillierte Systemarchitektur ist in der Datei `docs/architecture.md` beschrieben.

## Installation & Nutzung
### Voraussetzungen
- Python 3.8+
- Abhängigkeiten aus `requirements.txt`

### Installation
```sh
pip install -r requirements.txt
```

### Anwendung starten
```sh
python main.py
```

## API-Integration
Die Anwendung unterstützt folgende APIs:
- **OpenAI API** – GPT-3.5 zur Generierung von Fragen und Antworten
- **Gemini API** – Google AI für NLP-Verarbeitung

Die API-Schlüssel müssen in der Anwendung eingegeben oder als Umgebungsvariablen gespeichert werden.

## Tests
Es sind automatisierte Tests für zentrale Komponenten der Anwendung implementiert.
- **Unittests** für den `PDFParser` und `QnAGenerator`
- **Integrationstests** für API-Aufrufe

Tests ausführen:
```sh
pytest tests/
```

## Dokumentation
Detaillierte technische Dokumentation:
- **`docs/architecture.md`** – Systemübersicht mit UML/C4-Diagrammen
- **`docs/usage.md`** – Benutzeranleitung und Wireframes
- **`docs/api.md`** – API-Spezifikationen
- **`docs/testing.md`** – Beschreibung der Teststrategie

## Lizenz
Dieses Projekt steht unter der MIT-Lizenz. Weitere Informationen in der Datei `LICENSE`.

## Autor
- Markus Tatzel
