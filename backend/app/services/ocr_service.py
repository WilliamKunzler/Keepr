import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from io import BytesIO
from typing import Optional


@dataclass
class ComprovanteData:
    """Resultado da extração — entrada pra confirmação manual do usuário (RN11)."""

    texto_bruto: str
    produtos_identificados: list[dict] = field(default_factory=list)
    valor_total: Optional[float] = None
    data_compra: Optional[str] = None


class OCRService(ABC):
    @abstractmethod
    def extrair(self, imagem_bytes: bytes) -> ComprovanteData:
        ...


class GeminiOCRService(OCRService):
    """Implementação usando Gemini Vision para análise de comprovantes.

    Envia a imagem ao modelo multimodal e pede JSON estruturado com produtos
    e valor total — sem regex, sem heurística de texto.
    """

    _PROMPT = """
Analise esta nota fiscal ou comprovante de compra.

Extraia TODOS os produtos encontrados.

Retorne APENAS um JSON válido no formato abaixo, sem markdown, sem explicações:

{
  "produtos": [
    {
      "nome": "",
      "valor": 0.0
    }
  ],
  "valor_total_nota": 0.0
}

Regras:
- "nome" deve ser a descrição do produto, limpa e legível.
- "valor" é o valor unitário do item como número decimal.
- "valor_total_nota" é o total da nota como número decimal.
- Converta valores monetários para número decimal (ex: "R$ 12,50" → 12.5).
- Retorne somente JSON válido, sem qualquer outro texto.
"""

    def __init__(self, api_key: str, model: str = "gemini-3.5-flash") -> None:
        self.api_key = api_key
        self.model_name = model

    def extrair(self, imagem_bytes: bytes) -> ComprovanteData:
        import google.generativeai as genai
        from google.api_core import exceptions as gexc
        from google.api_core.retry import Retry
        from PIL import Image

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model_name)
        imagem = Image.open(BytesIO(imagem_bytes))

        # Sem retry automático: por padrão o SDK reenvia a mesma chamada várias
        # vezes em caso de 429/503, e isso sozinho estoura a cota de 5 req/min do
        # free tier. Com o predicate sempre False, é 1 upload = 1 requisição.
        sem_retry = Retry(predicate=lambda _exc: False)

        try:
            response = model.generate_content(
                [self._PROMPT, imagem],
                request_options={"retry": sem_retry, "timeout": 60},
            )
            texto = response.text.strip()
            # Remove blocos markdown caso o modelo os inclua mesmo pedindo pra não
            if texto.startswith("```"):
                texto = re.sub(r"^```[a-z]*\n?", "", texto)
                texto = re.sub(r"\n?```$", "", texto)
            dados = json.loads(texto)
        except gexc.ResourceExhausted:
            return ComprovanteData(
                texto_bruto=(
                    "[Limite de requisições da IA atingido (free tier: 5/min). "
                    "Aguarde cerca de 1 minuto e reenvie a nota.]"
                ),
                produtos_identificados=[],
            )
        except Exception as exc:
            return ComprovanteData(
                texto_bruto=f"[Gemini erro: {exc}]",
                produtos_identificados=[],
            )

        produtos = [
            {"nome": p.get("nome", ""), "valor": p.get("valor")}
            for p in dados.get("produtos", [])
            if p.get("nome")
        ]

        return ComprovanteData(
            texto_bruto=texto,
            produtos_identificados=produtos,
            valor_total=dados.get("valor_total_nota"),
        )
