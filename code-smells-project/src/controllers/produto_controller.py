from flask import jsonify

from src.config.settings import settings
from src.models.produto_model import ProdutoModel


class ProdutoController:
    @staticmethod
    def _validar_payload(dados, partial=False):
        if not dados:
            return None, ("Dados inválidos", 400)

        if not partial or "nome" in dados:
            if "nome" not in dados:
                return None, ("Nome é obrigatório", 400)
            nome = dados["nome"]
            if len(nome) < 2:
                return None, ("Nome muito curto", 400)
            if len(nome) > 200:
                return None, ("Nome muito longo", 400)

        if not partial or "preco" in dados:
            if "preco" not in dados:
                return None, ("Preço é obrigatório", 400)
            if dados["preco"] < 0:
                return None, ("Preço não pode ser negativo", 400)

        if not partial or "estoque" in dados:
            if "estoque" not in dados:
                return None, ("Estoque é obrigatório", 400)
            if dados["estoque"] < 0:
                return None, ("Estoque não pode ser negativo", 400)

        categoria = dados.get("categoria", "geral")
        if categoria not in settings.CATEGORIAS_VALIDAS:
            return None, (
                f"Categoria inválida. Válidas: {list(settings.CATEGORIAS_VALIDAS)}",
                400,
            )

        return {
            "nome": dados["nome"],
            "descricao": dados.get("descricao", ""),
            "preco": dados["preco"],
            "estoque": dados["estoque"],
            "categoria": categoria,
        }, None

    def listar(self):
        produtos = ProdutoModel.listar_todos()
        return jsonify({"dados": produtos, "sucesso": True}), 200

    def buscar(self, produto_id):
        produto = ProdutoModel.buscar_por_id(produto_id)
        if not produto:
            return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404
        return jsonify({"dados": produto, "sucesso": True}), 200

    def criar(self, dados):
        payload, erro = self._validar_payload(dados)
        if erro:
            mensagem, status = erro
            return jsonify({"erro": mensagem}), status

        produto_id = ProdutoModel.criar(**payload)
        return (
            jsonify(
                {
                    "dados": {"id": produto_id},
                    "sucesso": True,
                    "mensagem": "Produto criado",
                }
            ),
            201,
        )

    def atualizar(self, produto_id, dados):
        if not ProdutoModel.buscar_por_id(produto_id):
            return jsonify({"erro": "Produto não encontrado"}), 404

        payload, erro = self._validar_payload(dados)
        if erro:
            mensagem, status = erro
            return jsonify({"erro": mensagem}), status

        ProdutoModel.atualizar(produto_id, **payload)
        return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200

    def deletar(self, produto_id):
        if not ProdutoModel.buscar_por_id(produto_id):
            return jsonify({"erro": "Produto não encontrado"}), 404
        ProdutoModel.deletar(produto_id)
        return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200

    def buscar_filtrado(self, termo, categoria, preco_min, preco_max):
        resultados = ProdutoModel.buscar(termo, categoria, preco_min, preco_max)
        return (
            jsonify(
                {
                    "dados": resultados,
                    "total": len(resultados),
                    "sucesso": True,
                }
            ),
            200,
        )


produto_controller = ProdutoController()
