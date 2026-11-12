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
                    with st.container(key="otp-campos"):
                        partes_otp = [
                            st.text_input(
                                f"Dígito {indice + 1}",
                                key=f"recuperacao_otp_{indice}",
                                max_chars=1,
                                label_visibility="collapsed",
                            )
                            for indice in range(6)
                        ]
                    st.html("""
                    <script>
                    (() => {
                      const configurarCampos = () => {
                      const root = document.querySelector('.st-key-otp-campos');
                      if (!root) return;
                      const campos = [...root.querySelectorAll('[data-testid="stTextInput"] input')];
                      if (campos.length !== 6) return;
                      campos.forEach((campo, indice) => {
                        if (campo.dataset.otpConfigurado === '1') return;
                        campo.dataset.otpConfigurado = '1';
                        campo.inputMode = 'numeric';
                        campo.pattern = '[0-9]*';
                        campo.autocomplete = indice === 0 ? 'one-time-code' : 'off';
                        campo.addEventListener('keydown', (evento) => {
                          if (evento.ctrlKey || evento.metaKey || evento.altKey) return;
                          if (evento.key === 'Backspace' && !campo.value && indice > 0) {
                            campos[indice - 1].focus();
                            campos[indice - 1].select();
                          }
                          if (evento.key.length === 1 && !/[0-9]/.test(evento.key)) evento.preventDefault();
                        });
                        campo.addEventListener('input', () => {
                          const somenteDigitos = campo.value.replace(/[^0-9]/g, '');
                          if (campo.value !== somenteDigitos) {
                            const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
                            setter.call(campo, somenteDigitos.slice(-1));
                            campo.dispatchEvent(new Event('input', { bubbles: true }));
                          }
                          if (campo.value && indice < campos.length - 1) {
                            window.setTimeout(() => {
                              campos[indice + 1].focus();
                              campos[indice + 1].select();
                            }, 0);
                          }
                        });
                        campo.addEventListener('paste', (evento) => {
                          const colado = (evento.clipboardData || window.clipboardData).getData('text').replace(/[^0-9]/g, '');
                          if (!colado) return;
                          evento.preventDefault();
                          const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
                          [...colado.slice(0, campos.length - indice)].forEach((digito, deslocamento) => {
                            const destino = campos[indice + deslocamento];
                            setter.call(destino, digito);
                            destino.dispatchEvent(new Event('input', { bubbles: true }));
                          });
                          window.setTimeout(() => campos[Math.min(indice + colado.length, campos.length - 1)].focus(), 0);
                        });
                      });
                      };
                      window.sorrisoOtpObserver?.disconnect();
                      window.sorrisoOtpObserver = new MutationObserver(configurarCampos);
                      window.sorrisoOtpObserver.observe(document.body, {childList: true, subtree: true});
                      configurarCampos();
                    })();
                    </script>
                    """, unsafe_allow_javascript=True)
                    otp = recuperacao.montar_otp(partes_otp)
                    if st.button("Validar código", type="primary", width="stretch"):
                        try:
                            cliente.validar_otp(st.session_state.get("recuperacao_operacao", ""), otp)
                            st.session_state["recuperacao_etapa"] = "senha"
                            for indice in range(6):
                                st.session_state.pop(f"recuperacao_otp_{indice}", None)
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
                        chaves_otp = [f"recuperacao_otp_{indice}" for indice in range(6)]
                        for chave in ("recuperacao_etapa", "recuperacao_email", "recuperacao_operacao", *chaves_otp, "recuperacao_nova", "recuperacao_confirmacao"):
                            st.session_state.pop(chave, None)
                        st.rerun()


try:
    cliente = ClienteXano(Configuracao.do_ambiente())
except ConfiguracaoInvalida as error:
    cliente = None
    sessao.limpar(st.session_state)
    configuracao_mensagem = str(error)

try:
    from sorrisomais import sessao_local
    try:
        sessao_local.restaurar(st.session_state, st.context.cookies)
    except OSError:
        st.warning("A recuperação local está indisponível. Entre novamente para continuar.")
    conta = sessao.identificar(st.session_state, cliente) if cliente else None
except ErroAcesso as error:
    if st.session_state.get(sessao.CHAVE):
        st.error("Não foi possível verificar seu acesso agora. Tente novamente em instantes.")
        if st.button("Tentar novamente", key="revalidar-sessao"):
            st.rerun()
        st.stop()
    st.session_state["aviso"] = ("error", str(error))
    conta = None

if conta:
    try:
        sessao_local.manter(st.session_state)
    except OSError:
        st.warning("Não foi possível ativar a recuperação local. Confira se a porta 8502 está livre.")
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
