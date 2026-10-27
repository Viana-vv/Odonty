"""Cache privado, sob demanda, para respostas GET autenticadas do Xano."""

from hashlib import sha256

_CHAVE_CACHE = "xano_get_cache"
_CHAVE_ESCOPO = "xano_get_escopo"
_DEPENDENCIAS_INVALIDACAO = {
    "profissionais": ("profissionais", "especialidades", "agenda/opcoes", "consultas", "disponibilidades"),
    "disponibilidades": ("disponibilidades", "consultas", "agenda/opcoes"),
    "consultas": ("consultas", "disponibilidades", "agenda/opcoes", "procedimentos-consulta", "exames", "registros-clinicos"),
    "consulta": ("consultas", "disponibilidades", "agenda/opcoes", "procedimentos-consulta", "exames", "registros-clinicos"),
    "pacientes": ("pacientes", "paciente", "agenda/opcoes", "consultas"),
    "registros-clinicos": ("registros-clinicos", "consultas"),
    "exames": ("exames", "registros-clinicos"),
    "procedimentos": ("procedimentos", "agenda/opcoes", "procedimentos-consulta"),
    "prontuario": ("consultas", "registros-clinicos", "exames"),
}


def _limpar(estado):
    estado.pop(_CHAVE_CACHE, None)
    estado.pop(_CHAVE_ESCOPO, None)


def invalidar_cache(state, namespaces=None):
    """Invalida todos os GETs em cache ou apenas namespaces informados."""
    if namespaces is None:
        _limpar(state)
        # Remo??o de caches legados enquanto cada tela passa ao helper comum.
        for chave in (
            "cad_especialidades_cache", "cad_especialidades_cache_em",
            "painel_recepcao_xano_cache", "painel_recepcao_xano_erro_em",
            "painel_administrativo_xano_cache", "painel_administrativo_xano_erro_em",
            "agenda_xano_cache", "agenda_xano_erro_em",
            "agenda_disponibilidades_cache", "agenda_disponibilidades_erro_em",
            "procedimentos_xano_catalogo_cache", "prontuario_historico_cache",
            "profissionais_xano_cache",
        ):
            state.pop(chave, None)
        return
    cache = state.get(_CHAVE_CACHE)
    if not isinstance(cache, dict):
        return
    if isinstance(namespaces, str):
        namespaces = {namespaces}
    else:
        namespaces = set(namespaces)
    namespaces = {dependencia
                  for namespace in namespaces
                  for dependencia in _DEPENDENCIAS_INVALIDACAO.get(namespace, (namespace,))}
    for chave in list(cache):
        namespace_cacheado = chave[1]
        if any(namespace_cacheado == namespace
               or namespace_cacheado.startswith(namespace + ":")
               or namespace_cacheado.startswith(namespace + "/")
               for namespace in namespaces):
            del cache[chave]
    if not cache:
        state.pop(_CHAVE_CACHE, None)


def carregar_cache(state, token, namespace, loader, force=False):
    """Carrega sob demanda e reutiliza somente sucesso na sess?o/Conta atual.

    ``namespace`` deve ser uma chave l?gica completa, incluindo par?metros do
    GET (por exemplo ``consultas:paciente=12``). O token nunca ? persistido.
    """
    if not isinstance(token, str) or not token:
        invalidar_cache(state)
        return loader()
    escopo = sha256(token.encode("utf-8")).hexdigest()
    if state.get(_CHAVE_ESCOPO) != escopo:
        invalidar_cache(state)
        state[_CHAVE_ESCOPO] = escopo
    chave = (escopo, str(namespace))
    cache = state.setdefault(_CHAVE_CACHE, {})
    if not force and chave in cache:
        return cache[chave]
    if force:
        cache.pop(chave, None)
    try:
        resposta = loader()
    except Exception as erro:
        if getattr(erro, "status", None) in (401, 403):
            invalidar_cache(state)
        raise
    cache = state.setdefault(_CHAVE_CACHE, {})
    cache[chave] = resposta
    return resposta
