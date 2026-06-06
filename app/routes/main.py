from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página inicial"""
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_tech():
            return redirect(url_for('admin.chamados_tech'))
        else:
            return redirect(url_for('user.dashboard'))
    
    return redirect(url_for('auth.login'))

@main_bp.route('/sobre')
def sobre():
    """Página sobre"""
    return render_template('sobre.html')

@main_bp.route('/contato')
def contato():
    """Página de contato"""
    return render_template('contato.html')
