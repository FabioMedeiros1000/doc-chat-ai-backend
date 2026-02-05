ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}

UPLOAD_SOURCE = "upload"
UPLOAD_SUCCESS_MESSAGE = "File indexed successfully."

ERROR_UNSUPPORTED_FORMAT = "Unsupported format. Send .pdf, .docx or .txt."
ERROR_EMPTY_FILE = "Empty file."
ERROR_NO_TEXT = "Could not extract text from file."

ERROR_MISSING_PDF_DEP = "Missing dependency for PDF. Install 'pypdf'."
ERROR_MISSING_DOCX_DEP = "Missing dependency for DOCX. Install 'python-docx'."
