from flask import jsonify

from src.config.settings import settings
from src.models.pedido_model import PedidoModel
from src.services.notification_service import notification_service


class PedidoController:
    def criar(self, dados):
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400

        usuario_id = dados.get("usuario_id")
        itens = dados.get("itens", [])

        if not usuario_id:
            return jsonify({"erro": "Usuario ID é obrigatório"}), 400
        if not itens:
            return jsonify({"erro": "Pedido deve ter pelo menos 1 item"}), 400

        resultado, erro = PedidoModel.criar(usuario_id, itens)
        if erro:
            return jsonify({"erro": erro, "sucesso": False}), 400

        notification_service.notify_pedido_criado(
            resultado["pedido_id"], usuario_id
        )
        return (
            jsonify(
                {
                    "dados": resultado,
                    "sucesso": True,
                    "mensagem": "Pedido criado com sucesso",
                }
            ),
            201,
        )

    def listar_por_usuario(self, usuario_id):
        pedidos = PedidoModel.listar_por_usuario(usuario_id)
        return jsonify({"dados": pedidos, "sucesso": True}), 200

    def listar_todos(self):
        pedidos = PedidoModel.listar_todos()
        return jsonify({"dados": pedidos, "sucesso": True}), 200

    def atualizar_status(self, pedido_id, dados):
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400

        novo_status = dados.get("status", "")
        if novo_status not in settings.STATUS_PEDIDO_VALIDOS:
            return jsonify({"erro": "Status inválido"}), 400

        if not PedidoModel.atualizar_status(pedido_id, novo_status):
            return jsonify({"erro": "Pedido não encontrado"}), 404

        notification_service.notify_status_alterado(pedido_id, novo_status)
        return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200

    def relatorio_vendas(self):
        relatorio = PedidoModel.relatorio_vendas()
        return jsonify({"dados": relatorio, "sucesso": True}), 200

    def health(self):
        counts = PedidoModel.contagens_health()
        return (
            jsonify(
                {
                    "status": "ok",
                    "database": "connected",
                    "counts": counts,
                    "versao": settings.APP_VERSION,
                    "ambiente": settings.ENVIRONMENT,
                    "debug": settings.DEBUG,
                }
            ),
            200,
        )


pedido_controller = PedidoController()
