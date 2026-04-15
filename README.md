## Guia de Uso do Projeto

Este README descreve os principais comandos para executar as etapas do projeto, desde a coleta de conteúdo até a execução dos agentes e da API.

---

### Gerar arquivos Markdown a partir do Firecrawl

Utilize o comando abaixo para realizar o scraping de um site e gerar um arquivo Markdown com o conteúdo extraído:

```powershell
python -m scripts.scraping "<URL_SITE>" "<NOME_ARQUIVO>.md"
```

### Vetorizar arquivos no banco vetorial

Após gerar os arquivos Markdown, execute o comando abaixo para indexar o conteúdo no banco vetorial:

```powershell
python -m scripts.index_laws
```

### Executar os agentes

Para rodar um agente específico, utilize o comando abaixo, informando o nome do arquivo do agente sem a extensão `.py`:

```powershell
python -m agents.<nome_do_arquivo_do_agente_sem_.py>
```

### Subir o Qdrant

Inicie o banco vetorial Qdrant utilizando Docker:

```powershell
docker-compose up -d
```

### Visualizar o Qdrant

Acesse o dashboard do Qdrant pelo navegador:

```powershell
http://localhost:6333/dashboard
```

### Criar ambiente virtual

```powershell
uv venv
```

**Observação**: Caso não tenha `uv`, você pode instalá-lo com `pip install uv`.

### Ativar o ambiente virtual

Windows:

```powershell
.venv/Scripts/activate
```

### Como baixar as dependências

```powershell
uv sync
```

### Subir a API

Com o ambiente virtual ativado, execute:

```powershell
uvicorn api.main:app
```

### Persistência de sessão do Agno

O histórico/sessão do Agno é persistido no mesmo banco definido em `MYSQL_DATABASE`.
Ao subir a API pela primeira vez, a biblioteca cria automaticamente as tabelas auxiliares dela nesse schema, como `agno_sessions`.

### Histórico do chat e limite de tokens

O histórico do chat da aplicação é salvo na tabela `chat_messages`.
O endpoint abaixo retorna as mensagens de um usuário em ordem cronológica:

```http
GET /chat/history?userHash=<USER_HASH>
```

O limite acumulado de tokens por usuário pode ser configurado com a variável:

```env
USER_MAX_CHAT_TOKENS=50000
```

### Subir o celery

```powershell
python -m celery -A celery_app worker --loglevel=info --pool=solo
```
