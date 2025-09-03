import streamlit as st
import PyPDF2
from googletrans import Translator
import re
import tempfile
import nltk
from nltk.corpus import wordnet



# ------------------------ Functions ------------------------

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text



def get_translation_and_meaning(word):
    translator = Translator()

    try:
        # English meaning using NLTK WordNet
        synsets = wordnet.synsets(word)
        if synsets:
            eng_meaning = synsets[0].definition()
            # Get example sentences if available
            examples = []
            for syn in synsets[:2]:  # Get from first 2 synsets
                if syn.examples():
                    examples.extend(syn.examples()[:2])  # Get up to 2 examples per synset
            examples = list(set(examples))[:3]  # Remove duplicates and limit to 3
        else:
            eng_meaning = "No English meaning found."
            examples = []

        # Translate to Tamil
        result = translator.translate(word, src='en', dest='ta')
        tamil_translation = result.text

        return eng_meaning, tamil_translation, examples
    except Exception as e:
        return f"Error: {str(e)}", "Translation not available", []

def get_word_context(text, word, num_lines=3):
    """Get context around a word in the text (2-3 lines)"""
    lines = text.split('\n')
    context = []
    
    for i, line in enumerate(lines):
        if word.lower() in line.lower():
            # Get previous, current and next lines
            start = max(0, i-1)
            end = min(len(lines), i+2)
            context.extend(lines[start:end])
            if len(context) >= num_lines:
                break
    
    # If we found context, return it, otherwise return None
    if context:
        return '\n'.join(context[:num_lines])
    return None



# ------------------------ Streamlit UI ------------------------

st.set_page_config(page_title="Document Translator", layout="centered", page_icon="📘")
st.title("📄 InkLingua")
st.write("Upload a PDF to extract text and get word meanings in English and Tamil.")

uploaded_file = st.file_uploader("Choose a file", type=["pdf"])

if uploaded_file:
    with st.spinner("Processing your file..."):
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        if uploaded_file.type == "application/pdf":
            text = extract_text_from_pdf(tmp_path)
       

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📝 Extracted Text")
            st.text_area("Extracted Text", text if text else "No text could be extracted.", height=500)

        with col2:
            st.subheader("🔍 Look Up a Word")
            # Only include words with at least one letter (no numbers or empty strings)
            words = [w for w in set(re.findall(r'\b[a-zA-Z]+\b', text.lower())) if w]
            words.sort()
            selected_word = st.selectbox("Choose a word from text", words)
            typed_word = st.text_input("Or type a custom word")
            word_to_lookup = typed_word.strip() if typed_word else selected_word

            # Only show details if a valid word is selected
            if word_to_lookup:
                eng_meaning, tamil_translation, examples = get_translation_and_meaning(word_to_lookup)
                context = get_word_context(text, word_to_lookup)

                st.markdown("### 📘 Translation and Meaning")
                st.write(f"Word: {word_to_lookup}")
                st.write(f"English Meaning: {eng_meaning}")
                st.write(f"Tamil Translation: {tamil_translation}")

                if context:
                    st.write("Context in document (2-3 lines):")
                    st.write(context)

                if examples:
                    st.write("Example sentences:")
                    for example in examples:
                        st.write(f"- {example}")