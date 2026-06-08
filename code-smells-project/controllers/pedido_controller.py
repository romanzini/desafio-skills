from flask import request, jsonify
from models.pedido_model import PedidoModel

STATUS_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]


def criar_pedido():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados invalidos"}), 400

    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        return jsonify({"erro": "Usuario ID e obrigatorio"}), 400
    if not itens:
        return jsonify({"erro": "Pedido deve ter pelo menos 1 item"}), 400

    resultado = PedidoModel.create(usuario_id, itens)
    if "erro" in resultado:
        return jsonify({"erro": resultado["erro"], "sucesso": False}), 400

    return jsonify({
        "dados": resultado,
        "sucesso": True,
        "mensagem": "Pedido criado com sucesso"
    }), 201


def listar_pedidos_usuario(usuario_id):
    pedidos = PedidoModel.get_by_usuario(usuario_id)
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def listar_todos_pedidos():
    pedidos = PedidoModel.get_all()
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def atualizar_status_pedido(pedido_id):
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados invalidos"}), 400

    novo_status = dados.get("status", "")
    if novo_status not in STATUS_VALIDOS:
        return jsonify({"erro": f"Status invalido. Validos: {STATUS_VALIDOS}"}), 400

    PedidoModel.update_status(pedido_id, novo_status)
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
