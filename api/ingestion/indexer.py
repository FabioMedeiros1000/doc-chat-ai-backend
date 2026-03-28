from pathlib import Path
from typing import Dict

from agno.knowledge.reader.markdown_reader import MarkdownReader
from agno.knowledge.chunking.recursive import RecursiveChunking

from api.exceptions import AgentError
from vectordb.knowledge import KnowledgeProvider


class Indexer:
    def __init__(self, knowledge_provider: KnowledgeProvider | None = None) -> None:
        self._knowledge_provider = knowledge_provider or KnowledgeProvider()

    async def index_markdown_file(
        self,
        path: Path,
        content_hash: str,
        metadata: Dict,
        userHash: str | None = None,
    ) -> None:
        try:
            reader = MarkdownReader(
                chunking_strategy=RecursiveChunking(chunk_size=700, overlap=100)
            )
            knowledge = self._knowledge_provider.get_knowledge(userHash)

            if knowledge is None:
                raise AgentError(
                    "Knowledge base is not available for the specified collection."
                )

            await knowledge.add_content_async(
                name=f"upload_{content_hash}",
                path=path,
                reader=reader,
                metadata=metadata,
                skip_if_exists=True,
            )
        except Exception as e:
            raise AgentError(f"Error indexing file: {str(e)}") from e



