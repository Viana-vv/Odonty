"""Execute com: python -m streamlit run app.py."""

from pathlib import Path
import base64

import streamlit as st

from sorrisomais.api import ClienteXano, ErroAcesso, ROTULOS
from sorrisomais.config import Configuracao, ConfiguracaoInvalida
from sorrisomais import sessao, paginas_equipe

RAIZ = Path(__file__).parent
st.set_page_config(page_title="Entrar · Sorriso+", page_icon="🦷", layout="wide")
st.html((RAIZ / "assets" / "estilos.css").read_text(encoding="utf-8"))


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
    paginas_equipe.renderizar(conta, cliente)
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
    with st.container(key="entrada"):
        ilustracao, formulario = st.columns([1.05, 1], gap="large", vertical_alignment="center")
        with ilustracao:
            imagem = base64.b64encode((RAIZ / "assets" / "1000323602.jpg").read_bytes()).decode("ascii")
            st.html(f'''<section class="boas-vindas">
              <div class="marca marca-clara"><span class="marca-icone">S</span><span class="marca-nome">Sorriso<span>+</span></span></div>
              <span class="etiqueta">GESTÃO ODONTOLÓGICA</span>
              <h1>Sua clínica mais organizada.<br>Seu atendimento mais <em>humano.</em></h1>
              <p>Agenda, pacientes e prontuários em um só lugar, para sua equipe cuidar do que realmente importa.</p>
              <div class="beneficios">
                <div><b>✓</b><span><strong>Rotina centralizada</strong><small>Mais clareza para toda a equipe.</small></span></div>
                <div><b>✓</b><span><strong>Dados fictícios e seguros</strong><small>Ambiente demonstrativo para apresentar.</small></span></div>
              </div>
              <div class="mascote-moldura"><img src="data:image/jpeg;base64,{imagem}" alt="Mascote dentista do Sorriso+" /></div>
              <small class="marca-rodape">MVP acadêmico · Sorriso+</small>
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
                        disabled=ocupado or not cliente, on_click=solicitar_entrada,
                    )
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

st.html('<footer>Sorriso+ <span>·</span> MVP acadêmico <span>·</span> Somente dados fictícios</footer>')
