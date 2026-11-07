"""Invariantes do modelo OFFLINE; não comprovam implementação/transação no Xano."""
import base64
import copy
import hashlib
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import pytest

from backend.contratos.redefinicao_senha import BackendLocalRelogio, ErroContrato


class Relogio:
    def __init__(self):
        self.valor = datetime(2026, 11, 7, 12, tzinfo=timezone.utc)

    def __call__(self):
        return self.valor

    def avancar(self, **delta):
        self.valor += timedelta(**delta)


def uuid7_em(instante, sequencia=1):
    milissegundos = int(instante.timestamp() * 1000)
    return str(uuid.UUID(int=(milissegundos << 80) | (7 << 76) | (2 << 62) | sequencia))


@pytest.fixture
def modelo():
    relogio = Relogio()
    codigos = []

    def emitir():
        codigo = base64.urlsafe_b64encode(len(codigos).to_bytes(32, 'big')).decode().rstrip('=')
        codigos.append(codigo)
        return codigo

    backend = BackendLocalRelogio(relogio, habilitado=True, emitir_token=emitir)
    backend.contas = {
        1: dict(email='admin@example.invalid', situacao='ativo', perfis=['administrador']),
        2: dict(email='titular@example.invalid', situacao='ativo', perfis=['paciente'], senha_hash='hash-anterior-ficticio'),
        3: dict(email='outro@example.invalid', situacao='ativo', perfis=['administrador']),
    }
    for identificador, conta in [('admin', 1), ('titular-1', 2), ('titular-2', 2), ('outro-admin', 3)]:
        backend.sessoes[identificador] = dict(conta_acesso_id=conta, expira_em=relogio() + timedelta(days=40))
    return backend, relogio, codigos


def erro(codigo, status, acao):
    with pytest.raises(ErroContrato) as capturado:
        acao()
    assert (capturado.value.codigo, capturado.value.status) == (codigo, status)
    assert capturado.value.headers['Cache-Control'] == 'no-store'
    return capturado.value


def criar(modelo, conta=2, sequencia=1):
    backend, relogio, _ = modelo
    identificador = uuid7_em(relogio(), sequencia)
    return identificador, backend.criar('admin', conta, identificador)


def snapshot(backend):
    return copy.deepcopy((backend.contas, backend.sessoes, backend.operacoes, backend.auditoria, backend.tentativas))


@pytest.mark.parametrize('metodo', ['criar', 'consultar'])
@pytest.mark.parametrize('mutacao,codigo,status', [
    ('ausente', 'SESSAO_INVALIDA', 401), ('revogada', 'SESSAO_INVALIDA', 401),
    ('expirada', 'SESSAO_INVALIDA', 401), ('versao', 'SESSAO_INVALIDA', 401),
    ('perfil', 'ACESSO_NEGADO', 403), ('inativa', 'ACESSO_NEGADO', 403),
])
def test_autorizacao_revalidada_sem_reserva(modelo, metodo, mutacao, codigo, status):
    backend, relogio, codigos = modelo
    sessao = 'admin'
    if mutacao == 'ausente': sessao = 'nao-existe'
    if mutacao == 'revogada': backend.sessoes['admin']['revogada_em'] = relogio()
    if mutacao == 'expirada': backend.sessoes['admin']['expira_em'] = relogio()
    if mutacao == 'versao': backend.contas[1]['versao_credencial'] = 2
    if mutacao == 'perfil': backend.contas[1]['perfis'] = ['recepcionista']
    if mutacao == 'inativa': backend.contas[1]['situacao'] = 'inativo'
    antes = snapshot(backend)
    erro(codigo, status, lambda: getattr(backend, metodo)(sessao, 999, uuid7_em(relogio())))
    assert snapshot(backend) == antes
    assert codigos == []


def test_get_desconhecido_e_projecao_de_deadline_nao_escrevem_nem_emitem(modelo):
    backend, relogio, codigos = modelo
    antes = snapshot(backend)
    erro('OPERACAO_NAO_ENCONTRADA', 404, lambda: backend.consultar('admin', 999, uuid7_em(relogio())))
    assert snapshot(backend) == antes and codigos == []
    identificador, _ = criar(modelo)
    relogio.avancar(seconds=20)
    backend.habilitado = False
    backend.contas[2]['situacao'] = 'bloqueado'
    antes = snapshot(backend)
    resultado = backend.consultar('admin', 2, identificador)
    assert (resultado['estado_envio'], resultado['estado_link']) == ('desconhecido', 'ativo')
    assert snapshot(backend) == antes and len(codigos) == 1


