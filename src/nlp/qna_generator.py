from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch
import os

class QnAGenerator:
    def __init__(self, model_name="google/flan-t5-base"):
        # Modell und Tokenizer laden
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)
        self.model.eval()  # Modell in den Inferenzmodus setzen
        
        # Prüfen, ob GPU verfügbar ist (für schnellere Verarbeitung)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        print(f"QnA-Modell läuft auf: {self.device}")

    def generate_question(self, context, max_new_tokens=100, max_input_length=400):
        """
        Generiert eine Frage aus einem gegebenen Kontext (Chunk)
        """
        # Kontext kürzen, wenn er zu lang ist
        input_ids = self.tokenizer.encode(context, return_tensors="pt")
        if len(input_ids[0]) > max_input_length:
            print(f"Warnung: Chunk zu lang ({len(input_ids[0])} Tokens). Kürze auf {max_input_length} Tokens.")
            context = self.tokenizer.decode(input_ids[0][:max_input_length], skip_special_tokens=True)
        
        # Präziserer Prompt zur Fragegenerierung
        prompt = (
            f"Hier ist ein Textabschnitt:\n{context}\n"
            f"Formuliere eine konkrete Frage zu diesem Textabschnitt und beantworte sie knapp und präzise.\n"
            f"Frage: "
        )
        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to(self.device)

        # Textgenerierung mit Flan-T5
        output = self.model.generate(
            input_ids,
            max_new_tokens=max_new_tokens,  # Begrenzung auf 100 Tokens für die Ausgabe
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )

        # Ausgabe dekodieren und Frage-Antwort-Paar zurückgeben
        generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
        
        # Ausgabe in Frage und Antwort aufteilen
        if "Frage:" in generated_text and "Antwort:" in generated_text:
            question, answer = generated_text.split("Antwort:")
            question = question.replace("Frage:", "").strip()
            return question.strip(), answer.strip()
        else:
            return "Keine sinnvolle Frage generiert", "Keine sinnvolle Antwort generiert"

    def generate_qna_pairs(self, chunks):
        """
        Generiert Frage-Antwort-Paare für eine Liste von Chunks
        """
        qna_pairs = []
        for i, chunk in enumerate(chunks):
            print(f"\nGeneriere Frage aus Chunk {i+1}:")
            question, answer = self.generate_question(chunk)
            qna_pairs.append({"question": question, "answer": answer})
            print(f"Frage: {question}\nAntwort: {answer}")
        
        return qna_pairs

    def save_qna_to_txt(self, qna_pairs, output_file="data/output/qna.txt"):
        """
        Speichert alle Frage-Antwort-Paare in einer TXT-Datei
        Überschreibt die Datei bei jedem Durchlauf
        """
        # Verzeichnis erstellen, falls es noch nicht existiert
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Datei öffnen und vorher leeren (Modus "w" = write)
        with open(output_file, "w", encoding="utf-8") as file:
            for i, pair in enumerate(qna_pairs):
                file.write(f"Frage {i+1}: {pair['question']}\n")
                file.write(f"Antwort {i+1}: {pair['answer']}\n")
                file.write("\n" + "-"*40 + "\n\n")  # Trennlinie zwischen den Paaren
        
        print(f"Frage-Antwort-Paare wurden in '{output_file}' gespeichert.")
