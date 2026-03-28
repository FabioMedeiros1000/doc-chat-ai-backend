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
