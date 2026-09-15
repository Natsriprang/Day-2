import streamlit as st
from pypdf import PdfReader
import os

st.title("Exercise 2.1")

uploaded_file = st.file_uploader("Choose a file", type="pdf")

chunk_by = st.selectbox(
    "Chunk by type",
    options=["Number of pages", "Number of words", "Number of paragraphs"],
)

if chunk_by == "Number of pages":
    unit_size = st.slider("Pages per chunk", min_value=1, max_value=20, value=1)
elif chunk_by == "Number of words":
    unit_size = st.slider("Words per chunk", min_value=50, max_value=1000, value=300, step=50)
else:
    unit_size = st.slider("Paragraphs per chunk", min_value=1, max_value=20, value=3)


def chunk_by_pages(pages_text, pages_per_chunk):
    """Group a list of per-page text into chunks of N pages each."""
    chunks = []
    for i in range(0, len(pages_text), pages_per_chunk):
        chunk = "\n\n".join(pages_text[i:i + pages_per_chunk])
        chunks.append(chunk)
    return chunks


def chunk_by_words(full_text, words_per_chunk):
    """Split text into chunks of N words each."""
    words = full_text.split()
    chunks = []
    for i in range(0, len(words), words_per_chunk):
        chunk = " ".join(words[i:i + words_per_chunk])
        chunks.append(chunk)
    return chunks


def chunk_by_paragraphs(full_text, paragraphs_per_chunk):
    """Split text into chunks of N paragraphs each. Paragraphs are separated by blank lines."""
    paragraphs = [p.strip() for p in full_text.split("\n\n") if p.strip() != ""]
    chunks = []
    for i in range(0, len(paragraphs), paragraphs_per_chunk):
        chunk = "\n\n".join(paragraphs[i:i + paragraphs_per_chunk])
        chunks.append(chunk)
    return chunks


if st.button("Submit"):
    if uploaded_file is None:
        st.warning("Please upload a PDF file before submitting.")
    else:
        # 1. Read the PDF and extract text (kept per-page for page-based chunking)
        reader = PdfReader(uploaded_file)
        pages_text = [page.extract_text() or "" for page in reader.pages]
        full_text = "\n\n".join(pages_text)

        # 2. Chunk the document according to the selected method
        if chunk_by == "Number of pages":
            chunks = chunk_by_pages(pages_text, unit_size)
        elif chunk_by == "Number of words":
            chunks = chunk_by_words(full_text, unit_size)
        else:
            chunks = chunk_by_paragraphs(full_text, unit_size)

        # 3. Save each chunk to the project directory
        os.makedirs("chunks", exist_ok=True)
        for i, chunk in enumerate(chunks, start=1):
            with open(f"chunks/chunk_{i}.txt", "w", encoding="utf-8") as f:
                f.write(chunk)

        st.success(f"Saved {len(chunks)} chunk(s) to the 'chunks' folder, chunked by {chunk_by.lower()}.")

        # Store the number of chunks so the selector below survives the rerun
        st.session_state["num_chunks"] = len(chunks)

# 4 & 5. Let the user pick a chunk, read it back, and display it
if "num_chunks" in st.session_state:
    chunk_num = st.selectbox(
        "Select which chunk to view",
        options=list(range(1, st.session_state["num_chunks"] + 1)),
    )

    with open(f"chunks/chunk_{chunk_num}.txt", "r", encoding="utf-8") as f:
        selected_chunk = f.read()

    st.subheader(f"Chunk {chunk_num}")
    st.write(selected_chunk)