from flask import request, jsonify
from models.produto_model import ProdutoModel

CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]


def listar_produtos():
    produtos = ProdutoModel.get_all()
    return jsonify({"dados": produtos, "sucesso": True}), 200


def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria") or None
    preco_min = request.args.get("preco_min")
    preco_max = request.args.get("preco_max")
    if preco_min:
        preco_min = float(preco_min)
    if preco_max:
        preco_max = float(preco_max)
    resultados = ProdutoModel.search(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200


def buscar_produto(id):
    produto = ProdutoModel.get_by_id(id)
    if not produto:
        return jsonify({"erro": "Produto nao encontrado", "sucesso": False}), 404
    return jsonify({"dados": produto, "sucesso": True}), 200


def criar_produto():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados invalidos"}), 400

    nome = dados.get("nome", "")
    preco = dados.get("preco")
    estoque = dados.get("estoque")

    if not nome:
        return jsonify({"erro": "Nome e obrigatorio"}), 400
    if preco is None:
        return jsonify({"erro": "Preco e obrigatorio"}), 400
    if estoque is None:
        return jsonify({"erro": "Estoque e obrigatorio"}), 400
    if preco < 0:
        return jsonify({"erro": "Preco nao pode ser negativo"}), 400
    if estoque < 0:
        return jsonify({"erro": "Estoque nao pode ser negativo"}), 400
    if len(nome) < 2:
        return jsonify({"erro": "Nome muito curto"}), 400
    if len(nome) > 200:
        return jsonify({"erro": "Nome muito longo"}), 400

    categoria = dados.get("categoria", "geral")
    if categoria not in CATEGORIAS_VALIDAS:
        return jsonify({"erro": f"Categoria invalida. Validas: {CATEGORIAS_VALIDAS}"}), 400

    descricao = dados.get("descricao", "")
    produto_id = ProdutoModel.create(nome, descricao, preco, estoque, categoria)
    return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar_produto(id):
    produto_existente = ProdutoModel.get_by_id(id)
    if not produto_existente:
        return jsonify({"erro": "Produto nao encontrado"}), 404

    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados invalidos"}), 400

    nome = dados.get("nome", "")
    preco = dados.get("preco")
    estoque = dados.get("estoque")

    if not nome:
        return jsonify({"erro": "Nome e obrigatorio"}), 400
    if preco is None:
        return jsonify({"erro": "Preco e obrigatorio"}), 400
    if estoque is None:
        return jsonify({"erro": "Estoque e obrigatorio"}), 400
    if preco < 0:
        return jsonify({"erro": "Preco nao pode ser negativo"}), 400
    if estoque < 0:
        return jsonify({"erro": "Estoque nao pode ser negativo"}), 400

    descricao = dados.get("descricao", "")
    categoria = dados.get("categoria", "geral")
    ProdutoModel.update(id, nome, descricao, preco, estoque, categoria)
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar_produto(id):
    produto = ProdutoModel.get_by_id(id)
    if not produto:
        return jsonify({"erro": "Produto nao encontrado"}), 404
    ProdutoModel.delete(id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
