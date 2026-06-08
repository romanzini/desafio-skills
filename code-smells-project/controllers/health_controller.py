from flask import jsonify
from database import get_db
from datetime import datetime


def health_check():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT 1")
    cursor.execute("SELECT COUNT(*) FROM produtos")
    produtos = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    usuarios = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pedidos")
    pedidos = cursor.fetchone()[0]

    return jsonify({
        "status": "ok",
        "database": "connected",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "counts": {
            "produtos": produtos,
            "usuarios": usuarios,
            "pedidos": pedidos
        }
    }), 200
