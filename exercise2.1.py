import streamlit as st
from pypdf import PdfReader
import os
import re


st.title("Exercise 2.1")


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
    ],
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


# -----------------------------
# Chunking functions
# -----------------------------

def chunk_by_pages(text_by_page, pages_per_chunk):

    chunks = []

    for i in range(
        0,
        len(text_by_page),
        pages_per_chunk
    ):

        chunk = "\n\n".join(
            text_by_page[
                i:i + pages_per_chunk
            ]
        )

        if chunk.strip():

            chunks.append(chunk)

    return chunks


def chunk_by_words(text, words_per_chunk):

    words = text.split()

    chunks = []

    for i in range(
        0,
        len(words),
        words_per_chunk
    ):

        chunk = " ".join(
            words[
                i:i + words_per_chunk
            ]
        )

        if chunk.strip():

            chunks.append(chunk)

    return chunks


def chunk_by_paragraphs(
    text,
    paragraphs_per_chunk
):

    paragraphs = [
        p.strip()
        for p in text.split("\n\n")
        if p.strip()
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

        if chunk.strip():

            chunks.append(chunk)

    return chunks


# -----------------------------
# Process PDF
# -----------------------------

if st.button("Submit"):

    if uploaded_file is None:

        st.warning(
            "Please upload a PDF first."
        )

    else:

        # -----------------------------
        # Read PDF
        # -----------------------------

        reader = PdfReader(
            uploaded_file
        )

        pages = []

        for page in reader.pages:

            text = (
                page.extract_text()
                or ""
            )

            pages.append(text)


        full_text = "\n\n".join(
            pages
        )


        # -----------------------------
        # Create chunks
        # -----------------------------

        if chunk_by == "Number of pages":

            chunks = chunk_by_pages(
                pages,
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


        # -----------------------------
        # Create document folder
        # -----------------------------

        # Get filename without .pdf
        document_name = os.path.splitext(
            uploaded_file.name
        )[0]


        # Make filename safe for folder name
        safe_document_name = re.sub(
            r"[^a-zA-Z0-9ก-๙._-]",
            "_",
            document_name
        )


        # Create folder:
        # chunks/document_name/
        document_folder = os.path.join(
            "chunks",
            safe_document_name
        )

        os.makedirs(
            document_folder,
            exist_ok=True
        )


        # -----------------------------
        # Remove old chunks
        # from THIS document only
        # -----------------------------

        old_chunks = [
            file
            for file in os.listdir(
                document_folder
            )
            if file.startswith("chunk_")
            and file.endswith(".txt")
        ]


        for file in old_chunks:

            os.remove(
                os.path.join(
                    document_folder,
                    file
                )
            )


        # -----------------------------
        # Save new chunks
        # -----------------------------

        for i, chunk in enumerate(
            chunks,
            start=1
        ):

            file_path = os.path.join(
                document_folder,
                f"chunk_{i}.txt"
            )


            with open(
                file_path,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(chunk)


        # -----------------------------
        # Save information in session
        # -----------------------------

        st.session_state[
            "selected_document"
        ] = safe_document_name

        st.session_state[
            "num_chunks"
        ] = len(chunks)


        st.success(
            f"Created {len(chunks)} chunks "
            f"for {uploaded_file.name}"
        )


# -----------------------------
# Show saved chunks
# -----------------------------

if (
    "num_chunks" in st.session_state
    and "selected_document" in st.session_state
):

    selected_document = (
        st.session_state[
            "selected_document"
        ]
    )

    num_chunks = (
        st.session_state[
            "num_chunks"
        ]
    )


    st.subheader(
        f"Saved Chunks: {selected_document}"
    )


    chunk_num = st.selectbox(
        "Select a chunk",
        options=list(
            range(
                1,
                num_chunks + 1
            )
        )
    )


    file_path = os.path.join(
        "chunks",
        selected_document,
        f"chunk_{chunk_num}.txt"
    )


    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:

        selected_chunk = f.read()


    st.write(
        selected_chunk
    )


    st.download_button(
        label="Download this chunk",
        data=selected_chunk,
        file_name=f"chunk_{chunk_num}.txt",
        mime="text/plain"
    )