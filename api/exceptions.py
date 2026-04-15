class AgentError(Exception):
    """Erro ao utilizar o agente"""
    pass


class UserStorageLimitError(Exception):
    """Limite de armazenamento do usuario excedido"""
    pass


class UserTokenLimitError(Exception):
    """Limite de tokens do usuario excedido"""
    pass
