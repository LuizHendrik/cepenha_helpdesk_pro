from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # user, tech, admin
    status = db.Column(db.String(20), default='ativo')  # ativo, inativo
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    chamados = db.relationship('Chamado', backref='criador', lazy=True, foreign_keys='Chamado.criador_id')
    atribuidos = db.relationship('Chamado', backref='tecnico', lazy=True, foreign_keys='Chamado.tecnico_id')
    interacoes = db.relationship('Interacao', backref='autor', lazy=True)
    
    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_tech(self):
        return self.role in ['tech', 'admin']
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'role': self.role,
            'status': self.status
        }

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    
    chamados = db.relationship('Chamado', backref='categoria', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao
        }

class Prioridade(db.Model):
    __tablename__ = 'prioridades'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False, unique=True)
    nivel = db.Column(db.Integer, nullable=False)
    cor = db.Column(db.String(7), default='#999999')
    tempo_sla = db.Column(db.Integer)  # em horas
    
    chamados = db.relationship('Chamado', backref='prioridade', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'nivel': self.nivel,
            'cor': self.cor,
            'tempo_sla': self.tempo_sla
        }

class Chamado(db.Model):
    __tablename__ = 'chamados'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='aberto')  # aberto, em_andamento, resolvido, fechado
    prioridade_id = db.Column(db.Integer, db.ForeignKey('prioridades.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    criador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tecnico_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolvido_em = db.Column(db.DateTime)
    solucao = db.Column(db.Text)
    
    interacoes = db.relationship('Interacao', backref='chamado', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'status': self.status,
            'prioridade': self.prioridade.nome if self.prioridade else None,
            'categoria': self.categoria.nome if self.categoria else None,
            'criador': self.criador.nome if self.criador else None,
            'tecnico': self.tecnico.nome if self.tecnico else None,
            'criado_em': self.criado_em.isoformat(),
        }

class Interacao(db.Model):
    __tablename__ = 'interacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    chamado_id = db.Column(db.Integer, db.ForeignKey('chamados.id'), nullable=False)
    autor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(20), default='comentario')  # comentario, interno, sistema
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'autor': self.autor.nome if self.autor else None,
            'mensagem': self.mensagem,
            'tipo': self.tipo,
            'criado_em': self.criado_em.isoformat(),
        }
