#!/usr/bin/env python
"""Entry point da aplicação Cepenha Helpdesk Pro"""

import os
import sys
import click
from app import create_app, db
from app.models import Usuario, Categoria, Prioridade

app = create_app(os.environ.get('FLASK_ENV', 'development'))

@app.cli.command()
def init_db():
    """Inicializa o banco de dados"""
    click.echo('Criando tabelas...')
    db.create_all()
    
    if Prioridade.query.count() == 0:
        prioridades = [
            Prioridade(nome='Baixa', nivel=1, cor='#28a745', tempo_sla=168),
            Prioridade(nome='Média', nivel=2, cor='#ffc107', tempo_sla=72),
            Prioridade(nome='Alta', nivel=3, cor='#fd7e14', tempo_sla=24),
            Prioridade(nome='Crítica', nivel=4, cor='#dc3545', tempo_sla=4),
        ]
        for p in prioridades:
            db.session.add(p)
        db.session.commit()
    
    if Categoria.query.count() == 0:
        categorias = [
            Categoria(nome='Hardware'),
            Categoria(nome='Software'),
            Categoria(nome='Rede'),
            Categoria(nome='Email'),
        ]
        for c in categorias:
            db.session.add(c)
        db.session.commit()
    
    click.echo('✓ Banco de dados inicializado!')

@app.cli.command()
@click.option('--email', prompt='Email')
@click.option('--nome', prompt='Nome')
@click.password_option()
def create_admin(email, nome, password):
    """Cria administrador"""
    admin = Usuario(nome=nome, email=email, role='admin', status='ativo')
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    click.echo(f'✓ Admin criado: {email}')

if __name__ == '__main__':
    if len(sys.argv) == 1:
        app.run(host='0.0.0.0', port=5000)
    else:
        app.cli()
