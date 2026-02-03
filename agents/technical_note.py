from agno.team import Team
from agno.run.team import TeamRunOutput
from pathlib import Path

from agents.retriever_laws import agent as retriever_laws_agent
from config.llm_settings import get_llm, LLMModel
from prompts.technical_note import instructions

team = Team(
    name="Agente escritor de Nota Técnica Tributária",
    members=[retriever_laws_agent],
    model=get_llm(LLMModel.MEDIUM),
    instructions=instructions,
)

if __name__ == "__main__":
    run: TeamRunOutput = team.run("Quero uma nota técnica sobre as mudanças trazidas pelo IVA DUAL.")

    # --- Salvando em arquivo ---
    output = str(run.content)
    filename = "technical_note_iva_dual.txt"
    output_path = Path(filename)
    output_path.write_text(output, encoding="utf-8")

    print(f"\nArquivo salvo em: {output_path.resolve()}")
