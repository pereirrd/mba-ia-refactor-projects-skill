import logging

from flask import jsonify

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"erro": "Não encontrado", "sucesso": False}), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"erro": "Requisição inválida", "sucesso": False}), 400

    @app.errorhandler(Exception)
    def unexpected_error(error):
        logger.exception("Erro não tratado: %s", error)
        return jsonify({"erro": "Erro interno", "sucesso": False}), 500
