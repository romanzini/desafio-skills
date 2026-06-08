from database import get_db

DISCOUNT_THRESHOLDS = [
    (10000, 0.10),
    (5000, 0.05),
    (1000, 0.02),
]


class PedidoModel:

    @staticmethod
    def get_by_usuario(usuario_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
                   ip.produto_id, ip.quantidade, ip.preco_unitario,
                   pr.nome as produto_nome
            FROM pedidos p
            LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
            LEFT JOIN produtos pr ON pr.id = ip.produto_id
            WHERE p.usuario_id = ?
        """, (usuario_id,))
        return PedidoModel._aggregate_rows(cursor.fetchall())

    @staticmethod
    def get_all():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
                   ip.produto_id, ip.quantidade, ip.preco_unitario,
                   pr.nome as produto_nome
            FROM pedidos p
            LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
            LEFT JOIN produtos pr ON pr.id = ip.produto_id
        """)
        return PedidoModel._aggregate_rows(cursor.fetchall())

    @staticmethod
    def _aggregate_rows(rows):
        pedidos = {}
        for row in rows:
            pid = row["id"]
            if pid not in pedidos:
                pedidos[pid] = {
                    "id": row["id"],
                    "usuario_id": row["usuario_id"],
                    "status": row["status"],
                    "total": row["total"],
                    "criado_em": row["criado_em"],
                    "itens": []
                }
            if row["produto_id"]:
                pedidos[pid]["itens"].append({
                    "produto_id": row["produto_id"],
                    "produto_nome": row["produto_nome"] or "Desconhecido",
                    "quantidade": row["quantidade"],
                    "preco_unitario": row["preco_unitario"]
                })
        return list(pedidos.values())

    @staticmethod
    def create(usuario_id, itens):
        db = get_db()
        cursor = db.cursor()

        total = 0
        for item in itens:
            cursor.execute(
                "SELECT id, nome, preco, estoque FROM produtos WHERE id = ?",
                (item["produto_id"],)
            )
            produto = cursor.fetchone()
            if produto is None:
                return {"erro": f"Produto {item['produto_id']} nao encontrado"}
            if produto["estoque"] < item["quantidade"]:
                return {"erro": f"Estoque insuficiente para {produto['nome']}"}
            total += produto["preco"] * item["quantidade"]

        cursor.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total)
        )
        pedido_id = cursor.lastrowid

        for item in itens:
            cursor.execute(
                "SELECT preco FROM produtos WHERE id = ?",
                (item["produto_id"],)
            )
            produto = cursor.fetchone()
            cursor.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], produto["preco"])
            )
            cursor.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"])
            )

        db.commit()
        return {"pedido_id": pedido_id, "total": total}

    @staticmethod
    def update_status(pedido_id, novo_status):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE pedidos SET status = ? WHERE id = ?",
            (novo_status, pedido_id)
        )
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def relatorio_vendas():
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT COUNT(*) as total, COALESCE(SUM(total), 0) as faturamento FROM pedidos"
        )
        row = cursor.fetchone()
        total_pedidos = row["total"]
        faturamento = row["faturamento"]

        cursor.execute("SELECT status, COUNT(*) as count FROM pedidos GROUP BY status")
        status_counts = {r["status"]: r["count"] for r in cursor.fetchall()}

        desconto = 0
        for threshold, rate in DISCOUNT_THRESHOLDS:
            if faturamento > threshold:
                desconto = faturamento * rate
                break

        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": round(faturamento, 2),
            "desconto_aplicavel": round(desconto, 2),
            "faturamento_liquido": round(faturamento - desconto, 2),
            "pedidos_pendentes": status_counts.get("pendente", 0),
            "pedidos_aprovados": status_counts.get("aprovado", 0),
            "pedidos_cancelados": status_counts.get("cancelado", 0),
            "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0
        }
