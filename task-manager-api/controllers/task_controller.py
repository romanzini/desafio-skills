from flask import request, jsonify
from database import db
from models.task import Task
from models.user import User
from models.category import Category
from datetime import datetime
from sqlalchemy.orm import joinedload


def get_tasks():
    try:
        tasks = Task.query.options(
            joinedload(Task.user),
            joinedload(Task.category)
        ).all()
        result = []
        for t in tasks:
            data = t.to_dict()
            data['overdue'] = t.is_overdue()
            data['user_name'] = t.user.name if t.user else None
            data['category_name'] = t.category.name if t.category else None
            result.append(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': 'Erro interno ao listar tasks'}), 500


def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Task nao encontrada'}), 404
    data = task.to_dict()
    data['overdue'] = task.is_overdue()
    return jsonify(data), 200


def create_task():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados invalidos'}), 400

    title = data.get('title')
    if not title:
        return jsonify({'error': 'Titulo e obrigatorio'}), 400
    if len(title) < 3:
        return jsonify({'error': 'Titulo muito curto'}), 400
    if len(title) > 200:
        return jsonify({'error': 'Titulo muito longo'}), 400

    status = data.get('status', 'pending')
    priority = data.get('priority', 3)
    user_id = data.get('user_id')
    category_id = data.get('category_id')
    due_date_str = data.get('due_date')
    tags = data.get('tags')

    if status not in ['pending', 'in_progress', 'done', 'cancelled']:
        return jsonify({'error': 'Status invalido'}), 400
    if priority < 1 or priority > 5:
        return jsonify({'error': 'Prioridade deve ser entre 1 e 5'}), 400

    if user_id:
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'error': 'Usuario nao encontrado'}), 404
    if category_id:
        cat = db.session.get(Category, category_id)
        if not cat:
            return jsonify({'error': 'Categoria nao encontrada'}), 404

    task = Task()
    task.title = title
    task.description = data.get('description', '')
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id

    if due_date_str:
        try:
            task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Formato de data invalido. Use YYYY-MM-DD'}), 400

    if tags:
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    try:
        db.session.add(task)
        db.session.commit()
        return jsonify(task.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao criar task'}), 500


def update_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Task nao encontrada'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados invalidos'}), 400

    if 'title' in data:
        if len(data['title']) < 3:
            return jsonify({'error': 'Titulo muito curto'}), 400
        if len(data['title']) > 200:
            return jsonify({'error': 'Titulo muito longo'}), 400
        task.title = data['title']

    if 'description' in data:
        task.description = data['description']

    if 'status' in data:
        if data['status'] not in ['pending', 'in_progress', 'done', 'cancelled']:
            return jsonify({'error': 'Status invalido'}), 400
        task.status = data['status']

    if 'priority' in data:
        if data['priority'] < 1 or data['priority'] > 5:
            return jsonify({'error': 'Prioridade deve ser entre 1 e 5'}), 400
        task.priority = data['priority']

    if 'user_id' in data:
        if data['user_id']:
            user = db.session.get(User, data['user_id'])
            if not user:
                return jsonify({'error': 'Usuario nao encontrado'}), 404
        task.user_id = data['user_id']

    if 'category_id' in data:
        if data['category_id']:
            cat = db.session.get(Category, data['category_id'])
            if not cat:
                return jsonify({'error': 'Categoria nao encontrada'}), 404
        task.category_id = data['category_id']

    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': 'Formato de data invalido'}), 400
        else:
            task.due_date = None

    if 'tags' in data:
        task.tags = ','.join(data['tags']) if isinstance(data['tags'], list) else data['tags']

    task.updated_at = datetime.utcnow()

    try:
        db.session.commit()
        return jsonify(task.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar'}), 500


def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Task nao encontrada'}), 404
    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deletada com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao deletar'}), 500


def search_tasks():
    query_str = request.args.get('q', '')
    status = request.args.get('status', '')
    priority = request.args.get('priority', '')
    user_id = request.args.get('user_id', '')

    tasks_query = Task.query

    if query_str:
        tasks_query = tasks_query.filter(
            db.or_(
                Task.title.like(f'%{query_str}%'),
                Task.description.like(f'%{query_str}%')
            )
        )
    if status:
        tasks_query = tasks_query.filter(Task.status == status)
    if priority:
        tasks_query = tasks_query.filter(Task.priority == int(priority))
    if user_id:
        tasks_query = tasks_query.filter(Task.user_id == int(user_id))

    results = tasks_query.all()
    return jsonify([t.to_dict() for t in results]), 200


def task_stats():
    total = Task.query.count()
    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()

    all_tasks = Task.query.all()
    overdue_count = sum(1 for t in all_tasks if t.is_overdue())

    return jsonify({
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'done': done,
        'cancelled': cancelled,
        'overdue': overdue_count,
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0
    }), 200
