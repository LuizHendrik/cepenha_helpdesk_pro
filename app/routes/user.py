from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Chamado, Interacao, Categoria, Prioridade, StatusChamadoEnum
from app.utils import login_required_custom, get_pagination
from datetime import datetime
from config import TICKETS_PER_PAGE

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required_custom
def dashboard():
    """Dashboard do usuário"""
    page = request.args.get('page', 1, type=int)
    
    query = Chamado.query.filter_by(criador_id=current_user.id).order_by(Chamado.data_criacao.desc())
    paginated = get_pagination(query, page, TICKETS_PER_PAGE)
    
    stats = {
        'total': Chamado.query.filter_by(criador_id=current_user.id).count(),
        'abertos': Chamado.query.filter_by(criador_id=current_user.id, status=StatusChamadoEnum.ABERTO.value).count(),
        'em_andamento': Chamado.query.filter_by(criador_id=current_user.id, status=StatusChamadoEnum.EM_ANDAMENTO.value).count(),
        'resolvidos': Chamado.query.filter_by(criador_id=current_user.id, status=StatusChamadoEnum.RESOLVIDO.value).count(),
    }
    
    return render_template('user/dashboard.html', 
                         chamados=paginated.items,
                         pagination=paginated,
                         stats=stats)

@user_bp.route('/novo-chamado', methods=['GET', 'POST'])
@login_required_custom
def novo_chamado():
    """Criar novo chamado"""
    categorias = Categoria.query.filter_by(ativo=True).all()
    prioridades = Prioridade.query.all()
    
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        descricao = request.form.get('descricao', '').strip()
        categoria_id = request.form.get('categoria_id', type=int)
        prioridade_id = request.form.get('prioridade_id', type=int)
        local = request.form.get('local', '').strip()
        equipamento = request.form.get('equipamento', '').strip()
        
        if not all([titulo, descricao, categoria_id, prioridade_id]):
            flash('Todos os campos obrigatórios devem ser preenchidos.', 'danger')
            return redirect(url_for('user.novo_chamado'))
        
        if len(titulo) > 255:
            flash('O título não pode ter mais de 255 caracteres.', 'danger')
            return redirect(url_for('user.novo_chamado'))
        
        from app.utils import gerar_numero_chamado
        chamado = Chamado(
            numero=gerar_numero_chamado(),
            titulo=titulo,
            descricao=descricao,
            criador_id=current_user.id,
            categoria_id=categoria_id,
            prioridade_id=prioridade_id,
            local=local,
            equipamento=equipamento,
            status=StatusChamadoEnum.ABERTO.value
        )
        
        db.session.add(chamado)
        db.session.flush()
        
        interacao = Interacao(
            chamado_id=chamado.id,
            autor_id=current_user.id,
            conteudo=descricao,
            tipo='comentario',
            eh_publica=True
        )
        
        db.session.add(interacao)
        db.session.commit()
        
        flash(f'Chamado {chamado.numero} criado com sucesso!', 'success')
        return redirect(url_for('user.ver_chamado', chamado_id=chamado.id))
    
    return render_template('user/novo_chamado.html', 
                         categorias=categorias,
                         prioridades=prioridades)

@user_bp.route('/chamado/<int:chamado_id>')
@login_required_custom
def ver_chamado(chamado_id):
    """Ver detalhes do chamado"""
    chamado = Chamado.query.get_or_404(chamado_id)
    
    if chamado.criador_id != current_user.id and not current_user.is_admin():
        flash('Você não tem permissão para visualizar este chamado.', 'danger')
        return redirect(url_for('user.dashboard'))
    
    interacoes = Interacao.query.filter_by(chamado_id=chamado_id).order_by(Interacao.data_criacao.asc()).all()
    
    return render_template('user/detalhes_chamado.html', 
                         chamado=chamado,
                         interacoes=interacoes)

@user_bp.route('/chamado/<int:chamado_id>/comentario', methods=['POST'])
@login_required_custom
def adicionar_comentario(chamado_id):
    """Adicionar comentário a um chamado"""
    chamado = Chamado.query.get_or_404(chamado_id)
    
    if chamado.criador_id != current_user.id and not current_user.is_admin():
        flash('Você não tem permissão para comentar neste chamado.', 'danger')
        return redirect(url_for('user.dashboard'))
    
    conteudo = request.form.get('conteudo', '').strip()
    
    if not conteudo:
        flash('O comentário não pode estar vazio.', 'danger')
        return redirect(url_for('user.ver_chamado', chamado_id=chamado_id))
    
    interacao = Interacao(
        chamado_id=chamado_id,
        autor_id=current_user.id,
        conteudo=conteudo,
        tipo='comentario',
        eh_publica=True
    )
    
    chamado.data_atualizacao = datetime.utcnow()
    db.session.add(interacao)
    db.session.commit()
    
    flash('Comentário adicionado com sucesso!', 'success')
    return redirect(url_for('user.ver_chamado', chamado_id=chamado_id))

@user_bp.route('/chamado/<int:chamado_id>/reabrir', methods=['POST'])
@login_required_custom
def reabrir_chamado(chamado_id):
    """Reabrir um chamado"""
    chamado = Chamado.query.get_or_404(chamado_id)
    
    if chamado.criador_id != current_user.id and not current_user.is_admin():
        flash('Você não tem permissão para reabrir este chamado.', 'danger')
        return redirect(url_for('user.dashboard'))
    
    if chamado.status not in [StatusChamadoEnum.RESOLVIDO.value, StatusChamadoEnum.FECHADO.value]:
        flash('Apenas chamados resolvidos ou fechados podem ser reabiertos.', 'danger')
        return redirect(url_for('user.ver_chamado', chamado_id=chamado_id))
    
    chamado.reabrir()
    
    interacao = Interacao(
        chamado_id=chamado_id,
        autor_id=current_user.id,
        conteudo='Chamado reabierto pelo usuário',
        tipo='mudanca_status',
        eh_publica=True
    )
    db.session.add(interacao)
    db.session.commit()
    
    flash('Chamado reabierto com sucesso!', 'success')
    return redirect(url_for('user.ver_chamado', chamado_id=chamado_id))

@user_bp.route('/meu-perfil')
@login_required_custom
def meu_perfil():
    """Perfil do usuário"""
    return render_template('user/perfil.html', usuario=current_user)

@user_bp.route('/meu-perfil/atualizar', methods=['POST'])
@login_required_custom
def atualizar_perfil():
    """Atualizar dados do perfil"""
    nome = request.form.get('nome', '').strip()
    telefone = request.form.get('telefone', '').strip()
    departamento = request.form.get('departamento', '').strip()
    
    if not nome:
        flash('O nome é obrigatório.', 'danger')
        return redirect(url_for('user.meu_perfil'))
    
    current_user.nome = nome
    current_user.telefone = telefone
    current_user.departamento = departamento
    current_user.data_atualizacao = datetime.utcnow()
    
    db.session.commit()
    flash('Perfil atualizado com sucesso!', 'success')
    return redirect(url_for('user.meu_perfil'))
