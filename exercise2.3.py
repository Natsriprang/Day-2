import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import numpy as np


load_dotenv()


st.title("Exercise 2.3 - Implementing RAG Manually")


st.write(
    "This uses the chunks saved by Exercise 2.1."
)


# --------------------------------------------------
# Session state
# --------------------------------------------------

if "answer" not in st.session_state:
    st.session_state.answer = None

if "sources" not in st.session_state:
    st.session_state.sources = []


# --------------------------------------------------
# Check if documents exist
# --------------------------------------------------

if (
    "documents" not in st.session_state
    or len(st.session_state.documents) == 0
):

    st.warning(
        "No documents found. "
        "Please go to Exercise 2.1 and upload a PDF first."
    )

else:

    # --------------------------------------------------
    # Select document
    # --------------------------------------------------

    document_names = list(
        st.session_state.documents.keys()
    )


    # Use the document selected in Exercise 2.1
    if (
        "selected_document" not in st.session_state
        or st.session_state.selected_document
        not in document_names
    ):

        st.session_state.selected_document = (
            document_names[0]
        )


    selected_document = st.selectbox(
        "Select which document to ask about",
        options=document_names,
        index=document_names.index(
            st.session_state.selected_document
        ),
        key="rag_document_selector"
    )


    # Remember selected document
    st.session_state.selected_document = (
        selected_document
    )


    # Get ONLY the chunks belonging to this document
    chunks = (
        st.session_state
        .documents[selected_document]["chunks"]
    )


    st.write(
        f"Using document: **{selected_document}**"
    )


    # --------------------------------------------------
    # Ask question
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

            client = OpenAI()


            # --------------------------------------------------
            # 1. Create embedding for question
            # --------------------------------------------------

            question_embedding = np.array(
                client.embeddings.create(
                    model="text-embedding-3-large",
                    input=question,
                ).data[0].embedding
            )


            # --------------------------------------------------
            # 2. Create embeddings for this document's chunks
            # --------------------------------------------------

            similarities = []


            for chunk in chunks:

                chunk_embedding = np.array(
                    client.embeddings.create(
                        model="text-embedding-3-large",
                        input=chunk,
                    ).data[0].embedding
                )


                similarity = (
                    np.dot(
                        question_embedding,
                        chunk_embedding
                    )
                    /
                    (
                        np.linalg.norm(
                            question_embedding
                        )
                        *
                        np.linalg.norm(
                            chunk_embedding
                        )
                    )
                )


                similarities.append(similarity)


            # --------------------------------------------------
            # 3. Find top 3 relevant chunks
            # --------------------------------------------------

            top_indices = np.argsort(
                similarities
            )[-3:][::-1]


            # --------------------------------------------------
            # 4. Create context
            # --------------------------------------------------

            context = ""


            for index in top_indices:

                context += (
                    f"\n\n--- Chunk {index + 1} "
                    f"(similarity: "
                    f"{similarities[index]:.4f}) ---\n"
                )

                context += chunks[index]


            # --------------------------------------------------
            # 5. Ask the model
            # --------------------------------------------------

            response = client.responses.create(
                model="gpt-4o",
                input=(
                    "Answer the question using the relevant "
                    "information from the document excerpts below.\n\n"

                    "The question may use different wording "
                    "from the document. Use relevant information "
                    "from the excerpts to answer the question "
                    "even if the exact words are not present.\n\n"

                    "Only say that the information was not found "
                    "if the document excerpts genuinely do not "
                    "contain information that can answer the question.\n\n"

                    "After answering, briefly explain what "
                    "information from the document you used. "
                    "Include the relevant chunk number as the source.\n\n"

                    f"Document: {selected_document}\n\n"

                    f"Document excerpts:\n{context}\n\n"

                    f"Question: {question}"
                ),
            )


            # --------------------------------------------------
            # 6. Save answer
            # --------------------------------------------------

            st.session_state.answer = (
                response.output_text
            )


            # --------------------------------------------------
            # 7. Save sources
            # --------------------------------------------------

            st.session_state.sources = [
                (
                    index,
                    similarities[index],
                    chunks[index]
                )
                for index in top_indices
            ]

      # Display answer
  
    if st.session_state.answer is not None:

        st.subheader("Answer")

        st.write(
            st.session_state.answer
        )


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