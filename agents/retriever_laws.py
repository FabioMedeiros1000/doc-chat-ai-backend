from agno.agent import Agent, RunOutput

from scripts.index_laws import knowledge
from config.llm_settings import get_llm, LLMModel
from schemas.trechos_lei import ListaTrechosLei
from prompts.retriever_laws import instructions
from rich.pretty import pprint

agent = Agent(
    name="Agente RAG Tributário",
    role="Localizar dispositivos relevantes nas normas da reforma tributária (EC 132, EC 45, EC 87, EC 103, LC 214 e PLP 108) e devolver, em JSON estruturado, o texto literal da lei com contexto mínimo para interpretação jurídica.",
    model=get_llm(LLMModel.MEDIUM),
    instructions=instructions,
    markdown=False,
    knowledge=knowledge,
    search_knowledge=True,
    enable_agentic_knowledge_filters=True,
    add_knowledge_to_context=True,
    references_format="json",
    add_datetime_to_context=True,
    output_schema=ListaTrechosLei,
    # parser_model=get_llm(LLMModel.SMALL),
    structured_outputs=False,
    use_json_mode=True,
)

if __name__ == "__main__":
    run: RunOutput = agent.run("Quais dispositivos tratam do IVA DUAL?")
    pprint(run.content)
