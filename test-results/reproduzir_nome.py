import os
import secrets
import requests
import time
import sys
sys.path.insert(0, 'test-results')
from xano_admin import origin
from playwright.sync_api import sync_playwright
from streamlit.proto.BackMsg_pb2 import BackMsg

def observar_frame(payload):
    if not isinstance(payload, bytes):
        return
    msg = BackMsg()
    msg.ParseFromString(payload)
    if msg.WhichOneof('type') == 'rerun_script':
        print('Envio:', [(w.id.rsplit('-', 1)[-1], w.WhichOneof('value'), len(w.string_value) if w.WhichOneof('value') == 'string_value' else '') for w in msg.rerun_script.widget_states.widgets])

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(os.getenv('TEST_APP_URL', 'http://localhost:8501'))
    page.get_by_label('E-mail', exact=True).fill(os.environ['TEST_ADMIN_EMAIL'])
    page.get_by_label('Senha', exact=True).fill(os.environ['TEST_ADMIN_PASSWORD'])
    page.get_by_role('button', name='Entrar', exact=True).click()
    page.get_by_role('button', name='Cadastrar profissional', exact=True).wait_for(timeout=30000)
    page.wait_for_timeout(25000)
    page.get_by_role('button', name='Cadastrar profissional', exact=True).click(timeout=30000)
    page.get_by_label('Nome completo', exact=True).fill('Profissional Ficticio de Teste')
    email = 'teste.nome.' + secrets.token_hex(6) + '@example.com'
    senha = secrets.token_urlsafe(18)
    page.get_by_label('E-mail do profissional', exact=True).fill(email)
    page.get_by_label('Senha inicial', exact=True).fill(senha)
    page.get_by_label('Confirmar senha', exact=True).fill(senha)
    page.get_by_label('CRO', exact=True).fill('SP-' + str(secrets.randbelow(900000000) + 100000000))
    page.get_by_role('combobox').click()
    page.get_by_role('combobox').press('ArrowDown')
    page.get_by_role('combobox').press('Enter')
    print('Nome antes do clique:', len(page.get_by_label('Nome completo', exact=True).input_value()))
    page.wait_for_timeout(25000)
    page.get_by_role('button', name='Cadastrar', exact=True).click()
    sucesso = page.get_by_text('Profissional cadastrado. Ele já pode entrar pelo login da equipe.', exact=True)
    try:
        sucesso.wait_for(timeout=45000)
    except Exception:
        print('Mensagem apos cadastro:', page.get_by_test_id('stAlert').all_text_contents())
        raise
    print(page.get_by_test_id('stAlert').all_text_contents())
    print('Nome apos envio:', page.get_by_label('Nome completo', exact=True).input_value())
    assert sucesso.count() == 1, 'Cadastro real ainda nao confirmou sucesso'
    time.sleep(25)
    login = requests.post(origin + '/api:sorriso-acesso:v1/auth/login', json={'email': email, 'senha': senha}, timeout=30)
    print('Login REST da nova conta:', login.status_code)
    assert login.status_code == 200
    token_criado = login.json()['token']
    time.sleep(3)
    requests.post(origin + '/api:sorriso-acesso:v1/auth/logout', headers={'Authorization': 'Bearer ' + token_criado}, timeout=30)
    page.get_by_role('button', name='Sair', exact=True).click()
    page.get_by_role('button', name='Entrar', exact=True).wait_for()
    page.wait_for_timeout(25000)
    page.get_by_label('E-mail', exact=True).fill(email)
    page.get_by_label('Senha', exact=True).fill(senha)
    page.get_by_role('button', name='Entrar', exact=True).click()
    try:
        page.get_by_role('heading', name='Bem-vindo ao Sorriso+').wait_for(timeout=30000)
    except Exception:
        print('Mensagem no login:', page.get_by_test_id('stAlert').all_text_contents())
        raise
    assert page.get_by_role('button', name='Cadastrar profissional', exact=True).count() == 0
    print('Login do profissional criado confirmado, sem acao administrativa.')
    page.get_by_role('button', name='Sair', exact=True).click()
    browser.close()
