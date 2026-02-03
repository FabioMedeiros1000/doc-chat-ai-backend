from agno.knowledge.knowledge import Knowledge
from vectordb.connection import get_vector_db

COLLECTION_NAME = "laws"

knowledge = Knowledge(
    name="Leis tributárias",
    description="Vector store com normas constitucionais, leis complementares e projetos relacionados à reforma tributária e ao sistema tributário brasileiro.",
    vector_db=get_vector_db(collection_name=COLLECTION_NAME),
)