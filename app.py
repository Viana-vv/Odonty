"""Execute com: python -m streamlit run app.py."""

from pathlib import Path

import streamlit as st

from sorrisomais.api import ClienteXano, ErroAcesso
from sorrisomais.config import Configuracao, ConfiguracaoInvalida
from sorrisomais import sessao, paginas_equipe, acesso_equipe, recuperacao
from sorrisomais.ilustracoes import MARCA_MASCOTE, marca_html
from sorrisomais.icones import estilos_icones

RAIZ = Path(__file__).parent
st.set_page_config(page_title="Entrar · Sorriso+", page_icon=str(MARCA_MASCOTE), layout="wide")
st.html((RAIZ / "assets" / "estilos.css").read_text(encoding="utf-8"))
st.html(estilos_icones())


def solicitar_entrada():
    if st.session_state.get("processando") or st.session_state.get(sessao.CHAVE):
        return
    st.session_state["entrada_pendente"] = (
        st.session_state.get("email", ""), st.session_state.get("senha", "")
    )
    st.session_state["senha"] = ""
    st.session_state["processando"] = True


def aviso():
    notification = st.session_state.pop("aviso", None)
    if notification:
        kind, message = notification
        getattr(st, kind)(message)


def recuperar_senha():
    etapa = st.session_state.get("recuperacao_etapa", "email")
    with st.container(key="entrada"):
        ilustracao, formulario = st.columns([1.05, 1], gap="large", vertical_alignment="center")
        with ilustracao:
            from sorrisomais.ilustracoes import _data_uri
            arte_login = _data_uri("14-seguranca-login.png")
            st.html(f'''<section class="boas-vindas">
              <div class="marca-clara">{marca_html()}</div>
              <h1>Recupere seu acesso.<br>Com segurança e tranquilidade.</h1>
              <p>Enviaremos um código para confirmar sua identidade e permitir que você crie uma nova senha.</p>
              <div class="login-arte"><img src="{arte_login}" alt="Mascote com proteção de acesso" /></div>
              <div class="marca-rodape">Cuidado que transforma sorrisos.</div>
            </section>''')
        with formulario:
            with st.container(key="formulario"):
                st.caption("RECUPERAÇÃO DE ACESSO")
                if etapa == "email":
                    st.title("Esqueceu sua senha?")
                    st.markdown("Informe o e-mail da sua Conta de Acesso.")
                    email = st.text_input("E-mail", key="recuperacao_email", placeholder="voce@exemplo.com")
                    if st.button("Enviar código", type="primary", width="stretch", disabled=not cliente):
                        try:
                            st.session_state["recuperacao_operacao"] = cliente.solicitar_recuperacao(email)
                            st.session_state["recuperacao_etapa"] = "otp"
                            st.session_state["aviso"] = ("success", "Se o e-mail estiver cadastrado, você receberá um código em instantes.")
                            st.rerun()
                        except ErroAcesso as error:
                            st.session_state["aviso"] = ("error", str(error))
                    aviso()
                elif etapa == "otp":
                    st.title("Valide seu código")
                    st.markdown("Digite o código de seis dígitos enviado para seu e-mail.")
                    otp = st.text_input("Código OTP", key="recuperacao_otp", max_chars=6)
                    if st.button("Validar código", type="primary", width="stretch"):
                        try:
                            cliente.validar_otp(st.session_state.get("recuperacao_operacao", ""), otp)
                            st.session_state["recuperacao_etapa"] = "senha"
                            st.session_state.pop("recuperacao_otp", None)
                            st.rerun()
                        except ErroAcesso as error:
                            st.session_state["aviso"] = ("error", str(error))
                    aviso()
                else:
                    st.title("Crie uma nova senha")
                    st.markdown("Escolha uma senha com pelo menos 12 caracteres.")
                    nova = st.text_input("Nova senha", type="password", key="recuperacao_nova")
                    confirmacao = st.text_input("Confirmar senha", type="password", key="recuperacao_confirmacao")
                    if st.button("Trocar senha", type="primary", width="stretch"):
                        try:
                            cliente.trocar_senha(st.session_state.get("recuperacao_operacao", ""), nova, confirmacao)
                            for chave in ("recuperacao_etapa", "recuperacao_email", "recuperacao_operacao", "recuperacao_nova", "recuperacao_confirmacao"):
                                st.session_state.pop(chave, None)
                            st.session_state["aviso"] = ("success", "Senha alterada com sucesso. Entre com sua nova senha.")
                            st.rerun()
                        except ErroAcesso as error:
                            st.session_state["aviso"] = ("error", str(error))
                    aviso()
                with st.container(key="recuperacao-voltar"):
                    if st.button("Voltar para o login", type="tertiary"):
                        for chave in ("recuperacao_etapa", "recuperacao_email", "recuperacao_operacao", "recuperacao_otp", "recuperacao_nova", "recuperacao_confirmacao"):
                            st.session_state.pop(chave, None)
                        st.rerun()


