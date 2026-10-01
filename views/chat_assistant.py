import streamlit as st

from src.groq_client import get_client, get_model_name

client = get_client()

SYSTEM_PROMPT = (
    "You are a friendly eyewear styling assistant for LensMatch-AI, an app that "
    "recommends glasses based on face shape. Help users with questions about "
    "face shapes, glasses styles, frame materials, and general eyewear advice. "
    "Keep answers concise and helpful."
)


def show():

    st.title("💬 Eyewear Style Assistant")

    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    # Display past messages
    for message in st.session_state["chat_messages"][1:]:

        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_input = st.chat_input(
        "Ask me about glasses, face shapes, or styling..."
    )

    if user_input:

        st.session_state["chat_messages"].append(
            {"role": "user", "content": user_input}
        )

        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                try:

                    response = client.chat.completions.create(
                        model=get_model_name(),
                        messages=st.session_state["chat_messages"],
                    )

                    reply = response.choices[0].message.content

                    st.write(reply)

                    st.session_state["chat_messages"].append(
                        {
                            "role": "assistant",
                            "content": reply
                        }
                    )

                except Exception as e:

                    st.error(f"Groq Error: {e}")