from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash


class UsuarioModel:

    @staticmethod
    def get_all():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, nome, email, tipo, criado_em FROM usuarios")
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_by_id(usuario_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, nome, email, tipo, criado_em FROM usuarios WHERE id = ?",
            (usuario_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    def create(nome, email, senha, tipo="cliente"):
        db = get_db()
        cursor = db.cursor()
        senha_hash = generate_password_hash(senha)
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, senha_hash, tipo)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def authenticate(email, senha):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, nome, email, tipo, senha FROM usuarios WHERE email = ?",
            (email,)
        )
        row = cursor.fetchone()
        if row and check_password_hash(row["senha"], senha):
            return {
                "id": row["id"],
                "nome": row["nome"],
                "email": row["email"],
                "tipo": row["tipo"]
            }
        return None
