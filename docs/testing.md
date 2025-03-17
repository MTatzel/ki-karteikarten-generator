# Teststrategie

## Übersicht
Das Testkonzept für den Karteikarten-Generator umfasst **Unit-Tests, Integrationstests und manuelle Tests**. Ziel ist es, die **Funktionalität, Stabilität und korrekte Verarbeitung der PDF-Daten und API-Kommunikation** sicherzustellen.

## Testarten

### 1. **Unittests**
- Getestete Komponenten:
  - `PDFParser`: Extraktion und Chunking von PDF-Dokumenten
  - `QnAGenerator`: Verarbeitung von Chunks und Generierung von Fragen-Antwort-Paaren
  - `GUI`: Interaktion der UI-Elemente
- **Framework:** `pytest`
- **Testausführung:**
  ```sh
  pytest tests/
  ```

### 2. **Integrationstests**
- Überprüfung der **Kommunikation zwischen Komponenten**:
  - `PDFParser` → `QnAGenerator` → `GUI`
  - API-Anbindung an OpenAI/Gemini
- Fokus auf **richtige Datenflüsse & API-Response-Handling**
- Automatisierte Tests mit **Mocking der API-Aufrufe**

### 3. **Manuelle Tests**
- **GUI-Tests**: Manuelle Validierung der Navigation & UI-Elemente
- **End-to-End-Test**: Hochladen einer PDF, Generierung & Export
- **Fehlertests**: Falsche Eingaben, ungültige API-Schlüssel, leere PDFs

## Testabdeckung
| Komponente       | Unittests | Integrationstests | Manuelle Tests |
|-----------------|-----------|------------------|---------------|
| PDFParser       | ✅        | ✅               | 🔄 Manuelle Validierung |
| QnAGenerator    | ✅        | ✅               | 🔄 Manuelle Validierung |
| GUI             | 🔄 Teilweise | ✅               | ✅ Umfangreich |
| API-Kommunikation | ❌ Mocking | ✅               | 🔄 Begrenzte Validierung |

## Testdaten & Mocking
- **Unit-Tests nutzen kleine, fest definierte Testdateien** für PDF-Parsing.
- **API-Aufrufe werden mit Mocking simuliert**, um Kosten zu vermeiden.
- **Fehlerszenarien werden mit Edge Cases getestet** (z. B. leere Antworten, Zeitüberschreitungen).

## Testausführung
Die Tests können mit folgendem Befehl ausgeführt werden:
```sh
pytest --cov=src tests/
```

⚠ **Hinweis:** Einige Tests (z. B. API-Anfragen) können Kosten verursachen, falls keine Mocking-Umgebung verwendet wird.

## Fazit
Durch die Kombination aus **automatisierten und manuellen Tests** wird sichergestellt, dass der Karteikarten-Generator zuverlässig funktioniert und Fehlerszenarien korrekt behandelt werden.
