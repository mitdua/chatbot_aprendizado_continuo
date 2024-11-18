import streamlit as st
from datetime import datetime
from nodes import chatbot


st.set_page_config(
    page_title="ChatBot",
    page_icon="🤖",
    layout="wide",   
)


# Title of the application
st.title("Chatbot Aprendizado Contínuo")


# Initialize the session state for storing messages if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display each message in the session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input field for entering messages
if user_input := st.chat_input("Digite sua mensagem"):
    # Save the user's message to the session state
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get the chatbot's response (modify this logic to use a real model)
    response = chatbot(messages=st.session_state.messages)
    # Save the chatbot's response to the session state
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
