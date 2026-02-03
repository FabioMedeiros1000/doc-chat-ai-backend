from firecrawl import Firecrawl
import os
import sys
from urllib.parse import urlparse

from config.env_settings import get_settings

settings = get_settings()
API_KEY = settings.FIRECRAWL_API_KEY

if not API_KEY:
    raise RuntimeError("FIRECRAWL_API_KEY não encontrada no .env")

app = Firecrawl(api_key=API_KEY)

def scrape_url_to_markdown(url: str) -> str:
    """
    Usa a lib oficial do Firecrawl para extrair o conteúdo da URL em markdown.
    """
    result = app.scrape(
        url=url,
        formats=["markdown"]
    )

    try:
        data = result.markdown
        return data

    except Exception as e:
        raise RuntimeError(f"Erro ao processar resposta do Firecrawl: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scrape_to_markdown.py <URL> [NOME_ARQUIVO.md]")
        sys.exit(1)

    url = sys.argv[1]
    print(f"Scrapeando URL: {url}\n")

    markdown = scrape_url_to_markdown(url)

    output_dir = "docs"
    os.makedirs(output_dir, exist_ok=True)

    if len(sys.argv) >= 3:
        filename = sys.argv[2]
    else:
        parsed = urlparse(url)
        filename = (parsed.path.rstrip("/") or "index").replace("/", "_") + ".md"

    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"\nMarkdown salvo em {filepath}")
