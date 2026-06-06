from app import db
from datetime import datetime

class Prioridade(db.Model):
    """Modelo de prioridades de chamados"""
    
    __tablename__ = 'prioridades'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)  # Baixa, Média, Alta, Crítica
    nivel = db.Column(db.Integer, nullable=False)  # 1, 2, 3, 4
    descricao = db.Column(db.Text)
    cor = db.Column(db.String(7), default='#808080')  # Cor para UI
    tempo_sla = db.Column(db.Integer)  # Tempo em horas para resolução
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    chamados = db.relationship('Chamado', back_populates='prioridade')
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'nivel': self.nivel,
            'descricao': self.descricao,
            'cor': self.cor,
            'tempo_sla': self.tempo_sla,
        }
    
    def __repr__(self):
        return f'<Prioridade {self.nome}>'