def test_projecao_estrita_prazos_do_servidor_e_sem_segredos(modelo):
    backend, relogio, codigos = modelo
    identificador = uuid7_em(relogio() - timedelta(minutes=5))
    resultado = backend.criar('admin', 2, identificador)
    assert resultado == {
        'operacao_id': identificador, 'criada_em': '2026-11-07T12:00:00.000Z',
        'consultavel_ate': '2026-12-07T12:00:00.000Z',
        'expira_em': '2026-11-07T12:15:00.000Z', 'envio_limite_em': '2026-11-07T12:00:20.000Z',
        'estado_envio': 'processando', 'estado_link': 'pendente',
    }
    assert codigos[0] not in repr(backend.operacoes)
    assert 'titular@example.invalid' not in repr(backend.operacoes)
    assert codigos[0] not in repr(backend.auditoria)


@pytest.mark.parametrize('deslocamento,esperado', [(-300, None), (-300.001, 'OPERACAO_ANTIGA'), (60, None), (60.001, 'OPERACAO_FUTURA')])
def test_fronteiras_uuid7(modelo, deslocamento, esperado):
    backend, relogio, codigos = modelo
    identificador = uuid7_em(relogio() + timedelta(seconds=deslocamento))
    if esperado:
        erro(esperado, 409, lambda: backend.criar('admin', 2, identificador))
        assert not backend.operacoes and not codigos
    else:
        assert backend.criar('admin', 2, identificador)['estado_link'] == 'pendente'


@pytest.mark.parametrize('identificador', [str(uuid.uuid4()), 'identificador-invalido', '019A44D4-5C00-7000-8000-000000000001', '019a44d4-5c00-7000-0000-000000000001'])
def test_uuid_invalido_sem_reserva(modelo, identificador):
    backend, _, codigos = modelo
    erro('DADOS_INVALIDOS', 400, lambda: backend.criar('admin', 2, identificador))
    assert not backend.operacoes and not codigos


def test_replay_30_dias_sem_cota_frescor_flag_ou_novo_token(modelo):
    backend, relogio, codigos = modelo
    identificador, _ = criar(modelo)
    backend.registrar_resultado(identificador, 'aceito')
    relogio.avancar(days=29)
    backend.habilitado = False
    antes = snapshot(backend)
    assert backend.criar('admin', 2, identificador)['estado_link'] == 'expirado'
    assert snapshot(backend) == antes and len(codigos) == 1
    relogio.avancar(days=1)
    erro('OPERACAO_ANTIGA', 409, lambda: backend.criar('admin', 2, identificador))
    erro('OPERACAO_NAO_ENCONTRADA', 404, lambda: backend.consultar('admin', 2, identificador))
    del backend.operacoes[identificador]
    erro('OPERACAO_ANTIGA', 409, lambda: backend.criar('admin', 2, identificador))
    assert len(codigos) == 1


def test_vinculo_original_indistinto_no_get_e_conflitante_no_post(modelo):
    backend, _, codigos = modelo
    identificador, _ = criar(modelo)
    erro('OPERACAO_NAO_ENCONTRADA', 404, lambda: backend.consultar('outro-admin', 2, identificador))
    erro('OPERACAO_NAO_ENCONTRADA', 404, lambda: backend.consultar('admin', 3, identificador))
    erro('OPERACAO_CONFLITANTE', 409, lambda: backend.criar('outro-admin', 2, identificador))
    assert len(codigos) == 1


@pytest.mark.parametrize('situacao', ['inativo', 'bloqueado'])
def test_destinatario_inelegivel_preserva_conta(modelo, situacao):
    backend, relogio, codigos = modelo
    backend.contas[2]['situacao'] = situacao
    antes = snapshot(backend)
    erro('CONTA_INELEGIVEL', 409, lambda: backend.criar('admin', 2, uuid7_em(relogio())))
    assert snapshot(backend) == antes and codigos == []


