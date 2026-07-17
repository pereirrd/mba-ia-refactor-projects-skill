from src.config.settings import settings
from src.models.database import db_cursor, get_connection


class PedidoModel:
    @staticmethod
    def _calcular_desconto(faturamento):
        for limite, taxa in settings.DESCONTO_FAIXAS:
            if faturamento > limite:
                return faturamento * taxa
        return 0

    @classmethod
    def criar(cls, usuario_id, itens):
        connection = get_connection()
        cursor = connection.cursor()
        try:
            total = 0
            produtos_cache = {}

            for item in itens:
                cursor.execute(
                    "SELECT * FROM produtos WHERE id = ?",
                    (item["produto_id"],),
                )
                produto = cursor.fetchone()
                if produto is None:
                    return None, f"Produto {item['produto_id']} não encontrado"
                if produto["estoque"] < item["quantidade"]:
                    return None, f"Estoque insuficiente para {produto['nome']}"
                produtos_cache[item["produto_id"]] = produto
                total += produto["preco"] * item["quantidade"]

            cursor.execute(
                "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
                (usuario_id, total),
            )
            pedido_id = cursor.lastrowid

            for item in itens:
                produto = produtos_cache[item["produto_id"]]
                cursor.execute(
                    """
                    INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)
                    VALUES (?, ?, ?, ?)
                    """,
                    (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
                )
                cursor.execute(
                    "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                    (item["quantidade"], item["produto_id"]),
                )

            connection.commit()
            return {"pedido_id": pedido_id, "total": total}, None
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()

    @classmethod
    def _montar_pedidos(cls, rows):
        if not rows:
            return []

        pedidos = {}
        for row in rows:
            pedido_id = row["id"]
            if pedido_id not in pedidos:
                pedidos[pedido_id] = {
                    "id": row["id"],
                    "usuario_id": row["usuario_id"],
                    "status": row["status"],
                    "total": row["total"],
                    "criado_em": row["criado_em"],
                    "itens": [],
                }
            if row["item_id"] is not None:
                pedidos[pedido_id]["itens"].append(
                    {
                        "produto_id": row["produto_id"],
                        "produto_nome": row["produto_nome"] or "Desconhecido",
                        "quantidade": row["quantidade"],
                        "preco_unitario": row["preco_unitario"],
                    }
                )
        return list(pedidos.values())

    @classmethod
    def listar_por_usuario(cls, usuario_id):
        with db_cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    p.id, p.usuario_id, p.status, p.total, p.criado_em,
                    i.id AS item_id, i.produto_id, i.quantidade, i.preco_unitario,
                    pr.nome AS produto_nome
                FROM pedidos p
                LEFT JOIN itens_pedido i ON i.pedido_id = p.id
                LEFT JOIN produtos pr ON pr.id = i.produto_id
                WHERE p.usuario_id = ?
                ORDER BY p.id, i.id
                """,
                (usuario_id,),
            )
            return cls._montar_pedidos(cursor.fetchall())

    @classmethod
    def listar_todos(cls):
        with db_cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    p.id, p.usuario_id, p.status, p.total, p.criado_em,
                    i.id AS item_id, i.produto_id, i.quantidade, i.preco_unitario,
                    pr.nome AS produto_nome
                FROM pedidos p
                LEFT JOIN itens_pedido i ON i.pedido_id = p.id
                LEFT JOIN produtos pr ON pr.id = i.produto_id
                ORDER BY p.id, i.id
                """
            )
            return cls._montar_pedidos(cursor.fetchall())

    @classmethod
    def atualizar_status(cls, pedido_id, novo_status):
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT status FROM pedidos WHERE id = ?", (pedido_id,))
            row = cursor.fetchone()
            if not row:
                return False

            status_anterior = row["status"]
            cursor.execute(
                "UPDATE pedidos SET status = ? WHERE id = ?",
                (novo_status, pedido_id),
            )

            if novo_status == "cancelado" and status_anterior != "cancelado":
                cursor.execute(
                    """
                    SELECT produto_id, quantidade
                    FROM itens_pedido
                    WHERE pedido_id = ?
                    """,
                    (pedido_id,),
                )
                for item in cursor.fetchall():
                    cursor.execute(
                        "UPDATE produtos SET estoque = estoque + ? WHERE id = ?",
                        (item["quantidade"], item["produto_id"]),
                    )

            connection.commit()
            return True
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()

    @classmethod
    def relatorio_vendas(cls):
        with db_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM pedidos")
            total_pedidos = cursor.fetchone()[0]

            cursor.execute("SELECT COALESCE(SUM(total), 0) FROM pedidos")
            faturamento = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'")
            pendentes = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'")
            aprovados = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'")
            cancelados = cursor.fetchone()[0]

        desconto = cls._calcular_desconto(faturamento)
        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": round(faturamento, 2),
            "desconto_aplicavel": round(desconto, 2),
            "faturamento_liquido": round(faturamento - desconto, 2),
            "pedidos_pendentes": pendentes,
            "pedidos_aprovados": aprovados,
            "pedidos_cancelados": cancelados,
            "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
        }

    @classmethod
    def contagens_health(cls):
        with db_cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.execute("SELECT COUNT(*) FROM produtos")
            produtos = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            usuarios = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM pedidos")
            pedidos = cursor.fetchone()[0]
        return {"produtos": produtos, "usuarios": usuarios, "pedidos": pedidos}
