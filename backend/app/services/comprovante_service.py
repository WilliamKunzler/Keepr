import os
import uuid
from pathlib import Path
from typing import Any

from app.extensions import db
from app.models.comprovante import Comprovante
from app.models.factories import ProdutoFactory
from app.models.garantia import Garantia
from app.repositories.comprovante_repo import ComprovanteRepository
from app.schemas.comprovante import ConfirmarComprovante
from app.schemas.produto import ProdutoValidadeCreate
from app.services.ocr_service import OCRService

ALLOWED_IMAGE_EXT = {"png", "jpg", "jpeg"}


class ComprovanteService:
    def __init__(
        self,
        repo: ComprovanteRepository,
        ocr: OCRService,
        upload_folder: str,
    ):
        self.repo = repo
        self.ocr = ocr
        self.upload_folder = upload_folder

    def receber(self, nome_original: str, conteudo: bytes, usuario_id: int) -> Comprovante:
        ext = self._validar_extensao(nome_original)
        nome_final = f"{uuid.uuid4().hex}.{ext}"
        caminho = Path(self.upload_folder) / nome_final
        caminho.write_bytes(conteudo)

        dados = self.ocr.extrair(conteudo)

        comprovante = Comprovante(
            nome_arquivo=nome_final,
            caminho_arquivo=str(caminho),
            texto_extraido=dados.texto_bruto,
            valor_total=dados.valor_total,
            usuario_id=usuario_id,
            confirmado=False,
        )
        comprovante.itens_identificados = dados.produtos_identificados
        return self.repo.save(comprovante)

    def confirmar(
        self, comprovante: Comprovante, dados: ConfirmarComprovante
    ) -> list:
        produtos_criados = []
        for produto_dados in dados.produtos:
            kwargs: dict[str, Any] = {
                "nome": produto_dados.nome,
                "descricao": produto_dados.descricao,
                "categoria_id": produto_dados.categoria_id,
                "usuario_id": comprovante.usuario_id,
                "comprovante_id": comprovante.id,
            }
            if isinstance(produto_dados, ProdutoValidadeCreate):
                produto = ProdutoFactory.criar(
                    "validade", data_validade=produto_dados.data_validade, **kwargs
                )
            else:  # ProdutoGarantiaCreate
                produto = ProdutoFactory.criar(
                    "garantia",
                    numero_serie=produto_dados.numero_serie,
                    data_compra=produto_dados.data_compra,
                    **kwargs,
                )
                produto.garantia = Garantia(
                    data_inicio=produto_dados.data_compra,
                    meses=produto_dados.garantia_meses,
                    data_fim=Garantia.calcular_data_fim(
                        produto_dados.data_compra, produto_dados.garantia_meses
                    ),
                )
            db.session.add(produto)
            produtos_criados.append(produto)

        comprovante.confirmado = True
        db.session.commit()
        return produtos_criados

    def excluir(self, comprovante: Comprovante) -> None:
        """Remove DB + arquivo do disco. Produtos vinculados perdem o link."""
        for p in list(comprovante.produtos):
            p.comprovante_id = None
        try:
            os.remove(comprovante.caminho_arquivo)
        except OSError:
            pass
        self.repo.delete(comprovante)

    @staticmethod
    def _validar_extensao(nome: str) -> str:
        if "." not in nome:
            raise ValueError("arquivo sem extensão")
        ext = nome.rsplit(".", 1)[1].lower()
        if ext not in ALLOWED_IMAGE_EXT:
            raise ValueError(f"extensão '.{ext}' não suportada (use png, jpg ou jpeg)")
        return ext
