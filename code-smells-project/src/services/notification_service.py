import logging

logger = logging.getLogger(__name__)


class NotificationService:
    def notify_pedido_criado(self, pedido_id, usuario_id):
        logger.info(
            "Pedido criado",
            extra={"pedido_id": pedido_id, "usuario_id": usuario_id},
        )

    def notify_status_alterado(self, pedido_id, novo_status):
        logger.info(
            "Status do pedido atualizado",
            extra={"pedido_id": pedido_id, "status": novo_status},
        )


notification_service = NotificationService()
