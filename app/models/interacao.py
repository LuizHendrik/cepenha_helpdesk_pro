from app import db
from datetime import datetime

class Interacao(db.Model):
    """Modelo de interações/comentários em chamados"""
    
    __tablename__ = 'interacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    chamado_id = db.Column(db.Integer, db.ForeignKey('chamados.id'), nullable=False)
    autor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    conteudo = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(20), default='comentario')  # comentario, nota_interna, mudanca_status
    
    eh_publica = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    chamado = db.relationship('Chamado', back_populates='interacoes')
    autor = db.relationship('Usuario', back_populates='interacoes')
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'autor': self.autor.to_dict() if self.autor else None,
            'conteudo': self.conteudo,
            'tipo': self.tipo,
            'eh_publica': self.eh_publica,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
        }
    
    def __repr__(self):
        return f'<Interacao {self.id} - Chamado {self.chamado_id}>'
