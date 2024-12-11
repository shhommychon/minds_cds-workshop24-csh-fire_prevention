import os
import requests
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def setup_korean_font():
    """Setup Korean font for PDF generation"""
    font_name = "NanumGothic"
    font_path = "NanumGothic-Regular.ttf"
    download_url = "https://themes.googleusercontent.com/static/fonts/earlyaccess/nanumgothic/v3/NanumGothic-Regular.ttf"

    if not os.path.exists(font_path):
        response = requests.get(download_url)
        with open(font_path, "wb") as f:
            f.write(response.content)

    pdfmetrics.registerFont(TTFont(font_name, font_path))
    return font_name