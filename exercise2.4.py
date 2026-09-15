import streamlit as st
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from openai import OpenAI
from dotenv import load_dotenv
import os
import glob


load_dotenv()


# ==================================================
# 1. Page title
# ==================================================

st.title("Building a Positive Law Firm")

st.write(
    "This document provides the content of Building a Positive Law Firm in chunks."
)


# ==================================================
# 2. Find document folders
# ==================================================

document_folders = [
    folder
    for folder in glob.glob("chunks/*")
    if os.path.isdir(folder)
]


# ==================================================
# 3. Check if documents exist
# ==================================================

if len(document_folders) == 0:

    st.warning(
        "No documents found. "
        "Please go to Exercise 2.1 and upload a PDF first."
    )


else:

    # ==================================================
    # 4. Get document names
    # ==================================================

    document_names = [
        os.path.basename(folder)
        for folder in document_folders
    ]


    # ==================================================
    # 5. Select document
    # ==================================================

    selected_document = st.selectbox(
        "Select a document",
        document_names
    )


    # ==================================================
    # 6. Find chunks for selected document
    # ==================================================

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


    # ==================================================
    # 7. Load chunks
    # ==================================================

    chunks = []

    for path in chunk_files:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            chunks.append(
                f.read()
            )


    st.write(
        f"Loaded {len(chunks)} chunk(s) "
        f"from **{selected_document}**."
    )


    # ==================================================
    # 8. Create Chroma client
    # ==================================================

    chroma_client = chromadb.PersistentClient(
        path="./chroma_db"
    )


    # ==================================================
    # 9. Create OpenAI embedding function
    # ==================================================

    openai_ef = OpenAIEmbeddingFunction(
        api_key_env_var="OPENAI_API_KEY",
        model_name="text-embedding-3-large"
    )


    # ==================================================
    # 10. Create a collection for this document
    # ==================================================

    collection_name = (
        "document_"
        + selected_document
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        embedding_function=openai_ef
    )


    # ==================================================
    # 11. Add chunks to Chroma
    # ==================================================

    collection.upsert(

        ids=[
            f"{selected_document}_chunk_{i + 1}"
            for i in range(len(chunks))
        ],

        documents=chunks
    )


    # ==================================================
    # 12. Ask a question
    # ==================================================

    question = st.text_input(
        "Ask a question about the document."
    )


    if st.button("Ask"):

        if question.strip() == "":

            st.warning(
                "Please enter a question before submitting."
            )


        else:

            # ==================================================
            # 13. Query Chroma for Top 3
            # ==================================================

            results = collection.query(

                query_texts=[
                    question
                ],

                n_results=min(
                    3,
                    len(chunks)
                )
            )


            # ==================================================
            # 14. Get retrieved chunks
            # ==================================================

            retrieved_chunks = (
                results["documents"][0]
            )

            retrieved_ids = (
                results["ids"][0]
            )

            retrieved_distances = (
                results["distances"][0]
            )


            # ==================================================
            # 15. Create context
            # ==================================================

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


            # ==================================================
            # 16. Ask OpenAI
            # ==================================================

            client = OpenAI()


            response = client.responses.create(

                model="gpt-4o",

                input=(

                    "Answer the question using the relevant "
                    "information from the document excerpts below.\n\n"

                    "The excerpts were retrieved from the document "
                    "using a vector database. Use the information "
                    "in the excerpts to answer the question.\n\n"

                    "Use the information in the excerpts to answer "
                    "the question even if the wording of the "
                    "question is different from the wording in "
                    "the document.\n\n"

                    "If the answer is not contained in the "
                    "retrieved excerpts, say that the information "
                    "was not found in the provided document.\n\n"

                    f"Document: {selected_document}\n\n"

                    f"Document excerpts:\n"
                    f"{context}\n\n"

                    f"Question: {question}"
                )
            )


            # ==================================================
            # 17. Display answer
            # ==================================================

            st.subheader(
                "Answer"
            )

            st.write(
                response.output_text
            )


            # ==================================================
            # 18. Display retrieved sources
            # ==================================================

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

                    st.write(
                        chunk
                    )