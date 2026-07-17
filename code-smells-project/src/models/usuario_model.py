from werkzeug.security import check_password_hash, generate_password_hash

from src.models.database import db_cursor, row_to_dict


class UsuarioModel:
    @staticmethod
    def _serialize(row, include_sensitive=False):
        data = row_to_dict(row)
        if not data:
            return None
        result = {
            "id": data["id"],
            "nome": data["nome"],
            "email": data["email"],
            "tipo": data["tipo"],
            "criado_em": data["criado_em"],
        }
        if include_sensitive:
            result["senha"] = data["senha"]
        return result

    @classmethod
    def listar_todos(cls):
        with db_cursor() as cursor:
            cursor.execute("SELECT * FROM usuarios ORDER BY id")
            return [cls._serialize(row) for row in cursor.fetchall()]

    @classmethod
    def buscar_por_id(cls, usuario_id):
        with db_cursor() as cursor:
            cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
            return cls._serialize(cursor.fetchone())

    @classmethod
    def criar(cls, nome, email, senha, tipo="cliente"):
        with db_cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO usuarios (nome, email, senha, tipo)
                VALUES (?, ?, ?, ?)
                """,
                (nome, email, generate_password_hash(senha), tipo),
            )
            return cursor.lastrowid

    @classmethod
    def autenticar(cls, email, senha):
        with db_cursor() as cursor:
            cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
            row = cursor.fetchone()
        if not row:
            return None
        if not check_password_hash(row["senha"], senha):
            return None
        return {
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "tipo": row["tipo"],
        }
