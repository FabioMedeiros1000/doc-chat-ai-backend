from typing import Optional, List
from pydantic import BaseModel, Field

class TrechoLei(BaseModel):
    nome_da_lei: Optional[str] = Field(
        None, alias="nome da lei", description="Nome completo ou sigla da lei"
    )
    artigo: Optional[str] = Field(
        None, alias="Artigo", description="Número do artigo, ex: 'Art. 1º'"
    )
    paragrafo: Optional[str] = Field(
        None, alias="Parágrafo", description="Número do parágrafo, ex: '§ 2º'"
    )
    inciso: Optional[str] = Field(
        None, alias="Inciso", description="Número ou indicação do inciso, ex: 'III'"
    )
    texto: Optional[str] = Field(
        None, alias="Texto", description="Texto literal do dispositivo"
    )


class ListaTrechosLei(BaseModel):
    itens: List[TrechoLei]
