from app import db
from datetime import datetime

class Categoria(db.Model):
    """Modelo de categorias de chamados"""
    
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    descricao = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    chamados = db.relationship('Chamado', back_populates='categoria')
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'ativo': self.ativo,
        }
    
    def __repr__(self):
        return f'<Categoria {self.nome}>'