def test_propria_conta_mesmas_regras_e_flag_desligada_por_padrao(modelo):
    backend, relogio, _ = modelo
    assert criar(modelo, conta=1)[1]['estado_link'] == 'pendente'
    offline = BackendLocalRelogio(relogio)
    offline.contas, offline.sessoes = backend.contas, backend.sessoes
    erro('RECURSO_INDISPONIVEL', 503, lambda: offline.criar('admin', 2, uuid7_em(relogio())))
    assert not offline.operacoes


def test_cooldown_e_cota_destinatario_sem_invalidar_link_rejeitado(modelo):
    backend, relogio, codigos = modelo
    identificador, _ = criar(modelo)
    e = erro('LIMITE_ENVIO', 429, lambda: backend.criar('admin', 2, uuid7_em(relogio(), 2)))
    assert e.retry_after == 60
    assert backend.consultar('admin', 2, identificador)['estado_link'] == 'pendente'
    for sequencia in [2, 3]:
        relogio.avancar(seconds=60)
        criar(modelo, sequencia=sequencia)
    relogio.avancar(seconds=60)
    e = erro('LIMITE_ENVIO', 429, lambda: backend.criar('admin', 2, uuid7_em(relogio(), 4)))
    assert e.retry_after == 3420 and len(codigos) == 3


def test_cota_solicitante_dez_por_hora(modelo):
    backend, relogio, codigos = modelo
    for conta in range(10, 21):
        backend.contas[conta] = dict(email=f'conta{conta}@example.invalid', situacao='ativo', perfis=['paciente'])
    for conta in range(10, 20):
        criar(modelo, conta=conta, sequencia=conta)
    erro('LIMITE_ENVIO', 429, lambda: backend.criar('admin', 20, uuid7_em(relogio(), 20)))
    assert len(codigos) == 10
    relogio.avancar(hours=1)
    criar(modelo, conta=20, sequencia=20)


@pytest.mark.parametrize('mesmo_id', [True, False])
def test_duas_reservas_concorrentes_deduplicadas_ou_limitadas(modelo, mesmo_id):
    backend, relogio, codigos = modelo
    barreira = threading.Barrier(2)

    def reservar(sequencia):
        barreira.wait(timeout=5)
        try:
            backend.criar('admin', 2, uuid7_em(relogio(), 1 if mesmo_id else sequencia))
            return 200
        except ErroContrato as falha:
            return falha.status

    with ThreadPoolExecutor(max_workers=2) as executor:
        resultados = list(executor.map(reservar, [1, 2]))
    assert sorted(resultados) == ([200, 200] if mesmo_id else [200, 429])
    assert len(backend.operacoes) == len(codigos) == len(backend.auditoria) == 1


@pytest.mark.parametrize('timeout', [True, 0, 31, '20'])
def test_configuracao_invalida_nao_reserva_ou_substitui(modelo, timeout):
    backend, relogio, codigos = modelo
    identificador, _ = criar(modelo)
    relogio.avancar(seconds=60)
    backend.timeout_envio_segundos = timeout
    antes = snapshot(backend)
    erro('RECURSO_INDISPONIVEL', 503, lambda: backend.criar('admin', 2, uuid7_em(relogio(), 2)))
    assert snapshot(backend) == antes and len(codigos) == 1
    assert backend.consultar('admin', 2, identificador)['estado_link'] == 'ativo'


def test_reenvio_aceito_invalida_anterior_mesmo_se_falhar(modelo):
    backend, relogio, codigos = modelo
    anterior, _ = criar(modelo)
    backend.registrar_resultado(anterior, 'aceito')
    relogio.avancar(seconds=60)
    atual, _ = criar(modelo, sequencia=2)
    backend.registrar_resultado(atual, 'falhou')
    assert backend.consultar('admin', 2, anterior)['estado_link'] == 'substituido'
    assert backend.consultar('admin', 2, atual)['estado_link'] == 'invalidado'
    for codigo in codigos:
        erro('LINK_INDISPONIVEL', 400, lambda: backend.confirmar(codigo, 'senha ficticia longa'))
    assert backend.contas[2]['senha_hash'] == 'hash-anterior-ficticio'


