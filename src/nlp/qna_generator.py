import openai
from google import genai
import os
import logging
import re
import json



class QnAGenerator:
    def __init__(self, api_type, api_key=None):
        """
        Initialisiert den QnAGenerator für OpenAI, Gemini oder Manuell.
        """
        self.api_type = api_type.lower()  # "openai", "gemini", "manual"
        self.api_key = api_key  # API-Schlüssel für OpenAI & Gemini
        self.client = None

        if self.api_type == "openai":
            openai.api_key = api_key
            self.client = openai.OpenAI(api_key=api_key)

        elif self.api_type == "gemini":
            #genai.configure(api_key=api_key)
            self.client = genai.Client(api_key=api_key)
            self.model = "gemini-2.0-flash"

    def generate_qna_pairs(self, chunk, num_questions=3):
        """
        Generiert Fragen & Antworten basierend auf dem gewählten Modell.
        """
        logging.debug(f"Generiere QnA-Paare für {self.api_type}...")

        # Prompt vorbereiten
        prompt_template = self.load_dynamic_prompt()
        formatted_prompt = prompt_template.format(chunk=chunk, num_questions=num_questions)

        # API-Anfrage je nach Modell
        response_text = ""
        if self.api_type == "openai":
            response_text = self.call_openai(formatted_prompt)
        elif self.api_type == "gemini":
            response_text = self.call_gemini(formatted_prompt)
        elif self.api_type == "manual":
            response_text = "⚠ Manuelle Verarbeitung – Bitte Antwort eingeben."
        else:
            raise ValueError(f"Unbekannter API-Typ: {self.api_type}")

        # **🔍 Antwort analysieren & Fragen-Antworten extrahieren**
        qna_pairs = self.extract_qna_pairs(response_text)

        return qna_pairs

    def call_openai(self, prompt):
        """Sendet den Prompt an OpenAI GPT-3.5 Turbo."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Kostengünstigere Alternative
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"❌ OpenAI API-Fehler: {e}")
            return "⚠ Fehler bei OpenAI API-Aufruf."


    def call_gemini(self, prompt):
        """Sendet den Prompt an Gemini (Google AI)."""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[{"role": "user", "parts": [{"text": prompt}]}],
                config={
                    "temperature": 0.5,
                    "top_p": 0.9,
                    "max_output_tokens": 1000
                }
            )
            return response.text
        except Exception as e:
            logging.error(f"❌ Gemini API-Fehler: {e}")
            return "⚠ Fehler bei Gemini API-Aufruf."

    def extract_qna_pairs(self, response_text):
        """
        Extrahiert Fragen und Antworten aus der API-Antwort.
        Erkennt "Frage:", "Frage 1:", "Q:" usw.
        """
        logging.debug(f"Analysiere API-Antwort:\n{response_text}")

        qna_pairs = []
        questions = re.split(r"\b(?:Frage \d*|Frage|Q)[:\-\s]", response_text, flags=re.IGNORECASE)
        answers = re.split(r"\b(?:Antwort \d*|Antwort|A)[:\-\s]", response_text, flags=re.IGNORECASE)

        # Sicherstellen, dass Fragen & Antworten paarweise sind
        questions = [q.strip() for q in questions if q.strip()]
        answers = [a.strip() for a in answers if a.strip()]

        if len(questions) != len(answers):
            logging.warning("⚠ Achtung: Unterschiedliche Anzahl an Fragen und Antworten erkannt!")

        for q, a in zip(questions, answers):
            qna_pairs.append({"question": q, "answer": a})

        return qna_pairs

    def load_dynamic_prompt(self):
        """Lädt den dynamischen Prompt für das aktuelle Modell."""
        prompt_path = f"data/prompts/dynamic_prompt_{self.api_type}.json"
        try:
            with open(prompt_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data.get("template", "")  # Holt den Text aus dem JSON
        except FileNotFoundError:
            logging.error(f"⚠ Prompt-Datei nicht gefunden: {prompt_path}")
            return "Hier ist ein Textabschnitt: \"{chunk}\". Erstelle Fragen und Antworten."
