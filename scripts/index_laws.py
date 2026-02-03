from agno.knowledge.reader.markdown_reader import MarkdownReader
from agno.knowledge.chunking.recursive import RecursiveChunking
from pathlib import Path

from scripts.metadados import build_metadata
from vectordb.knowledge import knowledge

def index_laws():
    """Roda a indexação dos arquivos Markdown da pasta docs uma vez."""
    reader = MarkdownReader(chunking_strategy=RecursiveChunking())
    docs_path = Path("docs")

    for md_file in docs_path.glob("*.md"):
        metadata = build_metadata(md_file)

        knowledge.add_content(
            name=md_file.stem,
            path=md_file,
            reader=reader,
            metadata=metadata,
            skip_if_exists=True,
        )

if __name__ == "__main__":
    index_laws()
