from flask import jsonify
from models.pedido_model import PedidoModel


def relatorio_vendas():
    relatorio = PedidoModel.relatorio_vendas()
    return jsonify({"dados": relatorio, "sucesso": True}), 200
