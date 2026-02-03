from agno.agent import Agent, RunOutput
from config.llm_settings import get_llm, LLMModel
from prompts.explain_law import instructions
from rich.pretty import pprint

agent = Agent(
    name="Agente responsável por explicar leis tributárias de forma clara e simplificada.",
    model=get_llm(LLMModel.SMALL),
    instructions=instructions,
    markdown=False
)

if __name__ == "__main__":
    article_example = """
    Art. 4º. O IBS e a CBS incidem sobre operações onerosas com bens ou com serviços. § 1º As operações não onerosas com bens ou com serviços serão tributadas nas hipóteses expressamente previstas nesta Lei Complementar.
    """
    run: RunOutput = agent.run(article_example)
    pprint(run.content)
