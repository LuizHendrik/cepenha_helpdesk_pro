from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user
from app import db
from app.models import Usuario
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Rota de login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        lembrar = request.form.get('lembrar') is not None
        
        if not email or not senha:
            flash('Email e senha são obrigatórios.', 'danger')
            return redirect(url_for('auth.login'))
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if not usuario or not usuario.check_password(senha):
            flash('Email ou senha inválidos.', 'danger')
            return redirect(url_for('auth.login'))
        
        if not usuario.is_active_user():
            flash('Sua conta está inativa. Entre em contato com o administrador.', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(usuario, remember=lembrar)
        usuario.ultimo_acesso = datetime.utcnow()
        db.session.commit()
        
        flash(f'Bem-vindo, {usuario.nome}!', 'success')
        
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        
        return redirect(url_for('main.index'))
    
    return render_template('auth/login.html')

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    """Rota de registro de novo usuário"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        confirmar_senha = request.form.get('confirmar_senha', '')
        departamento = request.form.get('departamento', '').strip()
        telefone = request.form.get('telefone', '').strip()
        
        if not all([nome, email, senha, confirmar_senha]):
            flash('Todos os campos obrigatórios devem ser preenchidos.', 'danger')
            return redirect(url_for('auth.registro'))
        
        if len(senha) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'danger')
            return redirect(url_for('auth.registro'))
        
        if senha != confirmar_senha:
            flash('As senhas não coincidem.', 'danger')
            return redirect(url_for('auth.registro'))
        
        if Usuario.query.filter_by(email=email).first():
            flash('Este email já está registrado.', 'danger')
            return redirect(url_for('auth.registro'))
        
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            departamento=departamento,
            telefone=telefone,
            role='user'
        )
        novo_usuario.set_password(senha)
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        flash('Registro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/registro.html')

@auth_bp.route('/logout')
def logout():
    """Rota de logout"""
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/alterar-senha', methods=['GET', 'POST'])
def alterar_senha():
    """Alterar senha do usuário"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        senha_atual = request.form.get('senha_atual', '')
        nova_senha = request.form.get('nova_senha', '')
        confirmar_nova_senha = request.form.get('confirmar_nova_senha', '')
        
        if not current_user.check_password(senha_atual):
            flash('Senha atual inválida.', 'danger')
            return redirect(url_for('auth.alterar_senha'))
        
        if len(nova_senha) < 6:
            flash('A nova senha deve ter pelo menos 6 caracteres.', 'danger')
            return redirect(url_for('auth.alterar_senha'))
        
        if nova_senha != confirmar_nova_senha:
            flash('As senhas não coincidem.', 'danger')
            return redirect(url_for('auth.alterar_senha'))
        
        current_user.set_password(nova_senha)
        db.session.commit()
        
        flash('Senha alterada com sucesso!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('auth/alterar_senha.html')
