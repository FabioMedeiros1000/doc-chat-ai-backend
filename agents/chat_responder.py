from agno.agent import Agent, RunOutput
from config.llm_settings import get_llm, LLMModel
from vectordb.knowledge import knowledge
from prompts.chat_responder import instructions

agent = Agent(
    model=get_llm(LLMModel.SMALL),
    instructions=instructions,
    knowledge=knowledge,
    search_knowledge=True,
    add_knowledge_to_context=True
)

if __name__ == "__main__":
    question = "Existem casos onde alguém do sexo masculino pode se aposentar com 15 anos de colaboração?"

    run: RunOutput = agent.run(question)

    print(run.content)
