ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}

UPLOAD_SOURCE = "upload"
UPLOAD_QUEUED_MESSAGE = "Seu arquivo esta sendo salvo e processado para leitura da IA."

MAX_USER_STORAGE_BYTES = 7 * 1024 * 1024
ERROR_MAX_USER_STORAGE = "Limite de 7MB por usuario atingido. Remova arquivos antigos para enviar novos."
ERROR_FILE_TOO_LARGE = "Arquivo excede o limite de 7MB."

ERROR_UNSUPPORTED_FORMAT = "Unsupported format. Send .pdf, .docx or .txt."
ERROR_EMPTY_FILE = "Empty file."
ERROR_NO_TEXT = "Could not extract text from file."

ERROR_MISSING_PDF_DEP = "Missing dependency for PDF. Install 'pypdf'."
ERROR_MISSING_DOCX_DEP = "Missing dependency for DOCX. Install 'python-docx'."
