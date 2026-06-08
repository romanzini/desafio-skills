from flask import request, jsonify
from database import db
from models.task import Task
from models.user import User
from models.category import Category
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload
from utils.helpers import format_date, calculate_percentage


def summary_report():
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()

    priority_counts = {i: Task.query.filter_by(priority=i).count() for i in range(1, 6)}

    all_tasks = Task.query.all()
    overdue_list = []
    for t in all_tasks:
        if t.is_overdue():
            overdue_list.append({
                'id': t.id,
                'title': t.title,
                'due_date': str(t.due_date),
                'days_overdue': (datetime.utcnow() - t.due_date).days
            })

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(
        Task.status == 'done',
        Task.updated_at >= seven_days_ago
    ).count()

    # Fix N+1: use joinedload to fetch all users with their tasks in 2 queries instead of N+1
    users = User.query.options(joinedload(User.tasks)).all()
    user_stats = []
    for u in users:
        total = len(u.tasks)
        completed = sum(1 for t in u.tasks if t.status == 'done')
        user_stats.append({
            'user_id': u.id,
            'user_name': u.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0
        })

    report = {
        'generated_at': str(datetime.utcnow()),
        'overview': {
            'total_tasks': total_tasks,
            'total_users': total_users,
            'total_categories': total_categories,
        },
        'tasks_by_status': {
            'pending': pending,
            'in_progress': in_progress,
            'done': done,
            'cancelled': cancelled,
        },
        'tasks_by_priority': {
            'critical': priority_counts[1],
            'high': priority_counts[2],
            'medium': priority_counts[3],
            'low': priority_counts[4],
            'minimal': priority_counts[5],
        },
        'overdue': {
            'count': len(overdue_list),
            'tasks': overdue_list,
        },
        'recent_activity': {
            'tasks_created_last_7_days': recent_tasks,
            'tasks_completed_last_7_days': recent_done,
        },
        'user_productivity': user_stats,
    }

    return jsonify(report), 200


def user_report(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'Usuario nao encontrado'}), 404

    tasks = Task.query.filter_by(user_id=user_id).all()

    stats = {s: 0 for s in ['done', 'pending', 'in_progress', 'cancelled']}
    overdue = 0
    high_priority = 0

    for t in tasks:
        if t.status in stats:
            stats[t.status] += 1
        if t.priority <= 2:
            high_priority += 1
        if t.is_overdue():
            overdue += 1

    total = len(tasks)
    report = {
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'statistics': {
            'total_tasks': total,
            **stats,
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': round((stats['done'] / total) * 100, 2) if total > 0 else 0
        }
    }
    return jsonify(report), 200


def get_categories():
    categories = Category.query.all()
    result = []
    for c in categories:
        cat_data = c.to_dict()
        cat_data['task_count'] = Task.query.filter_by(category_id=c.id).count()
        result.append(cat_data)
    return jsonify(result), 200


def create_category():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados invalidos'}), 400

    name = data.get('name')
    if not name:
        return jsonify({'error': 'Nome e obrigatorio'}), 400

    category = Category()
    category.name = name
    category.description = data.get('description', '')
    category.color = data.get('color', '#000000')

    try:
        db.session.add(category)
        db.session.commit()
        return jsonify(category.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao criar categoria'}), 500


def update_category(cat_id):
    cat = db.session.get(Category, cat_id)
    if not cat:
        return jsonify({'error': 'Categoria nao encontrada'}), 404

    data = request.get_json()
    if 'name' in data:
        cat.name = data['name']
    if 'description' in data:
        cat.description = data['description']
    if 'color' in data:
        cat.color = data['color']

    try:
        db.session.commit()
        return jsonify(cat.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar'}), 500


def delete_category(cat_id):
    cat = db.session.get(Category, cat_id)
    if not cat:
        return jsonify({'error': 'Categoria nao encontrada'}), 404

    try:
        db.session.delete(cat)
        db.session.commit()
        return jsonify({'message': 'Categoria deletada'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao deletar'}), 500
