from agno.agent import Agent
from config.llm_settings import get_llm, LLMModel
from prompts.chat_responder import instructions
from db.session import get_db_for_agent

def get_chat_responder_agent(knowledge) -> Agent:
    agent = Agent(
        model=get_llm(LLMModel.SMALL),
        instructions=instructions,
        cache_session=True,
        knowledge=knowledge,
        search_knowledge=True,
        add_knowledge_to_context=True,
        db=get_db_for_agent(),
        add_memories_to_context=True,
        add_history_to_context=True,
        num_history_runs=5,
        reasoning=True
    )

    return agent
