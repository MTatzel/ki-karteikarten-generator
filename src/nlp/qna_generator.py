import openai
from openai import OpenAI
import json
import os
import logging
from datetime import datetime


class QnAGenerator:
    def __init__(self, api_key=None):
        """
        Initialisiert den QnAGenerator mit OpenAI API-Key
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API-Key nicht gesetzt!")
        
        # OpenAI API-Key konfigurieren
        openai.api_key = self.api_key

        # OpenAI Client konfigurieren
        self.client = OpenAI(api_key=self.api_key)

        # Prompt-Konfigurationen laden
        self.system_message = self.load_system_message()
        self.dynamic_prompt = self.load_dynamic_prompt()

        # Zähler für Fragen initialisieren
        self.question_count = 0

    def load_system_message(self, file_path="data/prompts/system_message.json"):
        """
        Lädt die System-Nachricht aus der JSON-Datei
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"System-Nachricht Datei '{file_path}' nicht gefunden.")
        
        with open(file_path, "r", encoding="utf-8") as file:
            system_message = json.load(file)
        return system_message

    def load_dynamic_prompt(self, file_path="data/prompts/dynamic_prompt.json"):
        """
        Lädt die dynamische Prompt-Vorlage aus der JSON-Datei
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dynamischer Prompt '{file_path}' nicht gefunden.")
        
        with open(file_path, "r", encoding="utf-8") as file:
            dynamic_prompt = json.load(file)
        return dynamic_prompt

    def generate_qna_pairs(self, chunk, num_questions=3):
        """
        Generiert Frage-Antwort-Paare mit OpenAI GPT-3.5/4 für den übergebenen Chunk
        """
        # Dynamischen Prompt erstellen
        prompt = self.dynamic_prompt["template"].format(chunk=chunk, num_questions=num_questions)

        # Anfrage an OpenAI API mit der korrekten Methode
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": self.system_message["content"]},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )

        # Antwort korrekt aus dem ChatCompletion-Objekt extrahieren
        answer = response.choices[0].message.content

        try:
            qna_pairs = json.loads(answer)
            if not isinstance(qna_pairs, list):  # Sicherstellen, dass die Antwort eine Liste ist
                logging.error("Fehler: OpenAI hat kein gültiges JSON-Array zurückgegeben.")
                return []
        except json.JSONDecodeError:
            logging.error("JSON-Fehler: Die Antwort von OpenAI ist kein gültiges JSON.")
            return []

        # Überprüfung auf irrelevante Antworten
        if len(qna_pairs) == 1 and qna_pairs[0]["question"] == "irrelevant":
            logging.info("Irrelevanter Chunk – keine Fragen und Antworten generiert.")
            return []

        return qna_pairs

    def save_qna_to_txt(self, qna_pairs, output_dir="data/output"):
        """
        Speichert die Frage-Antwort-Paare in einer neuen TXT-Datei pro Programmausführung.
        Der Dateiname enthält einen Zeitstempel, um Überschreiben zu vermeiden.
        """
        # Verzeichnis erstellen, falls es noch nicht existiert
        os.makedirs(output_dir, exist_ok=True)

        # Erstelle Dateinamen mit Zeitstempel
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = os.path.join(output_dir, f"qna_output_{timestamp}.txt")

        # Datei öffnen und speichern
        with open(output_file, "w", encoding="utf-8") as file:
            for i, qna in enumerate(qna_pairs):
                self.question_count += 1
                file.write(f"Frage {self.question_count}: {qna['question']}\n")
                file.write(f"Antwort {self.question_count}: {qna['answer']}\n")
                file.write("\n" + "-"*40 + "\n\n")  # Trennlinie zwischen den Fragen

        logging.info(f"Frage-Antwort-Paare wurden in '{output_file}' gespeichert.")


    def save_qna_to_anki(self, qna_pairs, output_dir="data/output"):
        """
        Speichert die Frage-Antwort-Paare im Anki-kompatiblen CSV-Format mit Zeitstempel
        - Tabulator als Trennzeichen für Anki
        - UTF-8 Kodierung für Umlaute und Sonderzeichen
        """
        # Verzeichnis erstellen, falls es noch nicht existiert
        os.makedirs(output_dir, exist_ok=True)

        # Erstelle Dateinamen mit Zeitstempel
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = os.path.join(output_dir, f"qna_anki_{timestamp}.csv")

        # Datei öffnen und speichern
        with open(output_file, "w", encoding="utf-8") as file:
            for qna in qna_pairs:
                # Frage und Antwort mit Tabulator trennen
                file.write(f"{qna['question']}\t{qna['answer']}\n")

        logging.info(f"Frage-Antwort-Paare wurden in Anki-CSV '{output_file}' gespeichert.")

