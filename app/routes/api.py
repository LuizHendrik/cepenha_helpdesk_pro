from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Chamado, Usuario, Categoria, Prioridade
from app.utils import admin_required

api_bp = Blueprint('api', __name__)

@api_bp.route('/chamados', methods=['GET'])
@login_required
def get_chamados():
    """Listar chamados via API"""
    page = request.args.get('page', 1, type=int)
    query = Chamado.query if current_user.is_admin() else Chamado.query.filter_by(criador_id=current_user.id)
    chamados = query.paginate(page=page, per_page=10)
    
    return jsonify({
        'items': [c.to_dict() for c in chamados.items],
        'total': chamados.total,
        'pages': chamados.pages,
        'current_page': chamados.page
    })

@api_bp.route('/categorias', methods=['GET'])
def get_categorias():
    """Listar categorias"""
    categorias = Categoria.query.filter_by(ativo=True).all()
    return jsonify([c.to_dict() for c in categorias])

@api_bp.route('/prioridades', methods=['GET'])
def get_prioridades():
    """Listar prioridades"""
    prioridades = Prioridade.query.all()
    return jsonify([p.to_dict() for p in prioridades])

@api_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """Obter estatísticas"""
    if current_user.is_admin():
        stats = {
            'total_chamados': Chamado.query.count(),
            'abertos': Chamado.query.filter_by(status='aberto').count(),
            'em_andamento': Chamado.query.filter_by(status='em_andamento').count(),
            'resolvidos': Chamado.query.filter_by(status='resolvido').count(),
        }
    else:
        stats = {
            'total_chamados': Chamado.query.filter_by(criador_id=current_user.id).count(),
            'abertos': Chamado.query.filter_by(criador_id=current_user.id, status='aberto').count(),
        }
    
    return jsonify(stats)
