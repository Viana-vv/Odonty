"""Regras de apresentação do menu; a autorização final continua no Xano."""

from importlib import import_module
from importlib.util import find_spec

AREAS = (
    ("inicio", "Visão geral", {"administrador", "recepcionista", "profissional"}, True),
    ("agenda", "Agenda", {"administrador", "recepcionista", "profissional"}, False),
    ("pacientes", "Pacientes", {"administrador", "recepcionista"}, False),
    ("profissionais", "Profissionais", {"administrador", "recepcionista"}, False),
    ("prontuarios", "Prontuários", {"profissional"}, False),
    ("procedimentos", "Procedimentos", {"administrador"}, False),
)

# Cada tela conectada vive em módulo próprio. As ausentes seguem indisponíveis.
MODULOS_XANO = {
    "pacientes": "pagina_pacientes_xano",
    "profissionais": "pagina_profissionais_xano",
    "prontuarios": "pagina_prontuario_xano",
    "procedimentos": "pagina_procedimentos_xano",
    "nova_consulta": "pagina_nova_consulta_xano",
}
AREAS_XANO_BASE_DISPONIVEIS = {"inicio", "agenda"}
PERFIS_NOVA_CONSULTA = {"administrador", "recepcionista"}


def modulo_xano_disponivel(area):
    nome_modulo = MODULOS_XANO.get(area)
    if not nome_modulo:
        return False
    try:
        return find_spec(f"sorrisomais.{nome_modulo}") is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        return False


def carregar_modulo_xano(area):
    """Carrega um módulo conhecido quando já integrado ao projeto."""
    nome_modulo = MODULOS_XANO.get(area)
    if not nome_modulo or not modulo_xano_disponivel(area):
        return None
    try:
        return import_module(f"sorrisomais.{nome_modulo}")
    except ImportError:
        return None


def areas_visiveis(perfis, modo_demonstracao=False, cadastro_paciente_habilitado=True):
    perfis = set(perfis)
    areas = []
    for chave, rotulo, permitidos, _ in AREAS:
        if not perfis.intersection(permitidos):
            continue
        if chave == "pacientes" and not cadastro_paciente_habilitado:
            continue
        disponivel = (modo_demonstracao or chave in AREAS_XANO_BASE_DISPONIVEIS
                      or modulo_xano_disponivel(chave))
        areas.append({"chave": chave, "rotulo": rotulo, "disponivel": disponivel})
    return areas


def pode_acessar(perfis, area):
    if area == "nova_consulta":
        return bool(set(perfis).intersection(PERFIS_NOVA_CONSULTA))
    return any(chave == area and set(perfis).intersection(permitidos)
               for chave, _, permitidos, _ in AREAS)
