"""Harness visual local: componentes reais e cliente fictício sem rede."""
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
import json
import runpy
import sys
import time

import streamlit as st

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
from sorrisomais import paginas_equipe, sessao
from sorrisomais.icones import estilos_icones
from sorrisomais.api import ContaAcesso, Credencial, ErroAcesso

dados = json.loads((RAIZ / "tests/fixtures/agenda_ficticia.json").read_text(encoding="utf-8"))
area = st.query_params.get("tela", "inicio")
perfil = st.query_params.get("perfil", "administrador")


class ClienteVisual:
    configuracao = SimpleNamespace(modo_demonstracao=False, cadastro_paciente_habilitado=True)

    def listar_consultas(self, token, **filtros):
        if area == "erro":
            raise ErroAcesso("Falha fictícia de carregamento.", 503)
        if area == "vazio":
            return []
        consultas = [dict(dados["consultas"][0]), dict(dados["consultas"][2])]
        for indice, nome in enumerate(("Paciente Fictício Jardim", "Paciente Fictícia Lua", "Paciente Fictício Sol")):
            consulta = dict(dados["consultas"][0])
            consulta.update(id=503+indice, paciente_id=103+indice, paciente_nome=nome,
                            inicio_em=f'{dados["data"]}T{15+indice}:00:00-03:00',
                            fim_em=f'{dados["data"]}T{15+indice}:30:00-03:00')
            consultas.append(consulta)
        for consulta in consultas:
            consulta["inicio_em"] = consulta["inicio_em"].replace(dados["data"], date.today().isoformat())
            consulta["fim_em"] = consulta["fim_em"].replace(dados["data"], date.today().isoformat())
            consulta["procedimentos"] = [consulta["procedimento_nome"]] if consulta["procedimento_nome"] else []
        return consultas

    def listar_opcoes_agenda(self, token):
        return dados["opcoes"]

    def listar_profissionais(self, token):
        return [dict(id=201+i, nome=nome, cro=f"CRO FICTÍCIO {i+1}",
                     especialidade={"id": 1, "nome": "Clínica geral"},
                     email="profissional@example.invalid", telefone="11900000000", situacao="ativo")
                for i, nome in enumerate(("Dra. Exemplo Sorriso", "Dr. Exemplo Horizonte", "Dra. Exemplo Aurora"))]

    def listar_especialidades(self, token):
        return [{"id": 1, "nome": "Clínica geral", "situacao": "ativo"}]

    def listar_disponibilidades(self, token, *args, **kwargs):
        return []

    def listar_registros_clinicos(self, token):
        return [{"id": 1, "paciente_id": 101, "paciente_nome": "Paciente Fictícia Aurora",
                 "profissional_nome": "Dra. Exemplo Sorriso", "conteudo": "Avaliação fictícia e orientações de higiene.",
                 "registrado_em": "2026-10-30T13:00:00-03:00"}]

    def obter_paciente(self, token, paciente_id):
        return dict(dados["pacientes_cadastrais"][0])

    def sair(self, token):
        return None

    def identificar(self, token):
        return ContaAcesso(101, "Paciente Fictícia Aurora", ("paciente",), prazo)

    def listar_procedimentos_consulta(self, token, consulta_id):
        return [{"id": 1, "procedimento_nome": "Profilaxia fictícia", "situacao": "planejado"}]

    def _request(self, method, route, **kwargs):
        if route == "/exames":
            return {"exames": []}
        if route == "/contas-acesso":
            return {"contas_acesso": [{"id": 1, "nome": "Pessoa Fictícia", "email": "ficticio@example.invalid", "perfis": ["profissional"], "situacao": "ativo"}]}
        raise AssertionError("Rota não simulada: " + route)


if area in {"login", "portal_login"}:
    runpy.run_path(str(RAIZ / ("app.py" if area == "login" else "portal_paciente.py")), run_name="__main__")
elif area == "controles":
    st.set_page_config(layout="wide")
    st.html((RAIZ / "assets/estilos.css").read_text(encoding="utf-8"))
    st.html(estilos_icones())
    st.title("Controles fictícios")
    st.text_input("Senha de teste", type="password", value="ficticio")
    st.selectbox("Seleção de teste", ["Primeira", "Segunda"])
    st.date_input("Data de teste")
    st.number_input("Quantidade de teste", min_value=0, value=1)
    st.checkbox("Confirmação de teste", value=True)
    st.info("Informação de teste")
    st.success("Sucesso de teste")
    st.warning("Aviso de teste")
    st.error("Erro de teste")
    with st.expander("Detalhes de teste"):
        st.write("Conteúdo de teste")
    st.button("Ação de teste", key="acao-teste")
    st.button("Ação indisponível", key="acao-indisponivel", disabled=True)
elif area == "carregando":
    st.set_page_config(layout="wide")
    st.html((RAIZ / "assets/estilos.css").read_text(encoding="utf-8"))
    st.html(estilos_icones())
    st.button("Operação fictícia em andamento", disabled=True)
    with st.spinner("Carregamento fictício"):
        time.sleep(4)
else:
    st.set_page_config(layout="wide")
    st.html((RAIZ / "assets/estilos.css").read_text(encoding="utf-8"))
    st.html(estilos_icones())
    prazo = datetime.now(timezone.utc) + timedelta(hours=1)
    st.session_state[sessao.CHAVE] = Credencial("token-ficticio-local", prazo)
    pagina = {"erro": "agenda", "vazio": "agenda", "evolucao": "prontuarios", "edicao": "pacientes"}.get(area, area)
    if st.session_state.get("_visual_tela") != (area, perfil):
        st.session_state["_visual_tela"] = (area, perfil)
        st.session_state["pagina_equipe"] = pagina
        if area == "evolucao":
            st.session_state["prontuario_nova_evolucao_aberta"] = True
    conta = ContaAcesso(1, "Pessoa Fictícia", (perfil,), prazo)
    if area == "portal":
        from sorrisomais import autoatendimento_paciente, sessao_paciente
        st.session_state[sessao_paciente.CHAVE_CREDENCIAL] = Credencial("token-ficticio-local", prazo)
        autoatendimento_paciente.renderizar(ClienteVisual())
    elif area == "contas":
        from sorrisomais import pagina_contas_acesso_xano
        pagina_contas_acesso_xano.renderizar(ClienteVisual(), conta)
    elif area == "procedimentos_consulta":
        from sorrisomais import pagina_procedimentos_consulta
        pagina_procedimentos_consulta.renderizar(ClienteVisual(), conta, dados["consultas"][0])
    elif area.startswith("demo_"):
        from sorrisomais import paginas_demo
        st.session_state["demo_pagina"] = area.removeprefix("demo_")
        paginas_demo.renderizar(conta, ClienteVisual())
    else:
        paginas_equipe.renderizar(conta, ClienteVisual())
