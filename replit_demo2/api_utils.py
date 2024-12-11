from openai import OpenAI
from pydantic import BaseModel
from typing import List
from prompt import content
from key import _OPENAI_API_KEY


def setup_openai_client():
    return OpenAI(api_key=_OPENAI_API_KEY)


def process_whisper(audio_file):
    """Process audio file with Whisper API"""
    client = setup_openai_client()
    try:
        response = client.audio.transcriptions.create(model="whisper-1",
                                                      file=audio_file)
        return response.text
    except Exception as e:
        raise Exception(f"Error processing with Whisper: {str(e)}")


# define pydantic model
class InspectionItem(BaseModel):
    점검번호: str
    불량내용: str

class FireSafetyInspection(BaseModel):
    대상명: str
    소화설비: List[InspectionItem]
    경보설비: List[InspectionItem]
    피난구조설비: List[InspectionItem]
    소화용수설비: List[InspectionItem]
    소화활동설비: List[InspectionItem]
    기타: List[InspectionItem]
    안전시설등: List[InspectionItem]
    비고: str

def process_transcription(transcription):
    """Process text with ChatGPT to generate inspection report"""
    client = setup_openai_client()

    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": content
            }, {
                "role": "user",
                "content": transcription
            }],
            response_format=FireSafetyInspection,
        )
        return FireSafetyInspection.model_validate(
            completion.choices[0].message.parsed).model_dump()
    except Exception as e:
        raise Exception(f"Error processing with ChatGPT: {str(e)}")
