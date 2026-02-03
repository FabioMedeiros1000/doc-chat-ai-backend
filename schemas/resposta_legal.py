from pydantic import BaseModel, Field

class RespostaLegal(BaseModel):
    resumo_simplificado: str = Field(..., description="Resposta direta e clara ao usuário")
    trecho_documentacao: str = Field(..., description="Trecho literal da lei usada como fundamento")
    nome_da_lei: str | None = Field(None, description="Identificação da norma, ex.: 'LC 214/2024'")
    artigo: str | None = Field(None, description="Número do artigo, ex.: 'Art. 7º'")