import logging
from nlp.qna_generator import QnAGenerator

# Logging aktivieren
logging.basicConfig(level=logging.DEBUG)

def test_qna_extraction_new():
    """
    Testet die Extraktion mit einem neuen Beispieltext.
    """
    generator = QnAGenerator(api_type="manual")

    response_text = """
    **Frage 1:**  
    Welche mechanischen Hilfsmittel nutzten die Babylonier und Ägypter zur Durchführung von Berechnungen?  

    **Antwort:**  
    Die Babylonier und Ägypter verwendeten den Abakus und andere mechanische Hilfsmittel, um Berechnungen durchzuführen.  

    ---

    **Frage:**   
    Welche Rechenoperationen konnten die mechanischen Rechenmaschinen von Blaise Pascal und Gottfried Wilhelm Leibniz ausführen?  

    **Antwort:**  
    Die Rechenmaschine von Blaise Pascal konnte Additionen und Subtraktionen durchführen, während die Maschine von Gottfried Wilhelm Leibniz zusätzlich Multiplikationen und Divisionen beherrschte.  

    ---

    **Frage 3:**  
    Warum wird die „Analytical Engine“ von Charles Babbage als Vorläufer moderner Computer betrachtet?  

    **Antwort:**  
    Die „Analytical Engine“ gilt als Vorläufer moderner Computer, da sie nicht nur rechnen, sondern auch programmiert werden konnte.
    """

    expected_qna_pairs = [
        {
            "question": "Welche mechanischen Hilfsmittel nutzten die Babylonier und Ägypter zur Durchführung von Berechnungen?",
            "answer": "Die Babylonier und Ägypter verwendeten den Abakus und andere mechanische Hilfsmittel, um Berechnungen durchzuführen."
        },
        {
            "question": "Welche Rechenoperationen konnten die mechanischen Rechenmaschinen von Blaise Pascal und Gottfried Wilhelm Leibniz ausführen?",
            "answer": "Die Rechenmaschine von Blaise Pascal konnte Additionen und Subtraktionen durchführen, während die Maschine von Gottfried Wilhelm Leibniz zusätzlich Multiplikationen und Divisionen beherrschte."
        },
        {
            "question": "Warum wird die „Analytical Engine“ von Charles Babbage als Vorläufer moderner Computer betrachtet?",
            "answer": "Die „Analytical Engine“ gilt als Vorläufer moderner Computer, da sie nicht nur rechnen, sondern auch programmiert werden konnte."
        }
    ]

    qna_pairs = generator.extract_qna_pairs(response_text)

    # Ausgabe für Debugging
    for idx, pair in enumerate(qna_pairs, 1):
        print(f"Frage {idx}: {pair['question']}")
        print(f"Antwort: {pair['answer']}")
        print("-" * 50)

    # Prüfe, ob genau 3 Paare extrahiert wurden
    assert len(qna_pairs) == 3, f"❌ Es sollten genau 3 Frage-Antwort-Paare erkannt werden, aber es wurden {len(qna_pairs)} gefunden!"

    # Vergleiche jedes Paar mit der erwarteten Ausgabe
    for idx, (actual, expected) in enumerate(zip(qna_pairs, expected_qna_pairs), 1):
        assert actual["question"] == expected["question"], f"❌ Frage {idx} nicht korrekt: {actual['question']}"
        assert actual["answer"] == expected["answer"], f"❌ Antwort {idx} nicht korrekt: {actual['answer']}"

    print("✅ Neuer Test erfolgreich!")

if __name__ == "__main__":
    test_qna_extraction_new()
