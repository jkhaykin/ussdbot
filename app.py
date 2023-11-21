from dotenv import load_dotenv
load_dotenv()

import os
import time
import re

import streamlit as st
from openai import OpenAI

client = OpenAI()

# has weird source symbols in responses, so removing those
def remove_between(text, char1, char2):
    pattern = f"{re.escape(char1)}.*?{re.escape(char2)}"
    return re.sub(pattern, '', text, flags=re.DOTALL)

def generate_gpt4_response(question):
    thread = client.beta.threads.create()
    
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=question,
        file_ids=["file-E8N6jBRotQ3a8gcIlCuMRQoz"]
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id="asst_Z40oL1LYInABJlSoE8FbOn50"
    )

    while True:
        run_retrieve = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

        if run_retrieve.status == 'completed':
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
            )

            response = messages.data[0].content[0].text.value
            break
        elif run_retrieve.status in ['failed', 'cancelled']:
            response = run_retrieve.status
            break
        else:
            print("Run is still in progress...")

        time.sleep(7)  # Wait for 4 seconds before checking again
        
    return remove_between(response, "【", "】")


# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Ask me a question about USSD's material"}]

avatar_image = "./USSDLOGO.svg"

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=avatar_image if message["role"] == "assistant" else ""):
        st.write(message["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant", avatar=avatar_image if message["role"] == "assistant" else ""):
        with st.spinner("Thinking..."):
            response = generate_gpt4_response(prompt)
            placeholder = st.empty()
            full_response = ""
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)

    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)