@pytest.mark.parametrize('codigo', [None, '', 'A' * 42, 'B' * 43, 'A' * 43 + '=', ' A' * 43])
def test_codigo_ausente_malformado_generico_sem_efeitos(modelo, codigo):
    backend, _, _ = modelo
    antes = snapshot(backend)
    erro('LINK_INDISPONIVEL', 400, lambda: backend.confirmar(codigo, 'senha ficticia longa'))
    assert snapshot(backend) == antes


def test_deadline_20s_confirma_apos_desconhecido_e_consumido_nao_revive(modelo):
    backend, relogio, codigos = modelo
    identificador, _ = criar(modelo)
    erro('ENVIO_EM_PROCESSAMENTO', 409, lambda: backend.confirmar(codigos[0], 'senha ficticia longa'))
    relogio.avancar(seconds=19, milliseconds=1)
    e = erro('ENVIO_EM_PROCESSAMENTO', 409, lambda: backend.confirmar(codigos[0], 'senha ficticia longa'))
    assert e.retry_after == 1
    relogio.avancar(milliseconds=999)
    assert backend.confirmar(codigos[0], 'senha ficticia longa') is None
    backend.registrar_resultado(identificador, 'falhou')
    relogio.avancar(minutes=20)
    resultado = backend.consultar('admin', 2, identificador)
    assert (resultado['estado_envio'], resultado['estado_link']) == ('falhou', 'consumido')


@pytest.mark.parametrize('terminal', ['expirado', 'substituido', 'invalidado'])
def test_resultado_tardio_nao_reativa_terminal(modelo, terminal):
    backend, relogio, _ = modelo
    identificador, _ = criar(modelo)
    if terminal == 'expirado': relogio.avancar(minutes=15)
    if terminal == 'substituido':
        relogio.avancar(seconds=60)
        criar(modelo, sequencia=2)
    if terminal == 'invalidado': backend.revogar_links(2)
    backend.registrar_resultado(identificador, 'aceito')
    backend.registrar_resultado(identificador, 'falhou')
    resultado = backend.consultar('admin', 2, identificador)
    assert (resultado['estado_envio'], resultado['estado_link']) == ('aceito', terminal)


@pytest.mark.parametrize('mutacao', ['email', 'versao', 'bloqueado', 'inativo', 'expirado'])
def test_confirmacao_revalida_elegibilidade_sem_troca(modelo, mutacao):
    backend, relogio, codigos = modelo
    identificador, _ = criar(modelo)
    backend.registrar_resultado(identificador, 'aceito')
    if mutacao == 'email': backend.contas[2]['email'] = 'mudou@example.invalid'
    if mutacao == 'versao': backend.contas[2]['versao_credencial'] = 2
    if mutacao in ['bloqueado', 'inativo']: backend.contas[2]['situacao'] = mutacao
    if mutacao == 'expirado': relogio.avancar(minutes=15)
    antes = snapshot(backend)
    erro('LINK_INDISPONIVEL', 400, lambda: backend.confirmar(codigos[0], 'senha ficticia longa'))
    assert snapshot(backend)[:4] == antes[:4]


@pytest.mark.parametrize('senha', ['a' * 11, 'a' * 129, None])
def test_politica_senha_nao_consome_token(modelo, senha):
    backend, _, codigos = modelo
    identificador, _ = criar(modelo)
    backend.registrar_resultado(identificador, 'aceito')
    antes = snapshot(backend)
    erro('DADOS_INVALIDOS', 400, lambda: backend.confirmar(codigos[0], senha))
    assert snapshot(backend)[:4] == antes[:4]


def test_duas_threads_no_modelo_no_maximo_uma_confirmacao(modelo):
    backend, _, codigos = modelo
    identificador, _ = criar(modelo)
    backend.registrar_resultado(identificador, 'aceito')
    barreira = threading.Barrier(2)

    def confirmar():
        barreira.wait(timeout=5)
        try:
            backend.confirmar(codigos[0], 'senha ficticia longa')
            return 204
        except ErroContrato as falha:
            return falha.status

    with ThreadPoolExecutor(max_workers=2) as executor:
        resultados = list(executor.map(lambda _: confirmar(), range(2)))
    assert sorted(resultados) == [204, 400]
    assert backend.contas[2]['versao_credencial'] == 2
    assert all(backend.sessoes[s]['revogada_em'] for s in ['titular-1', 'titular-2'])
    assert 'revogada_em' not in backend.sessoes['admin']


