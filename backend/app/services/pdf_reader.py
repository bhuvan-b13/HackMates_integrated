import requests
from pypdf import PdfReader
from io import BytesIO


def read_pdf(url: str) -> str:
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    )

    response.raise_for_status()

    pdf = PdfReader(BytesIO(response.content))

    text = ""

    for page in pdf.pages:
        page_text = page.extract_text() or ""
        text += page_text + "\n"

    return text.strip()