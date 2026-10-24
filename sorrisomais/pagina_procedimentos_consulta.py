"""Tela independente para acompanhar Procedimentos de uma Consulta."""

from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

from . import sessao
from .api import ErroAcesso

_FUSO_LOCAL = ZoneInfo("America/Sao_Paulo")


def _data_legivel(valor):
    if not isinstance(valor, str):
        return "Data não informada"
    try:
        data = datetime.fromisoformat(valor.replace("Z", "+00:00"))
    except ValueError:
        return "Data não informada"
    if data.tzinfo is None:
        data = data.replace(tzinfo=_FUSO_LOCAL)
    return data.astimezone(_FUSO_LOCAL).strftime("%d/%m/%Y às %H:%M")


def _renderizar_lista(cliente, token, consulta, procedimentos):
    if not procedimentos:
        st.info("Esta Consulta ainda não possui Procedimentos planejados.")
        return

    for procedimento in procedimentos:
        identificador = procedimento.get("id", "sem-id")
        nome = procedimento.get("procedimento_nome")
        situacao = procedimento.get("situacao")
        with st.container(key=f"consulta-procedimento-{identificador}", border=True):
            coluna_info, coluna_situacao = st.columns([0.78, 0.22], vertical_alignment="center")
            with coluna_info:
                st.subheader(nome if isinstance(nome, str) and nome.strip() else "Procedimento")
                planejamento = procedimento.get("profissional_planejamento_nome")
                criado_em = procedimento.get("criado_em")
                if isinstance(planejamento, str) and planejamento.strip():
                    st.caption(f"Planejado por {planejamento} · {_data_legivel(criado_em)}")
                elif criado_em:
                    st.caption(f"Planejado em {_data_legivel(criado_em)}")
            with coluna_situacao:
                if situacao == "realizado":
                    st.success("Realizado")
                elif situacao == "planejado":
                    st.info("Planejado")
                elif situacao in {"autorizado", "cancelado"}:
                    st.caption(situacao.capitalize())
                else:
                    st.warning("Situação indisponível")

            if situacao == "realizado":
                responsavel = procedimento.get("realizado_por_nome")
                data = procedimento.get("realizado_em")
                if isinstance(responsavel, str) and responsavel.strip():
                    st.caption(f"Realizado por {responsavel} · {_data_legivel(data)}")
                else:
                    st.caption(f"Realizado em {_data_legivel(data)}")
            elif situacao == "planejado":
                chave = f"marcar-procedimento-realizado-{identificador}"
                if st.button("Marcar como realizado", key=chave, type="primary"):
                    try:
                        with st.spinner("Registrando realização…"):
                            realizado = cliente.marcar_procedimento_realizado(
                                token, consulta["id"], identificador
                            )
                        procedimento.update(realizado)
                        st.success("Procedimento marcado como realizado.")
                        responsavel = procedimento.get("realizado_por_nome")
                        data = procedimento.get("realizado_em")
                        if isinstance(responsavel, str) and responsavel.strip():
                            st.caption(f"Realizado por {responsavel} · {_data_legivel(data)}")
                        else:
                            st.caption(f"Realizado em {_data_legivel(data)}")
                    except ErroAcesso as erro:
                        if erro.status == 401:
                            sessao.limpar(st.session_state)
                            st.error("Sua sessão expirou. Entre novamente.")
                        else:
                            st.error(str(erro))
                        return
                    except Exception:
                        st.error("Não foi possível registrar a realização. Tente novamente.")
                        return


def renderizar(cliente, conta, consulta):
    """Renderiza Procedimentos da Consulta fornecida pelo chamador da navegação."""
    st.caption("ATENDIMENTO")
    st.title("Procedimentos da Consulta")
    st.markdown("Acompanhe o planejamento e registre os Procedimentos realizados.")

    perfis = set(getattr(conta, "perfis", ()))
    if "profissional" not in perfis:
        st.warning("Esta área está disponível somente para Profissionais autorizados.")
        return
    credencial = st.session_state.get(sessao.CHAVE)
    if not credencial:
        st.error("Sua sessão não está disponível. Entre novamente.")
        return
    if not isinstance(consulta, dict) or not isinstance(consulta.get("id"), int):
        st.info("Selecione uma Consulta para acompanhar seus Procedimentos.")
        return

    titulo = consulta.get("paciente_nome")
    if isinstance(titulo, str) and titulo.strip():
        st.subheader(titulo)
    inicio = consulta.get("inicio_em")
    if inicio:
        st.caption(f"Consulta · {_data_legivel(inicio)}")

    try:
        with st.spinner("Carregando Procedimentos…"):
            procedimentos = cliente.listar_procedimentos_consulta(
                credencial.token, consulta["id"]
            )
    except ErroAcesso as erro:
        if erro.status == 401:
            sessao.limpar(st.session_state)
            st.error("Sua sessão expirou. Entre novamente.")
        else:
            st.error(str(erro))
        return
    except Exception:
        st.error("Não foi possível carregar os Procedimentos. Tente novamente em instantes.")
        return

    _renderizar_lista(cliente, credencial.token, consulta, procedimentos)
