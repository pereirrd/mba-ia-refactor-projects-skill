from flask import jsonify

from src.models.usuario_model import UsuarioModel


class UsuarioController:
    def listar(self):
        usuarios = UsuarioModel.listar_todos()
        return jsonify({"dados": usuarios, "sucesso": True}), 200

    def buscar(self, usuario_id):
        usuario = UsuarioModel.buscar_por_id(usuario_id)
        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        return jsonify({"dados": usuario, "sucesso": True}), 200

    def criar(self, dados):
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400

        nome = dados.get("nome", "")
        email = dados.get("email", "")
        senha = dados.get("senha", "")

        if not nome or not email or not senha:
            return jsonify({"erro": "Nome, email e senha são obrigatórios"}), 400

        usuario_id = UsuarioModel.criar(nome, email, senha)
        return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201

    def login(self, dados):
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400

        email = dados.get("email", "")
        senha = dados.get("senha", "")
        if not email or not senha:
            return jsonify({"erro": "Email e senha são obrigatórios"}), 400

        usuario = UsuarioModel.autenticar(email, senha)
        if not usuario:
            return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401

        return (
            jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}),
            200,
        )


usuario_controller = UsuarioController()
