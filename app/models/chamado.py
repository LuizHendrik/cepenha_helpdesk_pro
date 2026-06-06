from app import db
from datetime import datetime
from enum import Enum

class StatusChamadoEnum(Enum):
    """Enumeração de status de chamados"""
    ABERTO = 'aberto'
    EM_ANDAMENTO = 'em_andamento'
    AGUARDANDO_USUARIO = 'aguardando_usuario'
    RESOLVIDO = 'resolvido'
    FECHADO = 'fechado'
    REABERTO = 'reaberto'

class Chamado(db.Model):
    """Modelo de chamados/tickets do sistema"""
    
    __tablename__ = 'chamados'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True, nullable=False, index=True)
    titulo = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    
    # Foreign keys
    criador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    atendente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    prioridade_id = db.Column(db.Integer, db.ForeignKey('prioridades.id'), nullable=False)
    
    # Status
    status = db.Column(db.String(20), default=StatusChamadoEnum.ABERTO.value, index=True)
    
    # Informações adicionais
    local = db.Column(db.String(100))
    equipamento = db.Column(db.String(150))
    observacoes_internas = db.Column(db.Text)
    
    # Timestamps
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data_atribuicao = db.Column(db.DateTime)
    data_resolucao = db.Column(db.DateTime)
    
    # Avaliação
    nota_satisfacao = db.Column(db.Integer)  # 1-5
    feedback = db.Column(db.Text)
    
    # Relacionamentos
    criador = db.relationship('Usuario', back_populates='chamados', foreign_keys=[criador_id])
    atendente = db.relationship('Usuario', back_populates='chamados_atendidos', foreign_keys=[atendente_id])
    categoria = db.relationship('Categoria', back_populates='chamados')
    prioridade = db.relationship('Prioridade', back_populates='chamados')
    interacoes = db.relationship('Interacao', back_populates='chamado', cascade='all, delete-orphan')
    anexos = db.relationship('Anexo', back_populates='chamado', cascade='all, delete-orphan')
    
    def atribuir_tecnico(self, tecnico):
        """Atribui um técnico ao chamado"""
        self.atendente_id = tecnico.id
        self.data_atribuicao = datetime.utcnow()
        self.status = StatusChamadoEnum.EM_ANDAMENTO.value
        db.session.commit()
    
    def resolver(self):
        """Marca o chamado como resolvido"""
        self.status = StatusChamadoEnum.RESOLVIDO.value
        self.data_resolucao = datetime.utcnow()
        db.session.commit()
    
    def reabrir(self):
        """Reabre um chamado"""
        self.status = StatusChamadoEnum.REABERTO.value
        self.data_resolucao = None
        db.session.commit()
    
    def tempo_aberto(self):
        """Retorna o tempo que o chamado está aberto em horas"""
        from datetime import datetime
        delta = datetime.utcnow() - self.data_criacao
        return delta.total_seconds() / 3600
    
    def tempo_para_sla(self):
        """Retorna o tempo restante para atender ao SLA em horas"""
        if self.prioridade and self.prioridade.tempo_sla:
            return self.prioridade.tempo_sla - self.tempo_aberto()
        return None
    
    def sla_vencido(self):
        """Verifica se o SLA foi vencido"""
        tempo_restante = self.tempo_para_sla()
        return tempo_restante is not None and tempo_restante < 0
    
    def to_dict(self, incluir_interacoes=False):
        """Converte para dicionário"""
        data = {
            'id': self.id,
            'numero': self.numero,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'status': self.status,
            'criador': self.criador.to_dict() if self.criador else None,
            'atendente': self.atendente.to_dict() if self.atendente else None,
            'categoria': self.categoria.to_dict() if self.categoria else None,
            'prioridade': self.prioridade.to_dict() if self.prioridade else None,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            'nota_satisfacao': self.nota_satisfacao,
        }
        
        if incluir_interacoes:
            data['interacoes'] = [i.to_dict() for i in self.interacoes]
        
        return data
    
    def __repr__(self):
        return f'<Chamado {self.numero} - {self.titulo}>'

class Anexo(db.Model):
    """Modelo de anexos de chamados"""
    
    __tablename__ = 'anexos'
    
    id = db.Column(db.Integer, primary_key=True)
    chamado_id = db.Column(db.Integer, db.ForeignKey('chamados.id'), nullable=False)
    nome_arquivo = db.Column(db.String(255), nullable=False)
    caminho_arquivo = db.Column(db.String(500), nullable=False)
    tamanho = db.Column(db.Integer)
    tipo_mime = db.Column(db.String(100))
    data_upload = db.Column(db.DateTime, default=datetime.utcnow)
    
    chamado = db.relationship('Chamado', back_populates='anexos')
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'nome_arquivo': self.nome_arquivo,
            'tamanho': self.tamanho,
            'data_upload': self.data_upload.isoformat() if self.data_upload else None,
        }
