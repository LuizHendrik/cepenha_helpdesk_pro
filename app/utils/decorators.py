from functools import wraps
from flask import redirect, url_for, flash, abort
from flask_login import current_user

def login_required_custom(f):
    """Decorator customizado para verificar login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Você precisa fazer login para continuar.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator para verificar se é administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Você precisa fazer login para continuar.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin():
            flash('Você não tem permissão para acessar esta área.', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def tech_required(f):
    """Decorator para verificar se é técnico ou admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Você precisa fazer login para continuar.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not (current_user.is_tech() or current_user.is_admin()):
            flash('Você não tem permissão para acessar esta área.', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function
