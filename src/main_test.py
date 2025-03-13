import logging
from nlp.qna_generator import QnAGenerator

# Logging aktivieren
logging.basicConfig(level=logging.DEBUG)

def test_qna_extraction_burn_down():
    """
    Testet die Extraktion mit einem neuen Beispieltext zu Burn Down Charts.
    """
    generator = QnAGenerator(api_type="manual")

    response_text = """
    **Frage 1:**
    
    *   **Frage:** Was ist das charakteristische Merkmal eines Burn Down Charts und was wird idealerweise am Ende des Berichtszeitraums erreicht?
    *   **Antwort:** Das charakteristische Merkmal eines Burn Down Charts ist der angestrebte Kurvenverlauf von links oben nach rechts unten. Im Idealfall wird am Ende des Berichtszeitraums die Null-Linie erreicht, was bedeutet, dass alle offenen Aufgaben "verbrannt" (abgearbeitet) wurden.

    ---

    **Frage 2:**
    
    *   **Frage:** Welche Informationen werden typischerweise auf der X- und Y-Achse eines Burn Down Charts dargestellt und welche Beispiele werden im Text genannt?
    *   **Antwort:** Die X-Achse (horizontal) stellt den zeitlichen Verlauf dar (z.B. Tage, Wochen, Sprints). Die Y-Achse (vertikal) stellt die Einheit bzw. Kennzahl dar, deren Verlauf über die Zeit veranschaulicht werden soll. Typische Beispiele für die Y-Achse sind die Anzahl der offenen Aufgaben oder von verbrauchten Ressourcen wie Geld oder Zeit.

    ---

    **Frage 3:**
    
    *   **Frage:** Was stellt die Ideallinie in einem Burn Down Chart dar und wie hilft sie bei der Projektsteuerung?
    *   **Antwort:** Die Ideallinie veranschaulicht den Idealverlauf der Messpunkte im Burn Down Chart. Durch den Vergleich des tatsächlichen Verlaufs mit der Ideallinie kann man zu jedem Zeitpunkt erkennen, ob sich das Projekt wie geplant entwickelt oder ob es schneller oder langsamer als geplant vorankommt.

    ---

    **Frage 4:**
    
    *   **Frage:** In welchen Arten von Projekten werden Burn Down Charts häufig eingesetzt und warum sind sie dort nützlich?
    *   **Antwort:** Burn Down Charts werden insbesondere bei Softwareprojekten eingesetzt, die in Iterationen organisiert sind bzw. mit Scrum arbeiten. Sie sind dort nützlich, um die Aufgaben innerhalb einer Iteration zu planen und zu verfolgen, die Kommunikation zu unterstützen und einzelne Arbeitspakete zu steuern.
    """

    expected_qna_pairs = [
        {
            "question": "Was ist das charakteristische Merkmal eines Burn Down Charts und was wird idealerweise am Ende des Berichtszeitraums erreicht?",
            "answer": "Das charakteristische Merkmal eines Burn Down Charts ist der angestrebte Kurvenverlauf von links oben nach rechts unten. Im Idealfall wird am Ende des Berichtszeitraums die Null-Linie erreicht, was bedeutet, dass alle offenen Aufgaben \"verbrannt\" (abgearbeitet) wurden."
        },
        {
            "question": "Welche Informationen werden typischerweise auf der X- und Y-Achse eines Burn Down Charts dargestellt und welche Beispiele werden im Text genannt?",
            "answer": "Die X-Achse (horizontal) stellt den zeitlichen Verlauf dar (z.B. Tage, Wochen, Sprints). Die Y-Achse (vertikal) stellt die Einheit bzw. Kennzahl dar, deren Verlauf über die Zeit veranschaulicht werden soll. Typische Beispiele für die Y-Achse sind die Anzahl der offenen Aufgaben oder von verbrauchten Ressourcen wie Geld oder Zeit."
        },
        {
            "question": "Was stellt die Ideallinie in einem Burn Down Chart dar und wie hilft sie bei der Projektsteuerung?",
            "answer": "Die Ideallinie veranschaulicht den Idealverlauf der Messpunkte im Burn Down Chart. Durch den Vergleich des tatsächlichen Verlaufs mit der Ideallinie kann man zu jedem Zeitpunkt erkennen, ob sich das Projekt wie geplant entwickelt oder ob es schneller oder langsamer als geplant vorankommt."
        },
        {
            "question": "In welchen Arten von Projekten werden Burn Down Charts häufig eingesetzt und warum sind sie dort nützlich?",
            "answer": "Burn Down Charts werden insbesondere bei Softwareprojekten eingesetzt, die in Iterationen organisiert sind bzw. mit Scrum arbeiten. Sie sind dort nützlich, um die Aufgaben innerhalb einer Iteration zu planen und zu verfolgen, die Kommunikation zu unterstützen und einzelne Arbeitspakete zu steuern."
        }
    ]

    qna_pairs = generator.extract_qna_pairs(response_text)

    # Ausgabe für Debugging
    for idx, pair in enumerate(qna_pairs, 1):
        print(f"Frage {idx}: {pair['question']}")
        print(f"Antwort: {pair['answer']}")
        print("-" * 50)

    # Prüfe, ob genau 4 Paare extrahiert wurden
    assert len(qna_pairs) == 4, f"❌ Es sollten genau 4 Frage-Antwort-Paare erkannt werden, aber es wurden {len(qna_pairs)} gefunden!"

    # Vergleiche jedes Paar mit der erwarteten Ausgabe
    for idx, (actual, expected) in enumerate(zip(qna_pairs, expected_qna_pairs), 1):
        assert actual["question"] == expected["question"], f"❌ Frage {idx} nicht korrekt: {actual['question']}"
        assert actual["answer"] == expected["answer"], f"❌ Antwort {idx} nicht korrekt: {actual['answer']}"

    print("✅ Neuer Test erfolgreich!")

if __name__ == "__main__":
    test_qna_extraction_burn_down()
