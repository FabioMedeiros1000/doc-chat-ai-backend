import json

from agno.agent import Agent, RunOutput
from config.llm_settings import get_llm, LLMModel
from vectordb.knowledge import knowledge
from prompts.legal_responder import instructions
from schemas.resposta_legal import RespostaLegal

agent = Agent(
    model=get_llm(LLMModel.SMALL),
    instructions=instructions,
    knowledge=knowledge,
    search_knowledge=True,
    add_knowledge_to_context=True,
    markdown=True,
    references_format="text", 
    output_schema=RespostaLegal,
    #parser_model=get_llm(LLMModel.SMALL),
    structured_outputs=False,
    use_json_mode=True,
)

if __name__ == "__main__":
    question = "Existem casos onde alguém do sexo masculino pode se aposentar com 15 anos de colaboração?"

    run: RunOutput = agent.run(question)

    # Se o schema foi aplicado, imprime apenas o JSON identado conforme o schema.
    if isinstance(run.content, RespostaLegal):
        print(json.dumps(run.content.model_dump(), ensure_ascii=False, indent=2))
    else:
        print(run.content)
