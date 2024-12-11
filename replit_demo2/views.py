import streamlit as st
import base64
import os
from api_utils import process_whisper, process_transcription
from pdf_utils import generate_pdf


def setup_page():
    """Initialize Streamlit page configuration"""
    st.set_page_config(page_title="소방시설 점검 음성 인식 데모", layout="centered")

    if 'audio_path' not in st.session_state:
        st.session_state.audio_path = None
    if 'pdf_path' not in st.session_state:
        st.session_state.pdf_path = None


def audio_recorder_view():
    """Render audio recorder component with direct file handling"""
    st.markdown("### 음성 녹음")

    # Create a container for the recorded audio file
    if 'audio_file' not in st.session_state:
        st.session_state.audio_file = None

    audio_recorder_html = """
    <div style="text-align: center;">
        <script>
            let mediaRecorder;
            let audioChunks = [];
            let recordButton;
            let statusDiv;

            document.addEventListener('DOMContentLoaded', function() {
                recordButton = document.getElementById('recordButton');
                statusDiv = document.getElementById('status');
            });

            async function toggleRecording() {
                if (!mediaRecorder || mediaRecorder.state === 'inactive') {
                    // Start recording
                    try {
                        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                        mediaRecorder = new MediaRecorder(stream);
                        audioChunks = [];

                        mediaRecorder.ondataavailable = (event) => {
                            audioChunks.push(event.data);
                        };

                        mediaRecorder.onstop = async () => {
                            const audioBlob = new Blob(audioChunks, { type: 'audio/mp3' });
                            const file = new File([audioBlob], 'recorded_audio.mp3', { type: 'audio/mp3' });

                            // Create a download link
                            const downloadLink = document.createElement('a');
                            downloadLink.href = URL.createObjectURL(file);
                            downloadLink.download = 'recorded_audio.mp3';
                            downloadLink.style.display = 'none';
                            document.body.appendChild(downloadLink);
                            downloadLink.click();
                            document.body.removeChild(downloadLink);

                            // Update status
                            statusDiv.innerText = '녹음 완료 - 파일이 다운로드되었습니다. 아래에서 파일을 선택해주세요.';
                        };

                        mediaRecorder.start();
                        recordButton.innerText = '녹음 중단';
                        statusDiv.innerText = '녹음 중...';
                    } catch (err) {
                        console.error('Error:', err);
                        statusDiv.innerText = '녹음 오류: ' + err.message;
                    }
                } else {
                    // Stop recording
                    mediaRecorder.stop();
                    mediaRecorder.stream.getTracks().forEach(track => track.stop());
                    mediaRecorder = null;
                    recordButton.innerText = '녹음 시작';
                }
            }
        </script>

        <button id="recordButton" onclick="toggleRecording()" style="margin: 5px;">녹음 시작</button>
        <div id="status" style="margin: 10px;">녹음 대기 중...</div>
    </div>
    """
    st.components.v1.html(audio_recorder_html, height=150)

    # Add file uploader for the recorded audio
    uploaded_file = st.file_uploader("녹음된 파일 선택",
                                     type=['mp3'],
                                     key='audio_uploader')
    if uploaded_file:
        st.session_state.audio_file = uploaded_file


def process_pipeline():
    """Process recorded audio and generate report"""
    if st.button("분석 시작", type="primary", use_container_width=True):
        if not st.session_state.audio_file:
            st.warning("녹음된 음성이 없습니다. 먼저 음성을 녹음하고 파일을 선택해주세요.")
            return

        try:
            # Process the uploaded audio file
            with st.spinner("음성을 텍스트로 변환 중..."):
                transcription = process_whisper(st.session_state.audio_file)
                st.success("음성 변환 완료")
                st.text(f"변환된 텍스트: {transcription}")

            # Analyze text
            with st.spinner("텍스트 분석 중..."):
                analysis_result = process_transcription(transcription)
                st.success("분석 완료")

            # Generate PDF
            with st.spinner("보고서 생성 중..."):
                pdf_path = generate_pdf(analysis_result)
                st.session_state.pdf_path = pdf_path
                st.success("보고서 생성 완료")

        except Exception as e:
            st.error(f"처리 중 오류가 발생했습니다: {str(e)}")


def pdf_displayer_view():
    """Display generated PDF report"""
    if st.session_state.pdf_path and os.path.exists(st.session_state.pdf_path):
        with open(st.session_state.pdf_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()

        st.download_button(label="PDF 다운로드",
                           data=pdf_bytes,
                           file_name="inspection_report.pdf",
                           mime="application/pdf",
                           use_container_width=True)

        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)


def main_view():
    """Render main application view"""
    st.title("소방시설 점검 음성 인식 데모")

    audio_recorder_view()
    st.markdown("---")

    process_pipeline()
    st.markdown("---")

    pdf_displayer_view()
