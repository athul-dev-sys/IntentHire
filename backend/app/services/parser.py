from io import BytesIO
import re
import zipfile
from typing import Optional
from xml.etree import ElementTree as ET

import fitz  # PyMuPDF
import numpy as np
from PIL import Image

try:
    from rapidocr_onnxruntime import RapidOCR
    ocr_engine = RapidOCR()
except Exception as exc:
    print(f"WARNING: OCR engine unavailable: {exc}")
    ocr_engine = None


def extract_text_from_file(file_content: bytes, mime_type: str) -> Optional[str]:
    if mime_type == "application/pdf":
        return _extract_pdf_text(file_content)

    if mime_type in {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    }:
        return _extract_docx_text(file_content)

    if mime_type == "text/plain":
        text = file_content.decode("utf-8", errors="ignore").strip()
        return text or None

    if mime_type in {"image/png", "image/jpeg", "image/jpg"}:
        return _extract_image_text(file_content)

    return None


def _extract_pdf_text(file_content: bytes) -> Optional[str]:
    try:
        doc = fitz.open(stream=file_content, filetype="pdf")
        text_blocks = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            blocks = page.get_text("blocks")
            blocks.sort(key=lambda b: (b[1], b[0]))

            for block in blocks:
                if block[6] == 0:
                    text = block[4].strip()
                    if text:
                        text_blocks.append(text)

        return "\n\n".join(text_blocks) or None
    except Exception as exc:
        print(f"Error parsing PDF document: {exc}")
        return None


def _extract_docx_text(file_content: bytes) -> Optional[str]:
    try:
        with zipfile.ZipFile(BytesIO(file_content)) as archive:
            with archive.open("word/document.xml") as doc_xml:
                xml_content = doc_xml.read()

        root = ET.fromstring(xml_content)
        namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        paragraphs = []

        for paragraph in root.findall(".//w:p", namespace):
            texts = [node.text for node in paragraph.findall(".//w:t", namespace) if node.text]
            line = "".join(texts).strip()
            if line:
                paragraphs.append(line)

        joined = "\n\n".join(paragraphs).strip()
        return re.sub(r"\n{3,}", "\n\n", joined) or None
    except Exception as exc:
        print(f"Error parsing DOCX document: {exc}")
        return None


def _extract_image_text(file_content: bytes) -> Optional[str]:
    if not ocr_engine:
        return None

    try:
        image = Image.open(BytesIO(file_content)).convert("RGB")
        result, _ = ocr_engine(np.array(image))
        if not result:
            return None

        lines = []
        for item in result:
            if len(item) < 2:
                continue
            text = item[1]
            if isinstance(text, str) and text.strip():
                lines.append(text.strip())

        return "\n".join(lines) or None
    except Exception as exc:
        print(f"Error parsing image document: {exc}")
        return None
