from flask import request, jsonify
from models.usuario_model import UsuarioModel


def listar_usuarios():
    usuarios = UsuarioModel.get_all()
    return jsonify({"dados": usuarios, "sucesso": True}), 200


def buscar_usuario(id):
    usuario = UsuarioModel.get_by_id(id)
    if not usuario:
        return jsonify({"erro": "Usuario nao encontrado"}), 404
    return jsonify({"dados": usuario, "sucesso": True}), 200


def criar_usuario():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados invalidos"}), 400

    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not nome or not email or not senha:
        return jsonify({"erro": "Nome, email e senha sao obrigatorios"}), 400

    usuario_id = UsuarioModel.create(nome, email, senha)
    return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201


def login():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados invalidos"}), 400

    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not email or not senha:
        return jsonify({"erro": "Email e senha sao obrigatorios"}), 400

    usuario = UsuarioModel.authenticate(email, senha)
    if usuario:
        return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
    return jsonify({"erro": "Email ou senha invalidos", "sucesso": False}), 401
