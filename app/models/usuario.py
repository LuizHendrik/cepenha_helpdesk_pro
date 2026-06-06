from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from enum import Enum

class RoleEnum(Enum):
    """Enumeração de papéis de usuário"""
    USER = 'user'
    TECH = 'tech'
    ADMIN = 'admin'

class StatusEnum(Enum):
    """Enumeração de status do usuário"""
    ATIVO = 'ativo'
    INATIVO = 'inativo'
    SUSPENSO = 'suspenso'

class Usuario(UserMixin, db.Model):
    """Modelo de usuário do sistema"""
    
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    departamento = db.Column(db.String(100))
    telefone = db.Column(db.String(20))
    cargo = db.Column(db.String(100))
    
    # Enums
    role = db.Column(db.String(20), default=RoleEnum.USER.value, nullable=False)
    status = db.Column(db.String(20), default=StatusEnum.ATIVO.value, nullable=False)
    
    # Timestamps
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ultimo_acesso = db.Column(db.DateTime)
    
    # Relacionamentos
    chamados = db.relationship('Chamado', back_populates='criador', foreign_keys='Chamado.criador_id')
    chamados_atendidos = db.relationship('Chamado', back_populates='atendente', foreign_keys='Chamado.atendente_id')
    interacoes = db.relationship('Interacao', back_populates='autor')
    
    def set_password(self, password):
        """Define a senha com hash"""
        self.senha_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, password)
    
    def is_admin(self):
        """Verifica se o usuário é administrador"""
        return self.role == RoleEnum.ADMIN.value
    
    def is_tech(self):
        """Verifica se o usuário é técnico"""
        return self.role == RoleEnum.TECH.value
    
    def is_active_user(self):
        """Verifica se o usuário está ativo"""
        return self.status == StatusEnum.ATIVO.value
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'departamento': self.departamento,
            'cargo': self.cargo,
            'role': self.role,
            'status': self.status,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'ultimo_acesso': self.ultimo_acesso.isoformat() if self.ultimo_acesso else None,
        }
    
    def __repr__(self):
        return f'<Usuario {self.nome} ({self.email})>'
