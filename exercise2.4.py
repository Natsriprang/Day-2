import streamlit as st
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from openai import OpenAI
from dotenv import load_dotenv
import os
import glob


load_dotenv()


st.title("Building a Positive Law Firm")


st.write("This document provides the content of Building a Positive Law Firm in chunks.")
# 1. Find the saved chunks

chunk_files = sorted(
    glob.glob("chunks/chunk_*.txt"),
    key=lambda path: int(
        os.path.basename(path)
        .split("_")[1]
        .split(".")[0]
    )
)


if len(chunk_files) == 0:

    st.warning(
        "No chunks found. "
        "Please make sure the chunks folder contains "
        "chunk_*.txt files."
    )


else:

    # --------------------------------------------------
    # 2. Load the chunks
    # --------------------------------------------------

    chunks = []

    for path in chunk_files:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            chunks.append(f.read())


    st.write(
        f"Loaded {len(chunks)} chunk(s)."
    )


    # --------------------------------------------------
    # 3. Create Chroma client
    # --------------------------------------------------

    chroma_client = chromadb.PersistentClient(
        path="./chroma_db"
    )


    # --------------------------------------------------
    # 4. Create OpenAI embedding function
    # --------------------------------------------------

    openai_ef = OpenAIEmbeddingFunction(
        api_key_env_var="OPENAI_API_KEY",
        model_name="text-embedding-3-large"
    )


    # --------------------------------------------------
    # 5. Create / get Chroma collection
    # --------------------------------------------------

    collection = chroma_client.get_or_create_collection(
        name="document_chunks",
        embedding_function=openai_ef
    )


    # --------------------------------------------------
    # 6. Add chunks to Chroma
    # --------------------------------------------------

    collection.upsert(
        ids=[
            f"chunk_{i + 1}"
            for i in range(len(chunks))
        ],
        documents=chunks
    )


    # --------------------------------------------------
    # 7. Ask a question
    # --------------------------------------------------

    question = st.text_input(
        "Ask a question about the document"
    )


    if st.button("Ask"):

        if question.strip() == "":

            st.warning(
                "Please enter a question before submitting."
            )

        else:

            # --------------------------------------------------
            # 8. Query Chroma for the 3 most relevant chunks
            # --------------------------------------------------

            results = collection.query(
                query_texts=[question],
                n_results=min(3, len(chunks))
            )
            # --------------------------------------------------
            # 9. Get retrieved documents
            # --------------------------------------------------
            retrieved_chunks = results["documents"][0]
            retrieved_ids = results["ids"][0]
            retrieved_distances = results["distances"][0]
            # --------------------------------------------------
            # 10. Create context for the AI
            # --------------------------------------------------
            context = ""
            for i, chunk in enumerate(
                retrieved_chunks
            ):
                context += (
                    f"\n\n--- "
                    f"{retrieved_ids[i]} "
                    f"(distance: "
                    f"{retrieved_distances[i]:.4f}) "
                    f"---\n"
                )
                context += chunk
            # --------------------------------------------------
            # 11. Ask OpenAI to answer using retrieved chunks
            # --------------------------------------------------
            client = OpenAI()


            response = client.responses.create(
                model="gpt-4o",
                input=(
                    "Answer the question using the relevant "
                    "information from the document excerpts below.\n\n"

                    "The excerpts were retrieved from the document "
                    "using a vector database. Use the information "
                    "in the excerpts to answer the question.\n\n"

                    "If the answer is not contained in the "
                    "retrieved excerpts, say that the information "
                    "was not found in the provided document.\n\n"

                    "After answering, briefly explain what "
                    "information from the document you used "
                    "and identify the relevant chunk number.\n\n"

                    f"Document excerpts:\n{context}\n\n"

                    f"Question: {question}"
                )
            )


            # --------------------------------------------------
            # 12. Display answer
            # --------------------------------------------------

            st.subheader("Answer")

            st.write(
                response.output_text
            )


            # --------------------------------------------------
            # 13. Display retrieved sources
            # --------------------------------------------------

            st.subheader(
                "Retrieved Sources"
            )


            for i, chunk in enumerate(
                retrieved_chunks
            ):

                st.write(
                    f"{retrieved_ids[i]} "
                    f"(distance: "
                    f"{retrieved_distances[i]:.4f})"
                )


                with st.expander(
                    f"View {retrieved_ids[i]}"
                ):

                    st.write(chunk)