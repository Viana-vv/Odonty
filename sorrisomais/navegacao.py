"""Regras de apresentação do menu; a autorização final continua no Xano."""

AREAS = (
    ("inicio", "Visão geral", {"administrador", "recepcionista", "profissional"}, True),
    ("agenda", "Agenda", {"administrador", "recepcionista", "profissional"}, False),
    ("pacientes", "Pacientes", {"administrador", "recepcionista"}, False),
    ("profissionais", "Profissionais", {"administrador", "recepcionista"}, False),
    ("prontuarios", "Prontuários", {"profissional"}, False),
    ("procedimentos", "Procedimentos", {"administrador"}, False),
)

# No modo conectado, só as rotas com operações existentes são interativas.
AREAS_XANO_DISPONIVEIS = {"inicio"}


def areas_visiveis(perfis, modo_demonstracao=False, cadastro_paciente_habilitado=True):
    perfis = set(perfis)
    areas = []
    for chave, rotulo, permitidos, _ in AREAS:
        if not perfis.intersection(permitidos):
            continue
        if chave == "pacientes" and not cadastro_paciente_habilitado:
            continue
        disponivel = modo_demonstracao or chave in AREAS_XANO_DISPONIVEIS
        areas.append({"chave": chave, "rotulo": rotulo, "disponivel": disponivel})
    return areas


def pode_acessar(perfis, area):
    return any(chave == area and set(perfis).intersection(permitidos)
               for chave, _, permitidos, _ in AREAS)
