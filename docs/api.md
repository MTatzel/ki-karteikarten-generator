# API-Spezifikationen

## Übersicht
Der Karteikarten-Generator nutzt externe APIs zur **automatischen Generierung von Frage-Antwort-Paaren**. Unterstützte APIs:
- **OpenAI GPT (gpt-3.5-turbo, gpt-4)**
- **Google Gemini (gemini-2.0-flash)**

## API-Integration
Die API wird innerhalb der Klasse `QnAGenerator` verwendet. Je nach Auswahl sendet die Anwendung Text-Chunks zur Verarbeitung an die API.

## API-Anforderungen
- **Authentifizierung:** API-Schlüssel erforderlich (über GUI einzugeben oder als Umgebungsvariable zu setzen)
- **Datenübermittlung:** Die Anwendung sendet die zu verarbeitenden Textabschnitte als Klartext-String an die API und erwartet formatierte Antworten.(über GUI einzugeben oder als Umgebungsvariable zu setzen)
- **Datenformat:**
  ```json
  {
    "chunk": "Hier ist der zu verarbeitende Textabschnitt...",
    "num_questions": 3
  }
  ```
- **Antwortformat:**
  ```json
  [
    { "question": "Was ist X?", "answer": "X ist..." },
    { "question": "Warum ist X wichtig?", "answer": "Weil..." }
  ]
  ```

## Endpunkte
### OpenAI GPT
- **URL:** `https://api.openai.com/v1/chat/completions`
- **Header:**
  ```json
  {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
  }
  ```
- **Body (vom System generiert, Beispiel für Klartext-Eingabe):**
  ```text
  Erstelle drei Fragen und Antworten basierend auf folgendem Text:
  "Hier ist der zu verarbeitende Textabschnitt..."
  ```

### Google Gemini
- **URL:** `https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent`
- **Body (vom System generiert, Beispiel für Klartext-Eingabe):**
  ```text
  Erstelle drei Fragen und Antworten basierend auf folgendem Text:
  "Hier ist der zu verarbeitende Textabschnitt..."
  ```
- **URL:** `https://api.openai.com/v1/chat/completions`
- **Header:**
  ```json
  {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
  }
  ```
- **Body:**
  ```json
  {
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "user", "content": "Erstelle Fragen aus: <chunk>"}
    ],
    "max_tokens": 1000
  }
  ```

### Google Gemini
- **URL:** `https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent`
- **Body:**
  ```json
  {
    "model": "gemini-2.0-flash",
    "contents": [{"role": "user", "parts": [{"text": "Erstelle Fragen aus: <chunk>"}]}],
    "temperature": 0.5,
    "max_output_tokens": 1000
  }
  ```

## Fehlerbehandlung
| Fehler | Ursache | Lösung |
|--------|--------|--------|
| `401 Unauthorized` | Ungültiger API-Schlüssel | Prüfen, ob API-Key korrekt eingegeben wurde |
| `429 Too Many Requests` | API-Limit erreicht | Wartezeit oder geringere Anzahl an Anfragen |
| `500 Internal Server Error` | Serverproblem | Erneute Anfrage nach einiger Zeit |

## Kostenhinweis
⚠ **Die Nutzung der APIs kann Kosten verursachen**, insbesondere bei hohen Token-Werten. Es wird empfohlen, ein **API-Limit zu setzen**, um unkontrollierte Kosten zu vermeiden.

## Fazit
Die API-Anbindung ermöglicht eine leistungsfähige automatische Generierung von Lerninhalten. Durch geeignete Fehlerbehandlung und Kostenkontrolle kann eine effiziente Nutzung sichergestellt werden.
