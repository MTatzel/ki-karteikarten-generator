from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import os

class QnAGenerator:
    def __init__(self, model_name="google/mt5-base"):
        print("Nix")

    def generate_question(self, context, max_new_tokens=150, max_input_length=250):
        """
        Generiert eine Frage und Antwort aus einem gegebenen Kontext (Chunk)
        """
        


    def generate_qna_pairs(self, chunks):
        """
        Generiert Frage-Antwort-Paare für eine Liste von Chunks
        """
        

    def save_qna_to_txt(self, qna_pairs, output_file="data/output/qna.txt"):
        """
        Speichert alle Frage-Antwort-Paare in einer TXT-Datei
        Überschreibt die Datei bei jedem Durchlauf
        """
        
