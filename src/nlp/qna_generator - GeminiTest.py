# AIzaSyB9xtpOty6afrTYwBO4W-oKn2NeBVxVYcY

import base64
import os
import json
import logging
from google import genai
from google.genai import types

class QnAGenerator:
    def __init__(self, api_key=None):
        """
        Initialisiert den QnAGenerator mit Gemini API-Key
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") 
        if not self.api_key:
            raise ValueError("Gemini API-Key nicht gesetzt!")
        
        # Gemini Client konfigurieren
        self.client = genai.Client(api_key=self.api_key)

        # Modellname für Gemini
        self.model = "gemini-2.0-flash"

        # Zähler für Fragen initialisieren
        self.question_count = 0

    def generate_qna_pairs(self, chunk, num_questions=3):
        """
        Generiert Frage-Antwort-Paare mit Gemini für den übergebenen Chunk
        """
        # Optimierter Prompt mit klarer Anweisung zur JSON-Antwort
        prompt = (
            f"Erstelle {num_questions} Frage-Antwort-Paare basierend auf folgendem Text:\n"
            f"{chunk}\n"
            "Gib die Antwort bitte im JSON-Format zurück, in folgender Struktur:\n"
            '[\n'
            '  {"question": "Frage 1", "answer": "Antwort 1"},\n'
            '  {"question": "Frage 2", "answer": "Antwort 2"},\n'
            '  {"question": "Frage 3", "answer": "Antwort 3"}\n'
            ']\n'
            "Stelle sicher, dass die Ausgabe ein valides JSON-Format hat."
        )

        # Anfrage-Konfiguration für Gemini
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            temperature=0.5,  # Niedrigere Temperatur für präzisere JSON-Ausgaben
            top_p=0.9,
            top_k=40,
            max_output_tokens=1000,
            response_mime_type="text/plain",
        )

        # Anfrage an Gemini API mit Stream-Verarbeitung
        answer = ""
        for chunk in self.client.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=generate_content_config,
        ):
            answer += chunk.text

        # JSON-String in Python-Objekt umwandeln
        try:
            qna_pairs = json.loads(answer)
            return qna_pairs
        except json.JSONDecodeError:
            logging.error("Ungültiges JSON-Format in der Antwort.")
            # Speichern der Roh-Antwort zur Analyse
            output_file = "data/output/raw_gemini_response.txt"
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, "a", encoding="utf-8") as file:
                file.write(answer + "\n\n")
            logging.info(f"Roh-Antwort von Gemini wurde in '{output_file}' gespeichert.")
            return []

    def save_qna_to_txt(self, qna_pairs, output_file="data/output/qna_output.txt"):
        """
        Speichert die Frage-Antwort-Paare in einer TXT-Datei
        """
        # Verzeichnis erstellen, falls es noch nicht existiert
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Datei öffnen und vorher leeren (Modus "w" = write)
        with open(output_file, "a", encoding="utf-8") as file:
            for i, qna in enumerate(qna_pairs):
                self.question_count += 1
                file.write(f"Frage {self.question_count}: {qna['question']}\n")
                file.write(f"Antwort {self.question_count}: {qna['answer']}\n")
                file.write("\n" + "-"*40 + "\n\n")  # Trennlinie zwischen den Fragen
        
        logging.info(f"Frage-Antwort-Paare wurden in '{output_file}' gespeichert.")
