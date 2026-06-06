from datetime import datetime
import pytz
from config import ALLOWED_EXTENSIONS
import uuid
import re

def get_pagination(query, page, per_page=10):
    """Retorna paginação de uma query"""
    return query.paginate(page=page, per_page=per_page, error_out=False)

def format_datetime(dt, formato='%d/%m/%Y %H:%M:%S', timezone='America/Sao_Paulo'):
    """Formata datetime para string"""
    if not dt:
        return ''
    
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    
    tz = pytz.timezone(timezone)
    dt_local = dt.astimezone(tz)
    
    return dt_local.strftime(formato)

def gerar_numero_chamado():
    """Gera número único para chamado"""
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    random_suffix = str(uuid.uuid4().hex[:4]).upper()
    return f'TICKET-{timestamp}-{random_suffix}'

def allowed_file(filename):
    """Verifica se o arquivo é permitido"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def sanitize_filename(filename):
    """Sanitiza o nome do arquivo"""
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    filename = re.sub(r'_+', '_', filename)
    return filename

def get_client_ip(request):
    """Obtém o IP real do cliente"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr

def calcular_tempo_sla(data_criacao, tempo_sla_horas):
    """Calcula o status de SLA"""
    agora = datetime.utcnow()
    delta = agora - data_criacao
    horas_passadas = delta.total_seconds() / 3600
    
    if horas_passadas >= tempo_sla_horas:
        return 'vencido'
    elif horas_passadas >= (tempo_sla_horas * 0.8):
        return 'critico'
    elif horas_passadas >= (tempo_sla_horas * 0.5):
        return 'atencao'
    else:
        return 'ok'

def truncate_text(text, length=100):
    """Trunca texto para um tamanho máximo"""
    if len(text) > length:
        return text[:length] + '...'
    return text

def get_status_color(status):
    """Retorna a cor do badge para um status"""
    cores = {
        'aberto': 'info',
        'em_andamento': 'warning',
        'aguardando_usuario': 'secondary',
        'resolvido': 'success',
        'fechado': 'dark',
        'reaberto': 'danger',
    }
    return cores.get(status, 'secondary')

def get_prioridade_color(nivel):
    """Retorna a cor do badge para prioridade"""
    cores = {
        1: 'success',    # Baixa
        2: 'info',       # Média
        3: 'warning',    # Alta
        4: 'danger',     # Crítica
    }
    return cores.get(nivel, 'secondary')