try:
    cliente = ClienteXano(Configuracao.do_ambiente())
except ConfiguracaoInvalida as error:
    cliente = None
    sessao.limpar(st.session_state)
    configuracao_mensagem = str(error)

try:
    conta = sessao.identificar(st.session_state, cliente) if cliente else None
except ErroAcesso as error:
    st.session_state["aviso"] = ("error", str(error))
    conta = None

if conta:
    acesso_equipe.renderizar(conta, cliente, paginas_equipe)
    # Reexecuta a página no prazo de expiração mesmo sem interação.
    @st.fragment(run_every="15s")
    def verificar_prazo():
        from datetime import datetime, timezone
        credencial = st.session_state.get(sessao.CHAVE)
        if credencial and credencial.expira_em <= datetime.now(timezone.utc):
            sessao.limpar(st.session_state)
            st.session_state["aviso"] = ("info", "Sua sessão expirou. Entre novamente.")
            st.rerun(scope="app")
    verificar_prazo()
else:
    if st.session_state.get("recuperacao_etapa"):
        recuperar_senha()
        st.stop()
    with st.container(key="entrada"):
        ilustracao, formulario = st.columns([1.05, 1], gap="large", vertical_alignment="center")
        with ilustracao:
            from sorrisomais.ilustracoes import _data_uri
            arte_login = _data_uri("14-seguranca-login.png")
            st.html(f'''<section class="boas-vindas">
              <div class="marca-clara">{marca_html()}</div>
              <span class="etiqueta">GESTÃO ODONTOLÓGICA</span>
              <h1>Sua clínica mais organizada.<br>Seu atendimento mais <em>humano.</em></h1>
              <p>Agenda, pacientes e prontuários em um só lugar, para sua equipe cuidar do que realmente importa.</p>
              <div class="login-arte"><img src="{arte_login}" alt="Mascote com proteção de acesso" /></div>
              <div class="marca-rodape">Cuidado que transforma sorrisos.</div>
            </section>''')
        with formulario:
            with st.container(key="formulario"):
                st.caption("BEM-VINDO DE VOLTA")
                st.title("Acesse a clínica")
                st.markdown("Entre com sua Conta de Acesso da equipe.")
                aviso()
                if not cliente:
                    st.info(configuracao_mensagem)
                ocupado = st.session_state.get("processando", False)
                with st.form("login", border=False):
                    st.text_input("E-mail", key="email", placeholder="voce@exemplo.com", disabled=ocupado or not cliente)
                    st.text_input("Senha", key="senha", type="password", placeholder="Digite sua senha", disabled=ocupado or not cliente)
                    st.form_submit_button(
                        "Entrando…" if ocupado else "Entrar", type="primary", width="stretch",
                        disabled=ocupado or not cliente, on_click=solicitar_entrada, key="login-entrar",
                    )
                with st.container(key="recuperacao-link"):
                    if st.button("Esqueci minha senha", type="tertiary", disabled=ocupado or not cliente):
                        st.session_state["recuperacao_etapa"] = "email"
                        st.rerun()
                st.caption("Acesso exclusivo à equipe da clínica.")
                st.html('<div class="nota-acesso">Seu cuidado faz a diferença. Vamos começar?</div>')
                if ocupado:
                    email, senha = st.session_state.pop("entrada_pendente", ("", ""))
                    try:
                        with st.spinner("Verificando seu acesso…"):
                            sessao.entrar(st.session_state, cliente, email, senha)
                    except ErroAcesso as error:
                        st.session_state["aviso"] = ("error", str(error))
                    finally:
                        senha = None
                        st.session_state["processando"] = False
                    st.rerun()
