from typing import Dict, Any
from pathlib import Path

# Mapeamento específico por arquivo (stem do nome do .md)
DOC_METADATA: Dict[str, Dict[str, Any]] = {
    "ec45": {
        "id_norma": "EC 45/2004",
        "tipo_norma": "emenda_constitucional",
        "numero": 45,
        "ano": 2004,
        "situacao": "vigente",
        "esfera": "constitucional",
        "tema_principal": "Reforma do Poder Judiciário, organização da justiça e controle externo (CNJ).",
        "foco_tributario": (
            "Impactos institucionais e processuais relevantes para o contencioso "
            "tributário e controle de constitucionalidade."
        ),
        "palavras_chave": [
            "EC 45",
            "reforma do judiciário",
            "controle de constitucionalidade",
            "CNJ",
            "processo judicial",
            "contencioso tributário",
        ],
    },
    "ec87": {
        "id_norma": "EC 87/2015",
        "tipo_norma": "emenda_constitucional",
        "numero": 87,
        "ano": 2015,
        "situacao": "vigente",
        "esfera": "constitucional",
        "tema_principal": "ICMS nas operações interestaduais destinadas a consumidor final.",
        "foco_tributario": (
            "Regras de partilha do ICMS entre estados de origem e destino; "
            "base para discussões de tributação no destino e reforma do consumo."
        ),
        "palavras_chave": [
            "EC 87",
            "ICMS",
            "consumidor final",
            "operações interestaduais",
            "partilha do imposto",
            "substituição tributária",
            "tributação no destino",
        ],
    },
    "ec103": {
        "id_norma": "EC 103/2019",
        "tipo_norma": "emenda_constitucional",
        "numero": 103,
        "ano": 2019,
        "situacao": "vigente",
        "esfera": "constitucional",
        "tema_principal": "Reforma da Previdência Social.",
        "foco_tributario": (
            "Impacto sobre contribuições previdenciárias e contribuições sociais, "
            "incluindo base de cálculo, alíquotas e regras de financiamento da seguridade."
        ),
        "palavras_chave": [
            "EC 103",
            "reforma da previdência",
            "contribuições sociais",
            "seguridade social",
            "INSS",
            "aposentadoria",
        ],
    },
    "ec132": {
        "id_norma": "EC 132/2023",
        "tipo_norma": "emenda_constitucional",
        "numero": 132,
        "ano": 2023,
        "situacao": "vigente",
        "esfera": "constitucional",
        "tema_principal": "Reforma tributária do consumo: IBS, CBS e IS.",
        "foco_tributario": (
            "Institui o modelo de imposto sobre valor agregado (IVA dual), criando o IBS "
            "e a CBS, regras de transição, fundos de compensação e repartição de receitas."
        ),
        "palavras_chave": [
            "EC 132",
            "reforma tributária",
            "IBS",
            "CBS",
            "IS",
            "IVA dual",
            "tributação sobre consumo",
            "sistema tributário",
        ],
    },
    "lc214": {
        "id_norma": "LC 214/2025",
        "tipo_norma": "lei_complementar",
        "numero": 214,
        "ano": 2025,
        "situacao": "vigente",
        "esfera": "infraconstitucional",
        "tema_principal": "Instituição da CBS e IBS e regras gerais da tributação sobre bens e serviços.",
        "foco_tributario": (
            "Define hipóteses de incidência, imunidades, não cumulatividade, créditos, "
            "regras de apuração, exportações e aspectos operacionais do IBS e da CBS."
        ),
        "palavras_chave": [
            "LC 214",
            "CBS",
            "IBS",
            "reforma tributária",
            "não cumulatividade",
            "créditos",
            "exportações",
            "imunidades",
        ],
    },
    "plp108": {
        "id_norma": "PLP 108/2024",
        "tipo_norma": "projeto_lei_complementar",
        "numero": 108,
        "ano": 2024,
        "situacao": "projeto",
        "esfera": "infraconstitucional",
        "tema_principal": "Projeto que regulamenta pontos específicos da reforma tributária do consumo (IBS/CBS).",
        "foco_tributario": (
            "Normas infraconstitucionais propostas para detalhar regime de transição, "
            "setores específicos, regimes diferenciados e operacionalização do IBS/CBS."
        ),
        "palavras_chave": [
            "PLP 108",
            "projeto IBS",
            "projeto CBS",
            "reforma tributária",
            "regulamentação",
            "regime de transição",
            "setores específicos",
        ],
    },
}

def build_metadata(md_file: Path) -> Dict[str, Any]:
    """
    Gera metadados ricos para cada documento, com base no stem do arquivo.
    Ex.: 'ec45.md' -> stem = 'ec45'.
    """
    stem = md_file.stem.lower()

    base_meta: Dict[str, Any] = {
        "filename": md_file.name,
        "path": str(md_file),
        "categoria_geral": "sistema_tributario_brasileiro",
    }

    # Se houver metadados específicos, mescla com o base
    if stem in DOC_METADATA:
        specific = DOC_METADATA[stem]
    else:
        # Fallback genérico para qualquer outro .md que aparecer
        specific = {
            "id_norma": stem,
            "tipo_norma": "desconhecido",
            "tema_principal": "Documento jurídico relacionado ao sistema tributário brasileiro.",
            "foco_tributario": "Conteúdo potencialmente relevante para análise tributária.",
            "palavras_chave": ["tributário", "norma", "lei", stem],
        }

    return {**base_meta, **specific}
