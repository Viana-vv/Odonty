"""Harness visual local: componentes reais e cliente fictício sem rede."""
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
import json
import runpy
import sys

import streamlit as st

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
from sorrisomais import paginas_equipe, sessao
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

    def _request(self, method, route, **kwargs):
        if route == "/exames":
            return {"exames": []}
        raise AssertionError("Rota não simulada: " + route)


if area == "login":
    runpy.run_path(str(RAIZ / "app.py"), run_name="__main__")
else:
    st.set_page_config(layout="wide")
    st.html((RAIZ / "assets/estilos.css").read_text(encoding="utf-8"))
    prazo = datetime.now(timezone.utc) + timedelta(hours=1)
    st.session_state[sessao.CHAVE] = Credencial("token-ficticio-local", prazo)
    pagina = {"erro": "agenda", "vazio": "agenda", "evolucao": "prontuarios", "edicao": "pacientes"}.get(area, area)
    if st.session_state.get("_visual_tela") != (area, perfil):
        st.session_state["_visual_tela"] = (area, perfil)
        st.session_state["pagina_equipe"] = pagina
        if area == "evolucao":
            st.session_state["prontuario_nova_evolucao_aberta"] = True
    conta = ContaAcesso(1, "Pessoa Fictícia", (perfil,), prazo)
    paginas_equipe.renderizar(conta, ClienteVisual())
