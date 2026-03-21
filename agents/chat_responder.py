from agno.agent import Agent, RunOutput
from config.llm_settings import get_llm, LLMModel
from prompts.chat_responder import instructions

def get_chat_responder_agent(knowledge) -> Agent:
    agent = Agent(
        model=get_llm(LLMModel.SMALL),
        instructions=instructions,
        knowledge=knowledge,
        search_knowledge=True,
        add_knowledge_to_context=True
    )

    return agent

if __name__ == "__main__":
    question = "Existem casos onde alguém do sexo masculino pode se aposentar com 15 anos de colaboração?"

    agent = get_chat_responder_agent(knowledge=None)

    run: RunOutput = agent.run(question)

    print(run.content)
