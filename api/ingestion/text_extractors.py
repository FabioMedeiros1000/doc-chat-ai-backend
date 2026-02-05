from pathlib import Path

from api.exceptions import AgentError
from api.ingestion.constants import ERROR_MISSING_DOCX_DEP, ERROR_MISSING_PDF_DEP


def extract_text(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return _extract_text_from_pdf(path)
    if ext == ".docx":
        return _extract_text_from_docx(path)
    if ext == ".txt":
        return _extract_text_from_txt(path)

    raise AgentError(f"Unsupported format: {ext}")


def _extract_text_from_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except Exception as e:
        raise AgentError(ERROR_MISSING_PDF_DEP) from e

    reader = PdfReader(str(path))
    parts = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text:
            parts.append(text)
    return "\n".join(parts)


def _extract_text_from_docx(path: Path) -> str:
    try:
        from docx import Document
    except Exception as e:
        raise AgentError(ERROR_MISSING_DOCX_DEP) from e

    doc = Document(str(path))
    parts = [p.text for p in doc.paragraphs if p.text]
    return "\n".join(parts)


def _extract_text_from_txt(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")
