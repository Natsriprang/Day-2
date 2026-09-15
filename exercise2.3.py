import streamlit as st
import os
import glob
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# Page title
# -----------------------------

st.title("Exercise 2.3 - Implementing RAG Manually")

st.write(
    "This uses the chunks saved by Exercise 2.1."
)


# -----------------------------
# Session state
# -----------------------------

if "selected_document" not in st.session_state:
    st.session_state.selected_document = None

if "answer" not in st.session_state:
    st.session_state.answer = None

if "sources" not in st.session_state:
    st.session_state.sources = []


# -----------------------------
# Find document folders
# -----------------------------

document_folders = [
    folder
    for folder in glob.glob("chunks/*")
    if os.path.isdir(folder)
]


# -----------------------------
# No documents
# -----------------------------

if len(document_folders) == 0:

    st.warning(
        "No documents found. Please go to Exercise 2.1 and upload a PDF first."
    )


# -----------------------------
# Documents found
# -----------------------------

else:

    # Get document names
    document_names = [
        os.path.basename(folder)
        for folder in document_folders
    ]


    # -----------------------------
    # Select document
    # -----------------------------

    if (
        st.session_state.selected_document
        not in document_names
    ):
        st.session_state.selected_document = document_names[0]


    selected_document = st.selectbox(
        "Select a document",
        options=document_names,
        index=document_names.index(
            st.session_state.selected_document
        )
    )


    # Save selected document
    st.session_state.selected_document = selected_document


    # -----------------------------
    # Find chunks
    # -----------------------------

    selected_folder = os.path.join(
        "chunks",
        selected_document
    )


    chunk_files = sorted(
        glob.glob(
            os.path.join(
                selected_folder,
                "chunk_*.txt"
            )
        ),
        key=lambda path: int(
            os.path.basename(path)
            .split("_")[1]
            .split(".")[0]
        )
    )


    # -----------------------------
    # Load chunks
    # -----------------------------

    chunks = []

    for path in chunk_files:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            chunks.append(f.read())


    st.write(
        f"Loaded {len(chunks)} chunks from **{selected_document}**."
    )


    # -----------------------------
    # Question
    # -----------------------------

    question = st.text_input(
        "Ask a question about the document"
    )


    # -----------------------------
    # Ask button
    # -----------------------------

    if st.button("Ask"):

        if question.strip() == "":

            st.warning(
                "Please enter a question before submitting."
            )

        else:

            # -----------------------------
            # OpenAI client
            # -----------------------------

            client = OpenAI()


            # -----------------------------
            # Create embedding for question
            # -----------------------------

            question_embedding = client.embeddings.create(
                model="text-embedding-3-large",
                input=question
            ).data[0].embedding


            # -----------------------------
            # Create embeddings for chunks
            # -----------------------------

            chunk_embeddings = []

            for chunk in chunks:

                embedding = client.embeddings.create(
                    model="text-embedding-3-large",
                    input=chunk
                ).data[0].embedding

                chunk_embeddings.append(embedding)


            # -----------------------------
            # Calculate cosine similarity
            # -----------------------------

            question_vector = np.array(
                question_embedding
            )

            similarities = []

            for embedding in chunk_embeddings:

                chunk_vector = np.array(
                    embedding
                )

                similarity = np.dot(
                    question_vector,
                    chunk_vector
                ) / (
                    np.linalg.norm(question_vector)
                    * np.linalg.norm(chunk_vector)
                )

                similarities.append(similarity)


            # -----------------------------
            # Get Top 3 most relevant chunks
            # -----------------------------

            top_n = min(3, len(chunks))

            top_indices = np.argsort(
                similarities
            )[-top_n:][::-1]


            # -----------------------------
            # Build context
            # -----------------------------

            context = ""

            for index in top_indices:

                context += (
                    f"\n\n"
                    f"--- Chunk {index + 1} "
                    f"(similarity: "
                    f"{similarities[index]:.4f}) ---\n"
                )

                context += chunks[index]


            # -----------------------------
            # Ask GPT
            # -----------------------------

            response = client.responses.create(

                model="gpt-4o",

                input=(
                    "Answer the question using the relevant "
                    "information from the document excerpts below.\n\n"

                    "The excerpts were retrieved from the document "
                    "based on their similarity to the question.\n\n"

                    "Use the information in the excerpts to answer "
                    "the question. The wording of the question does "
                    "not need to exactly match the wording in the "
                    "document.\n\n"

                    "If the answer is not contained in the provided "
                    "excerpts, say that the information was not found "
                    "in the provided document.\n\n"

                    f"Document: {selected_document}\n\n"

                    f"Document excerpts:\n"
                    f"{context}\n\n"

                    f"Question: {question}"
                )
            )


            # -----------------------------
            # Save answer
            # -----------------------------

            st.session_state.answer = (
                response.output_text
            )


            # -----------------------------
            # Save sources
            # -----------------------------

            st.session_state.sources = [

                (
                    index,
                    similarities[index],
                    chunks[index]
                )

                for index in top_indices
            ]


# -----------------------------
# Display answer
# -----------------------------

if st.session_state.answer is not None:

    st.subheader("Answer")

    st.write(
        st.session_state.answer
    )


    # -----------------------------
    # Display sources
    # -----------------------------

    st.subheader("Sources")

    for (
        index,
        similarity,
        chunk
    ) in st.session_state.sources:

        st.write(
            f"Chunk {index + 1} "
            f"(similarity: {similarity:.4f})"
        )

        with st.expander(
            f"View Chunk {index + 1}"
        ):

            st.write(chunk)