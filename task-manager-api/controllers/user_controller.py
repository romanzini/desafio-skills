from flask import request, jsonify
from database import db
from models.user import User
from models.task import Task
from datetime import datetime
import re
import os
from itsdangerous import URLSafeTimedSerializer


def _generate_token(user_id):
    secret = os.getenv('SECRET_KEY', 'dev-key-CHANGE-IN-PRODUCTION')
    s = URLSafeTimedSerializer(secret)
    return s.dumps(str(user_id), salt='auth-token')


def get_users():
    users = User.query.all()
    result = [
        {**u.to_dict(), 'task_count': len(u.tasks)}
        for u in users
    ]
    return jsonify(result), 200


def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'Usuario nao encontrado'}), 404
    data = user.to_dict()
    data['tasks'] = [t.to_dict() for t in Task.query.filter_by(user_id=user_id).all()]
    return jsonify(data), 200


def create_user():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados invalidos'}), 400

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')

    if not name:
        return jsonify({'error': 'Nome e obrigatorio'}), 400
    if not email:
        return jsonify({'error': 'Email e obrigatorio'}), 400
    if not password:
        return jsonify({'error': 'Senha e obrigatoria'}), 400
    if not re.match(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$', email):
        return jsonify({'error': 'Email invalido'}), 400
    if len(password) < 4:
        return jsonify({'error': 'Senha deve ter no minimo 4 caracteres'}), 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({'error': 'Email ja cadastrado'}), 409

    if role not in ['user', 'admin', 'manager']:
        return jsonify({'error': 'Role invalido'}), 400

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao criar usuario'}), 500


def update_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'Usuario nao encontrado'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados invalidos'}), 400

    if 'name' in data:
        user.name = data['name']

    if 'email' in data:
        if not re.match(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$', data['email']):
            return jsonify({'error': 'Email invalido'}), 400
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            return jsonify({'error': 'Email ja cadastrado'}), 409
        user.email = data['email']

    if 'password' in data:
        if len(data['password']) < 4:
            return jsonify({'error': 'Senha muito curta'}), 400
        user.set_password(data['password'])

    if 'role' in data:
        if data['role'] not in ['user', 'admin', 'manager']:
            return jsonify({'error': 'Role invalido'}), 400
        user.role = data['role']

    if 'active' in data:
        user.active = data['active']

    try:
        db.session.commit()
        return jsonify(user.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar'}), 500


def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'Usuario nao encontrado'}), 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    for t in tasks:
        db.session.delete(t)

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'Usuario deletado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao deletar'}), 500


def get_user_tasks(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'Usuario nao encontrado'}), 404
    tasks = Task.query.filter_by(user_id=user_id).all()
    result = [
        {**{'id': t.id, 'title': t.title, 'description': t.description,
            'status': t.status, 'priority': t.priority,
            'created_at': str(t.created_at),
            'due_date': str(t.due_date) if t.due_date else None},
         'overdue': t.is_overdue()}
        for t in tasks
    ]
    return jsonify(result), 200


def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados invalidos'}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email e senha sao obrigatorios'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Credenciais invalidas'}), 401

    if not user.active:
        return jsonify({'error': 'Usuario inativo'}), 403

    token = _generate_token(user.id)
    return jsonify({
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': token
    }), 200
