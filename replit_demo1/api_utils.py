from openai import OpenAI
from key import _OPENAI_API_KEY

def setup_openai_client():
    return OpenAI(api_key=_OPENAI_API_KEY)

def process_whisper(file_path, mode="transcription"):
    """Process audio file with Whisper API"""
    client = setup_openai_client()

    try:
        with open(file_path, "rb") as audio_file:
            if mode == "transcription":
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
                return response.text
            else:  # timestamp mode
                response = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-1",
                    response_format="verbose_json",
                    timestamp_granularities=["word"]
                )
                # Format timestamp results
                formatted_result = ""
                for word in response.words:
                    formatted_result += f"[{word.start:.2f}s - {word.end:.2f}s] {word.word}\n"
                return formatted_result
    except Exception as e:
        raise Exception(f"Error processing with Whisper: {str(e)}")