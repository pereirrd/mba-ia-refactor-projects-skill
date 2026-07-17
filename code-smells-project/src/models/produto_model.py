from src.models.database import db_cursor, row_to_dict


class ProdutoModel:
    @staticmethod
    def _serialize(row):
        data = row_to_dict(row)
        if not data:
            return None
        return {
            "id": data["id"],
            "nome": data["nome"],
            "descricao": data["descricao"],
            "preco": data["preco"],
            "estoque": data["estoque"],
            "categoria": data["categoria"],
            "ativo": data["ativo"],
            "criado_em": data["criado_em"],
        }

    @classmethod
    def listar_todos(cls):
        with db_cursor() as cursor:
            cursor.execute("SELECT * FROM produtos ORDER BY id")
            return [cls._serialize(row) for row in cursor.fetchall()]

    @classmethod
    def buscar_por_id(cls, produto_id):
        with db_cursor() as cursor:
            cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
            return cls._serialize(cursor.fetchone())

    @classmethod
    def criar(cls, nome, descricao, preco, estoque, categoria):
        with db_cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO produtos (nome, descricao, preco, estoque, categoria)
                VALUES (?, ?, ?, ?, ?)
                """,
                (nome, descricao, preco, estoque, categoria),
            )
            return cursor.lastrowid

    @classmethod
    def atualizar(cls, produto_id, nome, descricao, preco, estoque, categoria):
        with db_cursor(commit=True) as cursor:
            cursor.execute(
                """
                UPDATE produtos
                SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ?
                WHERE id = ?
                """,
                (nome, descricao, preco, estoque, categoria, produto_id),
            )
            return cursor.rowcount > 0

    @classmethod
    def deletar(cls, produto_id):
        with db_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
            return cursor.rowcount > 0

    @classmethod
    def buscar(cls, termo, categoria=None, preco_min=None, preco_max=None):
        query = "SELECT * FROM produtos WHERE 1=1"
        params = []

        if termo:
            query += " AND (nome LIKE ? OR descricao LIKE ?)"
            like = f"%{termo}%"
            params.extend([like, like])
        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)
        if preco_min is not None:
            query += " AND preco >= ?"
            params.append(preco_min)
        if preco_max is not None:
            query += " AND preco <= ?"
            params.append(preco_max)

        with db_cursor() as cursor:
            cursor.execute(query, params)
            return [cls._serialize(row) for row in cursor.fetchall()]
