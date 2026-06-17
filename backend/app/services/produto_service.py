"""ProdutoService — implementação do padrão Facade.

Aplica:
- Facade: o caller chama um método só e a fachada cuida do ballet entre
  Factory, Repository, Garantia e (opcionalmente) OCR.
- DIP: recebe abstrações no construtor, não implementações concretas.
- SRP: persistência fica no repository, criação na Factory, OCR no OCRService.
"""
from app.models.factories import ProdutoFactory
from app.models.garantia import Garantia
from app.models.produto import ProdutoValidade, ProdutoGarantia
from app.repositories.produto_repo import ProdutoRepository
from app.schemas.produto import ProdutoValidadeCreate, ProdutoGarantiaCreate
from app.services.ocr_service import OCRService


class ProdutoService:
    """Facade pra operações com produtos."""

    def __init__(self, repo: ProdutoRepository, ocr: OCRService | None = None):
        self.repo = repo
        self.ocr = ocr

    def cadastrar_via_comprovante(self, imagem_bytes: bytes, usuario_id: int):
        """Fluxo completo: foto da nota → produtos pré-cadastrados.

        Retorna lista de produtos detectados pra que o usuário confirme
        antes do cadastro definitivo (RN11).
        """
        if self.ocr is None:
            raise RuntimeError("ProdutoService sem OCR configurado")
        dados = self.ocr.extrair(imagem_bytes)
        # TODO: usar ProdutoFactory pra criar instâncias a partir de
        # dados.produtos_identificados e persistir como rascunho.
        return {
            "texto_extraido": dados.texto_bruto,
            "produtos_identificados": dados.produtos_identificados,
        }

    def cadastrar_produto_validade(
        self, dados: ProdutoValidadeCreate, usuario_id: int
    ) -> ProdutoValidade:
        produto = ProdutoFactory.criar(
            "validade",
            nome=dados.nome,
            descricao=dados.descricao,
            categoria_id=dados.categoria_id,
            data_validade=dados.data_validade,
            usuario_id=usuario_id,
        )
        return self.repo.save(produto)

    def cadastrar_produto_garantia(
        self, dados: ProdutoGarantiaCreate, usuario_id: int
    ) -> ProdutoGarantia:
        produto = ProdutoFactory.criar(
            "garantia",
            nome=dados.nome,
            descricao=dados.descricao,
            categoria_id=dados.categoria_id,
            numero_serie=dados.numero_serie,
            data_compra=dados.data_compra,
            usuario_id=usuario_id,
        )
        produto.garantia = Garantia(
            data_inicio=dados.data_compra,
            meses=dados.garantia_meses,
            data_fim=Garantia.calcular_data_fim(dados.data_compra, dados.garantia_meses),
        )
        return self.repo.save(produto)

    def atualizar(self, produto, dados) -> None:
        """RF02 — aplica `dados` (ProdutoUpdate) no produto."""
        atualizacoes = dados.model_dump(exclude_unset=True)
        for campo, valor in atualizacoes.items():
            setattr(produto, campo, valor)

        if "data_compra" in atualizacoes and produto.garantia is not None:
            produto.garantia.data_inicio = produto.data_compra
            produto.garantia.data_fim = Garantia.calcular_data_fim(
                produto.data_compra, produto.garantia.meses
            )

        self.repo.save(produto)

    def excluir(self, produto) -> None:
        """RF03 — remove o produto. Cascade deleta Garantia."""
        self.repo.delete(produto)
