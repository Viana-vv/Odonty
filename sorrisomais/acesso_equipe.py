"""Gate visual da aplicação interna; autorizações efetivas permanecem no Xano."""

import streamlit as st

PERFIS_INTERNOS = {"administrador", "recepcionista", "profissional"}


def renderizar(conta, cliente, paginas_equipe):
    if not set(conta.perfis).intersection(PERFIS_INTERNOS):
        st.title("Acesso da equipe")
        st.info("Esta Conta de Acesso não possui perfil interno. O autoatendimento do Paciente fica em um endereço separado.")
        return False
    paginas_equipe.renderizar(conta, cliente)
    return True
