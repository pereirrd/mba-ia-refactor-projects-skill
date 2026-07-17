from flask import jsonify, request

from src.config.settings import settings
from src.controllers.pedido_controller import pedido_controller
from src.controllers.produto_controller import produto_controller
from src.controllers.usuario_controller import usuario_controller


def register_routes(app):
    @app.get("/")
    def index():
        return jsonify(
            {
                "mensagem": "Bem-vindo à API da Loja",
                "versao": settings.APP_VERSION,
                "endpoints": {
                    "produtos": "/produtos",
                    "usuarios": "/usuarios",
                    "pedidos": "/pedidos",
                    "login": "/login",
                    "relatorios": "/relatorios/vendas",
                    "health": "/health",
                },
            }
        )

    @app.get("/produtos")
    def listar_produtos():
        return produto_controller.listar()

    @app.get("/produtos/busca")
    def buscar_produtos():
        termo = request.args.get("q", "")
        categoria = request.args.get("categoria")
        preco_min = request.args.get("preco_min")
        preco_max = request.args.get("preco_max")
        if preco_min is not None:
            preco_min = float(preco_min)
        if preco_max is not None:
            preco_max = float(preco_max)
        return produto_controller.buscar_filtrado(
            termo, categoria, preco_min, preco_max
        )

    @app.get("/produtos/<int:produto_id>")
    def buscar_produto(produto_id):
        return produto_controller.buscar(produto_id)

    @app.post("/produtos")
    def criar_produto():
        return produto_controller.criar(request.get_json())

    @app.put("/produtos/<int:produto_id>")
    def atualizar_produto(produto_id):
        return produto_controller.atualizar(produto_id, request.get_json())

    @app.delete("/produtos/<int:produto_id>")
    def deletar_produto(produto_id):
        return produto_controller.deletar(produto_id)

    @app.get("/usuarios")
    def listar_usuarios():
        return usuario_controller.listar()

    @app.get("/usuarios/<int:usuario_id>")
    def buscar_usuario(usuario_id):
        return usuario_controller.buscar(usuario_id)

    @app.post("/usuarios")
    def criar_usuario():
        return usuario_controller.criar(request.get_json())

    @app.post("/login")
    def login():
        return usuario_controller.login(request.get_json())

    @app.post("/pedidos")
    def criar_pedido():
        return pedido_controller.criar(request.get_json())

    @app.get("/pedidos")
    def listar_todos_pedidos():
        return pedido_controller.listar_todos()

    @app.get("/pedidos/usuario/<int:usuario_id>")
    def listar_pedidos_usuario(usuario_id):
        return pedido_controller.listar_por_usuario(usuario_id)

    @app.put("/pedidos/<int:pedido_id>/status")
    def atualizar_status_pedido(pedido_id):
        return pedido_controller.atualizar_status(pedido_id, request.get_json())

    @app.get("/relatorios/vendas")
    def relatorio_vendas():
        return pedido_controller.relatorio_vendas()

    @app.get("/health")
    def health_check():
        return pedido_controller.health()
