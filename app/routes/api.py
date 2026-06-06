from flask import Blueprint, jsonify

api_bp = Blueprint('api', __name__)

@api_bp.route('/chamados')
def get_chamados():
    """Retorna lista de chamados"""
    return jsonify({'chamados': []})

@api_bp.route('/status')
def get_status():
    """Retorna status da API"""
    return jsonify({'status': 'ok'})