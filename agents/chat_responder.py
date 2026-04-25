from agno.agent import Agent
from config.llm_settings import get_llm, LLMModel
from prompts.chat_responder import instructions
from prompts.chat_router import instructions as router_instructions
from schemas.chat_router_decision import ChatRouterDecision
from db.session import get_db_for_agent

def get_chat_responder_agent(knowledge, api_key: str | None = None) -> Agent:
    agent = Agent(
        model=get_llm(LLMModel.SMALL, api_key=api_key),
        instructions=instructions,
        cache_session=True,
        knowledge=knowledge,
        search_knowledge=True,
        add_knowledge_to_context=True,
        db=get_db_for_agent(),
        add_memories_to_context=True,
        add_history_to_context=True,
        num_history_runs=5,
        markdown=False
    )

    return agent


def get_chat_router_agent(api_key: str | None = None) -> Agent:
    agent = Agent(
        model=get_llm(LLMModel.SMALL, api_key=api_key),
        instructions=router_instructions,
        output_schema=ChatRouterDecision,
        markdown=False,
    )

    return agent
