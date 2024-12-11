import streamlit as st
from views import whisper_view, chatgpt_view

def setup_page():
    st.set_page_config(page_title="Fire Safety Inspection Demo", layout="wide")

    if 'current_view' not in st.session_state:
        st.session_state.current_view = 'whisper'
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'processed_audio' not in st.session_state:
        st.session_state.processed_audio = None
    if 'whisper_result' not in st.session_state:
        st.session_state.whisper_result = None

def setup_sidebar():
    with st.sidebar:
        st.title("Demo Navigation")
        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "Whisper", 
                type="primary" if st.session_state.current_view == "whisper" else "secondary",
                use_container_width=True,
            ):
                st.session_state.current_view = "whisper"
                st.experimental_rerun()

        with col2:
            if st.button(
                "ChatGPT",
                type="primary" if st.session_state.current_view == "chatgpt" else "secondary",
                use_container_width=True,
            ):
                st.session_state.current_view = "chatgpt"
                st.experimental_rerun()

def main():
    setup_page()
    setup_sidebar()

    if st.session_state.current_view == "whisper":
        whisper_view()
    else:
        chatgpt_view()

if __name__ == "__main__":
    main()