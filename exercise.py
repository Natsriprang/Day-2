import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()


st.title("MOOD CHECK! :)")
user_mood_input=st.text_input("How is it going?")
if st.button("Share!"):
    if user_mood_input.strip() == "":
        st.warning("Please share your emotion.")
    else:
        client = OpenAI()

        response = client.responses.create(
            model="gpt-4o",
            input=f"User shares that their feeling is '{user_mood_input}'."
                  f"Response will depend on the feeling, be particularly kind and compassionate if feeling is negative"
                  f"write a short answer in english"
    )
        st.write(response.output_text)
