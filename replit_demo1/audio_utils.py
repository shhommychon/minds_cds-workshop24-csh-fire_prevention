import os
from pydub import AudioSegment

_supported_extensions = (
    ".mp3", 
    ".aac", ".m4a", ".wav", ".flac", ".aiff",
    ".ogg", ".mp4", ".mpeg", ".mpga", ".webm",
)


def convert_to_mp3(file_path):
    """Convert audio file to MP3 format"""

    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension not in _supported_extensions:
        raise ValueError(f"Unsupported file type: {file_extension}")

    if file_extension == ".mp3":
        return file_path

    output_path = os.path.splitext(file_path)[0] + "_converted.mp3"

    try:
        audio = AudioSegment.from_file(file_path)
        audio.export(output_path, format="mp3")

        # Check file size
        if os.path.getsize(output_path) > 25 * 1024 * 1024:  # 25MB in bytes
            os.remove(output_path)
            raise ValueError("Converted file exceeds 25MB limit")

        return output_path
    except Exception as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        raise Exception(f"Error converting audio: {str(e)}")
