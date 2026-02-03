from agno.agent import RunOutput

from schemas.resposta_simples import RespostaSimples
from schemas.trechos_lei import ListaTrechosLei
from schemas.resposta_legal import RespostaLegal
from agents.explain_law import agent as agent_explain_law
from agents.legal_responder import agent as agent_responder
from agents.chat_responder import agent as chat_responder
from agents.technical_note import team as agent_technical_note
from agents.retriever_laws import agent as agent_retriever
from schemas.pergunta import Pergunta
from api.exceptions import AgentError

class LeiService:
    def retriever_laws(self, payload: Pergunta) -> ListaTrechosLei:
        try:
            run: RunOutput = agent_retriever.run(
                f"Quais dispositivos tratam de: {payload.pergunta}"
            )  
        except Exception as e:
            raise AgentError("Erro ao utilizar o agente de recuperação de leis.") from e

        results: ListaTrechosLei = run.content  
        return results
    
    def explain_law(self, payload: Pergunta) -> str:
        try:
            run: RunOutput = agent_explain_law.run(payload.pergunta)  
        except Exception as e:
            raise AgentError("Erro ao utilizar o agente que explica leis de forma simplificada.") from e

        result: str = run.content  
        return result
    
    def technical_note(self, payload: Pergunta) -> str:
        try:
            run: RunOutput = agent_technical_note.run(f"Nota técnica sobre: {payload.pergunta}")  
        except Exception as e:
            raise AgentError("Erro ao utilizar o agente que redige norma técnica sobre leis tributárias") from e

        result: str = run.content  
        return result

    def responder(self, payload: Pergunta) -> RespostaLegal:
        try:
            run: RunOutput = agent_responder.run(
                payload.pergunta
            )
        except Exception as e:
            raise AgentError("Error ao utilizar o agente") from e
        
        if isinstance(run.content, RespostaLegal):
            return run.content

        try:
            return RespostaLegal.model_validate(run.content)
        except Exception as e:
            raise AgentError("Resposta do agente em formato inesperado") from e
        
    def chat_responder(self, payload: Pergunta) -> RespostaSimples:
        try:
            run: RunOutput = chat_responder.run(
                payload.pergunta
            )
        except Exception as e:
            raise AgentError("Error ao utilizar o agente") from e

        # O agente normalmente retorna uma string simples em run.content.
        # Como o endpoint declara response_model=RespostaSimples, precisamos
        # garantir que o retorno seja um objeto desse modelo.
        if isinstance(run.content, RespostaSimples):
            return run.content

        if isinstance(run.content, str):
            return RespostaSimples(resposta=run.content)

        try:
            return RespostaSimples.model_validate(run.content)
        except Exception as e:
            raise AgentError("Resposta do agente em formato inesperado") from e
