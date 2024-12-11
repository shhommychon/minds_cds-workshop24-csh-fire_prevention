import streamlit as st
import os
import tempfile
from pathlib import Path
from audio_utils import convert_to_mp3, _supported_extensions
from api_utils import process_whisper, setup_openai_client

def whisper_view():
    st.title("Whisper (v1)")

    uploaded_file = st.file_uploader(
        "Upload audio file",
        type=_supported_extensions
    )

    if uploaded_file:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            converted_path = convert_to_mp3(tmp_file_path)
            st.session_state.processed_audio = converted_path
            st.success("Audio file processed successfully")

        except Exception as e:
            st.error(f"Error processing audio file: {str(e)}")
            st.session_state.processed_audio = None
        finally:
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Process with Whisper", disabled=not st.session_state.processed_audio):
            mode = st.session_state.whisper_mode
            try:
                result = process_whisper(st.session_state.processed_audio, mode)
                st.session_state.whisper_result = result
            except Exception as e:
                st.error(f"Error processing with Whisper: {str(e)}")

    with col2:
        st.session_state.whisper_mode = st.selectbox(
            "Processing mode",
            ["transcription", "timestamp"],
            key="whisper_mode_select"
        )

    if st.session_state.whisper_result:
        st.text_area("Whisper Results", st.session_state.whisper_result, height=300)

def chatgpt_view():
    st.title("ChatGPT (4o)")

    # Initialize conversation history in session state
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'chat_display' not in st.session_state:
        st.session_state.chat_display = ""

    # System prompt input
    system_prompt = st.text_area(
        "System Prompt",
        height=100,
        key="system_prompt"
    )

    # Chat display area with theme-aware styling
    st.markdown("""
        <style>
            .chat-area {
                height: 400px;
                overflow-y: auto;
                overflow-x: hidden;
                white-space: pre-wrap;
                word-wrap: break-word;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid rgba(128, 128, 128, 0.2);
                background-color: transparent;
            }
        </style>
    """, unsafe_allow_html=True)

    # Display the chat content
    st.markdown('<div class="chat-area">' + st.session_state.chat_display + '</div>', 
                unsafe_allow_html=True)

    # Message input form
    with st.form(key='message_form'):
        user_input = st.text_input("Enter your message:", key="user_input")
        submit_button = st.form_submit_button("Send")

        if submit_button and user_input:
            # Update conversation history
            if not st.session_state.conversation_history:
                # First message: include system prompt
                st.session_state.conversation_history = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
            else:
                st.session_state.conversation_history.append({"role": "user", "content": user_input})

            try:
                # Get response from API
                client = setup_openai_client()
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=st.session_state.conversation_history
                )

                assistant_response = response.choices[0].message.content

                # Update conversation history with assistant's response
                st.session_state.conversation_history.append(
                    {"role": "assistant", "content": assistant_response}
                )

                # Update display text
                st.session_state.chat_display += f"\nYou: {user_input}\nAssistant: {assistant_response}\n"

                st.experimental_rerun()

            except Exception as e:
                st.error(f"Error: {str(e)}")