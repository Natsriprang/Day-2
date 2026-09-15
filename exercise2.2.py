import streamlit as st
from openai import OpenAI
import numpy as np

st.title("Exercise 2.2 - Comparing Chunks")

# 1. Allow the user to copy and paste two different texts
text1 = st.text_area("Text 1", height=200)
text2 = st.text_area("Text 2", height=200)

if st.button("Compare"):
    if text1.strip() == "" or text2.strip() == "":
        st.warning("Please enter both texts before comparing.")
    else:
        client = OpenAI()

        # 2. Create an embedding for each chunk of text
        embedding_1 = client.embeddings.create(
            model="text-embedding-3-small",
            input=text1,
        ).data[0].embedding

        embedding_2 = client.embeddings.create(
            model="text-embedding-3-small",
            input=text2,
        ).data[0].embedding

        # 3. Compute and display the cosine similarity
        vec1 = np.array(embedding_1)
        vec2 = np.array(embedding_2)

        cosine_similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

        st.subheader("Cosine Similarity")
        st.write(f"{cosine_similarity:.4f}")