import streamlit as st
import tempfile
import os
import json
import csv
import fitz  # PyMuPDF für PDF-Verarbeitung
from pdf_parser.pdf_parser import PDFParser
from nlp.qna_generator import QnAGenerator

def save_flashcards(flashcards, format="csv", filename="karteikarten"):
    """Speichert die Karteikarten als CSV oder JSON."""
    if format == "csv":
        with open(f"{filename}.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter="\t")  # Tab für Anki-Import
            writer.writerow(["Frage", "Antwort"])
            for card in flashcards:
                writer.writerow([card["question"], card["answer"]])
        return f"{filename}.csv"

    elif format == "json":
        with open(f"{filename}.json", "w", encoding="utf-8") as file:
            json.dump(flashcards, file, indent=4, ensure_ascii=False)
        return f"{filename}.json"

def main():
    st.title("📄 PDF zu Karteikarten Generator")

    uploaded_file = st.file_uploader("Lade eine PDF hoch", type=["pdf"])

    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.read())
            pdf_path = temp_file.name

        try:
            with fitz.open(pdf_path) as doc:  # PDF wird automatisch geschlossen
                num_pages = len(doc)
                st.success(f"PDF erfolgreich geladen. Seitenanzahl: {num_pages}")

                start_page = st.number_input("Startseite", min_value=1, max_value=num_pages, value=1)
                end_page = st.number_input("Endseite", min_value=start_page, max_value=num_pages, value=num_pages)

                if st.button("📜 Text aus PDF extrahieren"):
                    parser = PDFParser(pdf_path)
                    extracted_text = parser.extract_text(start_page=start_page, end_page=end_page)
                    if extracted_text:
                        chunks = parser.chunk_text(min_tokens=200, max_tokens=1000)
                    else:
                        chunks = []
                    
                    st.session_state["chunks"] = chunks
                    st.session_state["edited_chunks"] = chunks.copy()
                    st.session_state["chunk_selection"] = [True] * len(chunks)
                    st.success(f"{len(chunks)} Chunks extrahiert!")

        finally:
            os.remove(pdf_path)  # Datei wird sicher gelöscht

    if "chunks" in st.session_state:
        def reset_chunks():
            st.session_state["edited_chunks"] = st.session_state["chunks"].copy()  # Zurücksetzen der Chunks auf den Originaltext
        
        st.markdown('<div style="margin-bottom: 10px;"></div>', unsafe_allow_html=True)
        st.subheader("📌 Bearbeite & wähle Chunks aus:")
        st.markdown('<div style="margin-bottom: 10px;"></div>', unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns([1, 1, 1])

        with col_a:
            if st.button("Alle auswählen"):
                st.session_state["chunk_selection"] = [True] * len(st.session_state["chunks"])

        with col_b:
            if st.button("Auswahl aufheben"):
                st.session_state["chunk_selection"] = [False] * len(st.session_state["chunks"])

        with col_c:
            if st.button("Chunks zurücksetzen"):
                reset_chunks()
        
        st.markdown('<hr style="margin-top: 0px; margin-bottom: 20px;">', unsafe_allow_html=True)

        for i, chunk in enumerate(st.session_state["chunks"]):
            col1, col2, col3 = st.columns([0.5, 12, 1])

            with col1:
                st.session_state["chunk_selection"][i] = st.checkbox(
                    "\u200b", key=f'check_{i}', value=st.session_state["chunk_selection"][i], label_visibility="collapsed"
                )

            with col2:
                st.session_state["edited_chunks"][i] = st.text_area(
                    f"Chunk {i+1}", value=st.session_state["edited_chunks"][i], height=150
                )

            with col3:
                st.markdown("<div style='height: 140px;'></div>", unsafe_allow_html=True)
                if st.button("🔄", key=f'reset_{i}'):
                    st.session_state["edited_chunks"][i] = st.session_state["chunks"][i]
            
            st.markdown("---")

        
        # Zähle ausgewählte Chunks
        selected_count = sum(st.session_state["chunk_selection"])
        total_chunks = len(st.session_state["chunks"])

        # Anzeige unter den Chunks
        st.markdown(f"**✅ {selected_count} von {total_chunks} Chunks ausgewählt**")
        
        api_key = st.text_input("🔑 OpenAI API-Key eingeben", type="password")
        num_questions = st.slider("Wie viele Fragen pro Chunk?", 1, 5, 3)

        if st.button("🎯 Karteikarten generieren"):
            if not api_key:
                st.warning("⚠️ API-Key eingeben!")
            else:
                selected_chunks = [
                    st.session_state["edited_chunks"][i]
                    for i, selected in enumerate(st.session_state["chunk_selection"])
                    if selected
                ]
                
                if not selected_chunks:
                    st.warning("⚠️ Bitte mindestens einen Chunk auswählen!")
                else:
                    qna_generator = QnAGenerator(api_key)
                    flashcards = []
                    for chunk in selected_chunks:
                        flashcards.extend(qna_generator.generate_qna_pairs(chunk, num_questions))

                    st.session_state["flashcards"] = flashcards
                    st.success(f"{len(flashcards)} Karteikarten generiert!")

    if "flashcards" in st.session_state:
        st.subheader("📋 Generierte Karteikarten")
        for i, card in enumerate(st.session_state["flashcards"]):
            st.write(f"**Frage {i+1}:** {card['question']}")
            st.write(f"**Antwort:** {card['answer']}")
            st.markdown("---")

        st.subheader("💾 Speichern als")
        format_option = st.selectbox("Format wählen", ["csv", "json"])

        if st.button("📥 Datei herunterladen"):
            file_path = save_flashcards(st.session_state["flashcards"], format_option)
            with open(file_path, "rb") as f:
                st.download_button(
                    label="Download starten",
                    data=f,
                    file_name=os.path.basename(file_path),
                    mime="text/csv" if format_option == "csv" else "application/json"
                )

if __name__ == "__main__":
    main()
