from agno.knowledge.reader.markdown_reader import MarkdownReader
from agno.knowledge.chunking.recursive import RecursiveChunking
from pathlib import Path

from scripts.metadados import build_metadata
from vectordb.knowledge import knowledge

def index_laws(content_hash: str, md_path: Path, metadata: dict):
    reader = MarkdownReader(chunking_strategy=RecursiveChunking())
    knowledge.add_content(
        name=f"upload_{content_hash}",
        path=md_path,
        reader=reader,
        metadata=metadata,
        skip_if_exists=True,
    )

if __name__ == "__main__":
    index_laws()