def test_rollback_integral_do_modelo_e_senha_com_espacos(modelo):
    backend, _, codigos = modelo
    identificador, _ = criar(modelo)
    backend.registrar_resultado(identificador, 'aceito')
    antes = copy.deepcopy((backend.contas, backend.sessoes, backend.operacoes, backend.auditoria))

    def falhar():
        raise RuntimeError('detalhe-proibido')

    backend.antes_commit = falhar
    erro('SERVICO_INDISPONIVEL', 503, lambda: backend.confirmar(codigos[0], '  senha ficticia longa  '))
    assert (backend.contas, backend.sessoes, backend.operacoes, backend.auditoria) == antes
    backend.antes_commit = None
    senha = '  senha ficticia longa  '
    backend.confirmar(codigos[0], senha)
    algoritmo, sal, digest = backend.contas[2]['senha_hash'].split('$')
    assert algoritmo == 'pbkdf2_sha256'
    assert hashlib.pbkdf2_hmac('sha256', senha.encode(), bytes.fromhex(sal), 100_000).hex() == digest


def test_commit_local_com_resposta204_perdida_nao_e_desfeito(modelo):
    backend, _, codigos = modelo
    identificador, _ = criar(modelo)
    backend.registrar_resultado(identificador, 'aceito')

    def perder_resposta():
        backend.confirmar(codigos[0], 'senha ficticia longa')
        raise ConnectionError('204 perdido somente no harness local')

    with pytest.raises(ConnectionError):
        perder_resposta()
    antes = snapshot(backend)
    erro('LINK_INDISPONIVEL', 400, lambda: backend.confirmar(codigos[0], 'outra senha ficticia longa'))
    assert snapshot(backend)[:4] == antes[:4]
    assert backend.consultar('admin', 2, identificador)['estado_link'] == 'consumido'


def test_limite_confirmacao_pendente_nao_invalida_codigo_alheio(modelo):
    backend, _, codigos = modelo
    criar(modelo)
    criar(modelo, conta=3, sequencia=2)
    for _ in range(30):
        erro('ENVIO_EM_PROCESSAMENTO', 409, lambda: backend.confirmar(codigos[0], 'senha ficticia longa'))
    erro('LIMITE_CONFIRMACAO', 429, lambda: backend.confirmar(codigos[0], 'senha ficticia longa'))
    erro('ENVIO_EM_PROCESSAMENTO', 409, lambda: backend.confirmar(codigos[1], 'senha ficticia longa'))
    assert backend.contas[2]['senha_hash'] == 'hash-anterior-ficticio'


def test_limite_codigo_desconhecido_inclui_senha_invalida_e_isola_titular(modelo):
    backend, _, codigos = modelo
    identificador, _ = criar(modelo)
    backend.registrar_resultado(identificador, 'aceito')
    inexistente = base64.urlsafe_b64encode(b'x' * 32).decode().rstrip('=')
    antes = snapshot(backend)
    for _ in range(30):
        erro('DADOS_INVALIDOS', 400, lambda: backend.confirmar(inexistente, 'curta'))
    erro('LIMITE_CONFIRMACAO', 429, lambda: backend.confirmar(inexistente, 'senha ficticia longa'))
    assert snapshot(backend)[:4] == antes[:4]
    assert backend.confirmar(codigos[0], 'senha ficticia longa') is None


@pytest.mark.parametrize('estado', ['consumido', 'expirado'])
def test_limite_tambem_cobre_codigo_consumido_ou_expirado(modelo, estado):
    backend, relogio, codigos = modelo
    identificador, _ = criar(modelo)
    backend.registrar_resultado(identificador, 'aceito')
    if estado == 'consumido':
        backend.confirmar(codigos[0], 'senha ficticia longa')
    else:
        relogio.avancar(minutes=15)
    antes = snapshot(backend)
    # A confirmação bem-sucedida também conta na janela do código consumido.
    for _ in range(29 if estado == 'consumido' else 30):
        erro('LINK_INDISPONIVEL', 400, lambda: backend.confirmar(codigos[0], 'senha ficticia longa'))
    erro('LIMITE_CONFIRMACAO', 429, lambda: backend.confirmar(codigos[0], 'senha ficticia longa'))
    assert snapshot(backend)[:4] == antes[:4]
