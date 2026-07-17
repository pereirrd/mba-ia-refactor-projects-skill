from flask import jsonify


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Não encontrado"}), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Requisição inválida"}), 400

    @app.errorhandler(Exception)
    def unexpected_error(error):
        app.logger.exception(error)
        return jsonify({"error": "Erro interno"}), 500
