import streamlit as st
from pypdf import PdfReader
import os
import re


st.title("Exercise 2.1")


# --------------------------------------------------
# Session state
# --------------------------------------------------

if "documents" not in st.session_state:
    st.session_state.documents = {}

if "selected_document" not in st.session_state:
    st.session_state.selected_document = None


# --------------------------------------------------
# Upload PDF
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Choose a file",
    type="pdf"
)


chunk_by = st.selectbox(
    "Chunk by type",
    options=[
        "Number of pages",
        "Number of words",
        "Number of paragraphs"
    ]
)


if chunk_by == "Number of pages":

    unit_size = st.slider(
        "Pages per chunk",
        min_value=1,
        max_value=20,
        value=1
    )

elif chunk_by == "Number of words":

    unit_size = st.slider(
        "Words per chunk",
        min_value=50,
        max_value=1000,
        value=300,
        step=50
    )

else:

    unit_size = st.slider(
        "Paragraphs per chunk",
        min_value=1,
        max_value=20,
        value=3
    )


# --------------------------------------------------
# Chunking functions
# --------------------------------------------------

def chunk_by_pages(pages_text, pages_per_chunk):

    chunks = []

    for i in range(
        0,
        len(pages_text),
        pages_per_chunk
    ):

        chunk = "\n\n".join(
            pages_text[i:i + pages_per_chunk]
        )

        chunks.append(chunk)

    return chunks


def chunk_by_words(full_text, words_per_chunk):

    words = full_text.split()

    chunks = []

    for i in range(
        0,
        len(words),
        words_per_chunk
    ):

        chunk = " ".join(
            words[i:i + words_per_chunk]
        )

        chunks.append(chunk)

    return chunks


def chunk_by_paragraphs(
    full_text,
    paragraphs_per_chunk
):

    paragraphs = [
        p.strip()
        for p in full_text.split("\n\n")
        if p.strip() != ""
    ]

    chunks = []

    for i in range(
        0,
        len(paragraphs),
        paragraphs_per_chunk
    ):

        chunk = "\n\n".join(
            paragraphs[
                i:i + paragraphs_per_chunk
            ]
        )

        chunks.append(chunk)

    return chunks


# --------------------------------------------------
# Submit
# --------------------------------------------------

if st.button("Submit"):

    if uploaded_file is None:

        st.warning(
            "Please upload a PDF file before submitting."
        )

    else:

        # Read PDF
        reader = PdfReader(uploaded_file)

        pages_text = [
            page.extract_text() or ""
            for page in reader.pages
        ]

        full_text = "\n\n".join(pages_text)


        # Create chunks
        if chunk_by == "Number of pages":

            chunks = chunk_by_pages(
                pages_text,
                unit_size
            )

        elif chunk_by == "Number of words":

            chunks = chunk_by_words(
                full_text,
                unit_size
            )

        else:

            chunks = chunk_by_paragraphs(
                full_text,
                unit_size
            )


        # --------------------------------------------------
        # Save document information in session state
        # --------------------------------------------------

        filename = uploaded_file.name

        st.session_state.documents[filename] = {
            "chunks": chunks,
            "chunk_by": chunk_by,
            "unit_size": unit_size
        }


        # Automatically select the newly uploaded document
        st.session_state.selected_document = filename


        # --------------------------------------------------
        # Save chunks to separate folder for this document
        # --------------------------------------------------

        # Make a safe folder name
        safe_filename = re.sub(
            r"[^a-zA-Z0-9ก-๙._-]",
            "_",
            filename
        )

        document_folder = os.path.join(
            "chunks",
            safe_filename
        )

        os.makedirs(
            document_folder,
            exist_ok=True
        )


        # Save each chunk
        for i, chunk in enumerate(
            chunks,
            start=1
        ):

            with open(
                os.path.join(
                    document_folder,
                    f"chunk_{i}.txt"
                ),
                "w",
                encoding="utf-8"
            ) as f:

                f.write(chunk)


        st.success(
            f"Saved {filename} "
            f"with {len(chunks)} chunk(s)."
        )


# --------------------------------------------------
# Select saved document
# --------------------------------------------------

if len(st.session_state.documents) > 0:

    st.divider()

    st.subheader("Saved documents")


    document_names = list(
        st.session_state.documents.keys()
    )


    # Make sure selected document still exists
    if (
        st.session_state.selected_document
        not in document_names
    ):

        st.session_state.selected_document = (
            document_names[0]
        )


    selected_document = st.selectbox(
        "Select which document to view",
        options=document_names,
        index=document_names.index(
            st.session_state.selected_document
        ),
        key="document_selector"
    )


    # Remember the selected document
    st.session_state.selected_document = (
        selected_document
    )


    # Get chunks belonging to this document
    selected_chunks = (
        st.session_state
        .documents[selected_document]["chunks"]
    )


    # --------------------------------------------------
    # Select chunk
    # --------------------------------------------------

    chunk_num = st.selectbox(
        "Select which chunk to view",
        options=list(
            range(
                1,
                len(selected_chunks) + 1
            )
        ),
        key="chunk_selector"
    )


    selected_chunk = selected_chunks[
        chunk_num - 1
    ]


    # --------------------------------------------------
    # Display chunk
    # --------------------------------------------------

    st.subheader(
        f"{selected_document} — Chunk {chunk_num}"
    )

    st.write(selected_chunk)


    # --------------------------------------------------
    # Download selected chunk
    # --------------------------------------------------

    st.download_button(
        label=f"Download chunk_{chunk_num}.txt",
        data=selected_chunk,
        file_name=(
            f"{selected_document}"
            f"_chunk_{chunk_num}.txt"
        ),
        mime="text/plain",
        key=(
            f"download_selected_"
            f"{selected_document}_"
            f"{chunk_num}"
        )
    )


    # --------------------------------------------------
    # Download all chunks
    # --------------------------------------------------

    st.divider()

    st.subheader("Download all chunks")


    for i, chunk_text in enumerate(
        selected_chunks,
        start=1
    ):

        st.download_button(
            label=f"Save chunk_{i}.txt",
            data=chunk_text,
            file_name=(
                f"{selected_document}"
                f"_chunk_{i}.txt"
            ),
            mime="text/plain",
            key=(
                f"download_all_"
                f"{selected_document}_"
                f"{i}"
            )
        )