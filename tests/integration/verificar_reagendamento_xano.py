"""Verificação opt-in em grupo/tabelas exclusivos; nunca chama Sorriso Acesso.

python tests/integration/verificar_reagendamento_xano.py planejar
python tests/integration/verificar_reagendamento_xano.py executar

O plano/IDs ficam em test-results/reagendamento-xano-plano.json, sem segredos.
Credenciais vêm exclusivamente do perfil local do CLI Xano. Todos os objetos
de teste recebem prefixo aleatório e são removidos em finally.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import threading
import time

import requests
import yaml

RAIZ = Path(__file__).resolve().parents[2]
PASTA_RESULTADOS = Path(os.getenv("XANO_REAGENDAMENTO_RESULTADOS_DIR", RAIZ / "test-results"))
PLANO = PASTA_RESULTADOS / "reagendamento-xano-plano.json"
BUNDLE = PASTA_RESULTADOS / "reagendamento-xano-temporario.xs"
RELATORIO = PASTA_RESULTADOS / "reagendamento-xano-resultado.json"
INTERVALO = 3.2


class Verificacao:
    def __init__(self):
        config = yaml.safe_load((Path.home() / ".xano/credentials.yaml").read_text())
        perfil = config["profiles"][config["default"]]
        self.origem = perfil["instance_origin"].rstrip("/")
        self.workspace = int(perfil["workspace"])
        self.meta = self.origem + f"/api:meta/workspace/{self.workspace}"
        self.sessao = requests.Session()
        self.sessao.headers["Authorization"] = "Bearer " + perfil["access_token"]
        self.trava = threading.Lock()
        self.inicios = []
        self.resultados = []
        self.tabelas = {}
        self.grupo = None
        self.funcao = None
        self.tokens = {}

    def aguardar(self):
        with self.trava:
            if self.inicios:
                time.sleep(max(0, INTERVALO - (time.monotonic() - self.inicios[-1])))
            self.inicios.append(time.monotonic())
            return self.inicios[-1]

    def metadados(self, metodo, caminho, **kwargs):
        self.aguardar()
        resposta = self.sessao.request(metodo, self.meta + caminho, timeout=90, **kwargs)
        if not resposta.ok:
            # Metadados desta ferramenta contêm somente código e fixtures fictícias.
            detalhe = resposta.text[:1500] if "multidoc" in caminho else ""
            raise RuntimeError(f"Metadados {metodo} {caminho}: HTTP {resposta.status_code} {detalhe}")
        return resposta.json() if resposta.content else None

    def listar(self, caminho):
        dados = self.metadados("GET", caminho, params={"per_page": 100})
        return dados if isinstance(dados, list) else dados["items"]

    def chamar(self, metodo, caminho, *, perfil="administrador", esperado=None, **kwargs):
        assert self.slug.startswith("teste-reagendamento-64-")
        inicio = self.aguardar()
        token = self.tokens.get(perfil) if perfil else None
        resposta = requests.request(
            metodo, self.origem + "/api:" + self.slug + "/" + self.prefixo + caminho,
            headers={"Authorization": "Bearer " + token} if token else {},
            timeout=90, allow_redirects=False, **kwargs,
        )
        fim = time.monotonic()
        if esperado is not None and resposta.status_code != esperado:
            raise AssertionError(f"{metodo} {caminho}: esperado {esperado}, recebido {resposta.status_code}; {resposta.text[:700]}")
        return resposta, inicio, fim

    def registrar(self, nome, **dados):
        print(nome, json.dumps(dados, ensure_ascii=False), flush=True)
        self.resultados.append({"cenario": nome, **dados})

    def adaptar(self, fonte):
        fonte = fonte.lstrip("\ufeff")
        fonte = re.sub(r'^\s*guid = .*$', '', fonte, flags=re.MULTILINE)
        fonte = fonte.replace('api_group = "Sorriso Acesso"', f'api_group = "{self.slug}"')
        for nome in self.nomes:
            novo = self.prefixo + nome
            fonte = re.sub(rf'\b(db\.(?:get|query|edit|add)|table) {nome}\b', rf'\1 {novo}', fonte)
            fonte = fonte.replace(f'$db.{nome}.', f'$db.{novo}.')
            fonte = fonte.replace(f'table = "{nome}"', f'table = "{novo}"')
            fonte = fonte.replace(f'auth = "{nome}"', f'auth = "{novo}"')
        fonte = fonte.replace("function sorriso_validar_sessao", "function " + self.prefixo + "validar_sessao")
        fonte = fonte.replace("function.run sorriso_validar_sessao", "function.run " + self.prefixo + "validar_sessao")
        # Nomes de rotas também são exclusivos: o dry-run não pode associá-los
        # a rotas existentes de outro grupo por coincidência de nome/verbo.
        fonte = re.sub(r'\bquery "([^"]+)"', lambda m: 'query "' + self.prefixo + '/' + m[1] + '"', fonte)
        fonte = re.sub(r'\bquery (\w+) verb=', lambda m: 'query "' + self.prefixo + '/' + m[1] + '" verb=', fonte)
        return fonte

    def carregar(self):
        plano = json.loads(PLANO.read_text(encoding="utf-8"))
        assert plano["workspace"] == self.workspace
        self.slug, self.prefixo, self.nomes = plano["grupo"], plano["prefixo"], plano["tabelas"]
        assert self.slug.startswith("teste-reagendamento-64-") and self.prefixo.startswith("tr64_")
        return plano

    def planejar(self):
        sufixo = secrets.token_hex(4)
        self.slug = "teste-reagendamento-64-" + sufixo
        self.prefixo = "tr64_" + sufixo + "_"
        principais = ["conta_acesso", "sessao_acesso", "consulta", "disponibilidade_agenda",
                      "consulta_disponibilidade", "consulta_reagendamento", "consulta_situacao_historico",
                      "agenda_controle", "consulta_procedimento"]
        self.nomes = ["conta_acesso", "sessao_acesso", "paciente", "profissional", "procedimento",
                      "consulta", "disponibilidade_agenda", "consulta_disponibilidade",
                      "consulta_reagendamento", "consulta_situacao_historico", "agenda_controle",
                      "consulta_procedimento", "registro_clinico"]
        documentos = []
        for nome in principais:
            documentos.append(self.adaptar((RAIZ / f"backend/xano/table/{nome}.xs").read_text(encoding="utf-8")))
        # Somente os campos que as rotas utilizam; nenhum schema real é alterado.
        for nome, schema in {
            "paciente": 'int id\n text situacao',
            "profissional": 'int id\n text situacao\n int? conta_acesso_id?',
            "procedimento": 'int id\n text nome',
            "registro_clinico": 'int id\n int consulta_id { table = "consulta" }\n text conteudo',
        }.items():
            documentos.append(self.adaptar(f'table {nome} {{\n auth = false\n schema {{\n {schema}\n }}\n index = [{{type: "primary", field: [{{name: "id"}}]}}]\n}}'))
        documentos.append(f'api_group "{self.slug}" {{\n canonical = "{self.slug}"\n swagger = {{active: false}}\n}}')
        documentos.append(self.adaptar((RAIZ / "backend/xano/function/sorriso_validar_sessao.xs").read_text(encoding="utf-8")))
        documentos.append(self.adaptar((RAIZ / "backend/xano/api/sorriso_acesso/auth/login_POST.xs").read_text(encoding="utf-8")))
        original = (RAIZ / "backend/xano/api/sorriso_acesso/consultas_id_reagendamento_POST.xs").read_text(encoding="utf-8")
        documentos.append(self.adaptar(original))
        lento = original.replace('query "consultas/{id}/reagendamento"', 'query "consultas/{id}/reagendamento_lento"')
        marcador = '            db.get consulta {\n'
        assert lento.count(marcador) == 1
        lento = lento.replace(marcador, '            util.sleep { value = 9 }\n' + marcador)
        documentos.append(self.adaptar(lento))
        falha = original.replace('query "consultas/{id}/reagendamento"', 'query "consultas/{id}/reagendamento_falha"')
        marcador = '                } as $destino_reservado'
        assert falha.count(marcador) == 1
        falha = falha.replace(marcador, marcador + '\n                precondition (false) {\n                  error_type = "standard"\n                  error = "Falha fictícia induzida após todas as gravações."\n                }')
        documentos.append(self.adaptar(falha))
        documentos.append(self.adaptar((RAIZ / "backend/xano/api/sorriso_acesso/disponibilidades_id_PATCH.xs").read_text(encoding="utf-8")))
        documentos.append(self.adaptar(self.ajudantes()))
        bundle = "\n---\n".join(documentos)
        # Todos os acessos a dados e auth do bundle devem apontar para cópias.
        assert all(nome.startswith(self.prefixo) for nome in re.findall(r'\bdb\.(?:get|query|edit|add) (\w+)', bundle))
        assert all(nome.startswith(self.prefixo) for nome in re.findall(r'(?:table|auth) = "([^"]+)"', bundle))
        PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)
        BUNDLE.write_text(bundle, encoding="utf-8")
        plano = {"workspace": self.workspace, "grupo": self.slug, "prefixo": self.prefixo,
                 "tabelas": self.nomes, "sha256_bundle": hashlib.sha256(bundle.encode()).hexdigest()}
        PLANO.write_text(json.dumps(plano, indent=2), encoding="utf-8")
        previa = self.metadados("POST", "/multidoc/dry-run", params={"partial": "true", "delete": "false", "records": "false", "env": "false", "transaction": "true"}, data=bundle.encode(), headers={"Content-Type": "text/x-xanoscript"})
        print(json.dumps({"grupo": self.slug, "resumo": previa["summary"]}, ensure_ascii=False, indent=2), flush=True)
        assert all(operacao["action"] == "create" for operacao in previa["operations"]), "A prévia deve conter somente objetos novos de teste."
        assert sum(op["type"] == "table" for op in previa["operations"]) == len(self.nomes)
        plano["somente_criacao_confirmada"] = True
        PLANO.write_text(json.dumps(plano, indent=2), encoding="utf-8")

    @staticmethod
    def ajudantes():
        auth = '''
    function.run sorriso_validar_sessao {
      input = {conta_id: $auth.id, sessao_id: $auth.extras.sessao_id}
    } as $sessao
    db.get conta_acesso {
      field_name = "id"
      field_value = $auth.id
    } as $conta
    precondition (($conta.perfis|intersect:["administrador"]|count) > 0 && $conta.situacao == "ativo") {
      error_type = "accessdenied"
      error = "Acesso de teste negado."
    }
'''
        # Os dados e cópias são exclusivos deste grupo temporário.
        preparar = '''query preparar verb=POST {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input { }
  stack { AUTH
    util.get_raw_input { encoding = "json" } as $bruto
    db.add paciente { data = {situacao: "ativo"} } as $paciente1
    db.add paciente { data = {situacao: "ativo"} } as $paciente2
    db.add profissional { data = {situacao: "Ativo"} } as $profissional1
    db.add profissional { data = {situacao: "Ativo"} } as $profissional2
    var $paciente_segundo { value = $paciente2.id }
    conditional { if ($bruto.mesmo_paciente) { var.update $paciente_segundo { value = $paciente1.id } } }
    db.add disponibilidade_agenda { data = {profissional_id: $profissional1.id, inicio: $bruto.inicio1, fim: $bruto.fim1, situacao: "reservado"} } as $origem1
    db.add disponibilidade_agenda { data = {profissional_id: $profissional2.id, inicio: $bruto.inicio2, fim: $bruto.fim2, situacao: "reservado"} } as $origem2
    db.add disponibilidade_agenda { data = {profissional_id: $profissional1.id, inicio: $bruto.inicio_destino, fim: $bruto.fim_destino, situacao: "disponivel"} } as $destino
    db.add disponibilidade_agenda { data = {profissional_id: $profissional2.id, inicio: $bruto.inicio_destino, fim: $bruto.fim_destino, situacao: "disponivel"} } as $alternativo
    db.add procedimento { data = {nome: "Procedimento fictício de teste"} } as $procedimento
    db.add consulta { data = {paciente_id: $paciente1.id, profissional_id: $profissional1.id, procedimento_id: $procedimento.id, inicio_em: $bruto.inicio1, fim_em: $bruto.fim1, situacao: "Confirmada", observacoes: "Observação fictícia preservada"} } as $consulta1
    db.add consulta { data = {paciente_id: $paciente_segundo, profissional_id: $profissional2.id, procedimento_id: null, inicio_em: $bruto.inicio2, fim_em: $bruto.fim2, situacao: "Agendada"} } as $consulta2
    db.add consulta_disponibilidade { data = {consulta_id: $consulta1.id, disponibilidade_id: $origem1.id} } as $vinculo1
    db.add consulta_disponibilidade { data = {consulta_id: $consulta2.id, disponibilidade_id: $origem2.id} } as $vinculo2
    db.add consulta_procedimento { data = {consulta_id: $consulta1.id, procedimento_id: $procedimento.id, profissional_id: $profissional1.id} } as $procedimento_original
    db.add registro_clinico { data = {consulta_id: $consulta1.id, conteudo: "Registro exclusivamente fictício"} } as $registro_original
  }
  response = {consulta1: $consulta1.id, consulta2: $consulta2.id, origem1: $origem1.id, origem2: $origem2.id, destino: $destino.id, alternativo: $alternativo.id, paciente1: $paciente1.id, paciente2: $paciente2.id, profissional1: $profissional1.id, profissional2: $profissional2.id}
  history = false
}'''.replace("AUTH", auth)
        tabelas = ["consulta", "disponibilidade_agenda", "consulta_disponibilidade",
                   "consulta_situacao_historico", "consulta_reagendamento", "agenda_controle",
                   "consulta_procedimento", "registro_clinico"]
        consultas = "\n".join(f'    db.query {nome} {{ return = {{type: "list"}} }} as ${nome}_linhas' for nome in tabelas)
        resposta = ", ".join(f"{nome}: ${nome}_linhas" for nome in tabelas)
        verificar = '''query verificar verb=GET {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input { }
  stack { AUTH
CONSULTAS
  }
  response = {RESPOSTA}
  history = false
}'''.replace("AUTH", auth).replace("CONSULTAS", consultas).replace("RESPOSTA", resposta)
        return preparar + "\n---\n" + verificar

    def descobrir_objetos(self):
        self.tabelas = {t["name"][len(self.prefixo):]: t["id"] for t in self.listar("/table") if t["name"].startswith(self.prefixo)}
        self.grupo = next((g["id"] for g in self.listar("/apigroup") if g["name"] == self.slug), None)
        self.funcao = next((f["id"] for f in self.listar("/function") if f["name"] == self.prefixo + "validar_sessao"), None)

    def limpar(self):
        self.carregar()
        self.descobrir_objetos()
        if self.grupo:
            self.metadados("DELETE", f"/apigroup/{self.grupo}")
        if self.funcao:
            self.metadados("DELETE", f"/function/{self.funcao}")
        for nome in reversed(self.nomes):
            if nome in self.tabelas:
                self.metadados("DELETE", f"/table/{self.tabelas[nome]}")
        self.descobrir_objetos()
        assert not self.tabelas and self.grupo is None and self.funcao is None
        self.registrar("limpeza", grupo_removido=True, tabelas_removidas=len(self.nomes), funcao_removida=True)

    def executar(self):
        plano = self.carregar()
        assert plano.get("somente_criacao_confirmada") is True
        bundle = BUNDLE.read_text(encoding="utf-8").encode("utf-8")
        assert hashlib.sha256(bundle).hexdigest() == plano["sha256_bundle"]
        try:
            self.metadados("POST", "/multidoc", params={"partial": "true", "delete": "false", "records": "false", "env": "false", "transaction": "true"}, data=bundle, headers={"Content-Type": "text/x-xanoscript"})
            self.descobrir_objetos()
            assert len(self.tabelas) == len(self.nomes) and self.grupo and self.funcao
            self.registrar("compilacao", grupo=self.slug, tabelas=len(self.tabelas), rotas=7)
            self.autenticar()
            self.testar()
        finally:
            self.limpar()
            intervalos = [b-a for a,b in zip(self.inicios,self.inicios[1:])]
            relatorio = {"data_utc": datetime.now(timezone.utc).isoformat(), "workspace": self.workspace,
                         "grupo_temporario": self.slug, "prefixo_tabelas": self.prefixo,
                         "requisicoes": len(self.inicios), "intervalo_minimo_segundos": min(intervalos) if intervalos else None,
                         "resultados": self.resultados}
            RELATORIO.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")

    def autenticar(self):
        self.contas = {}
        for perfil in ("administrador", "recepcionista", "profissional", "paciente"):
            senha = secrets.token_urlsafe(24)
            email = f"teste.{secrets.token_hex(6)}@example.com"
            conta = self.metadados("POST", f"/table/{self.tabelas['conta_acesso']}/content", json={"nome": "Conta Fictícia de Verificação", "email": email, "senha": senha, "perfis": [perfil], "situacao": "ativo"})
            assert conta["senha"] != senha
            self.contas[perfil] = conta["id"]
            resposta, _, _ = self.chamar("POST", "/auth/login", perfil=None, esperado=200, json={"email": email, "senha": senha})
            self.tokens[perfil] = resposta.json()["token"]
        self.registrar("autenticacao_isolada", perfis=4, senhas_transformadas=True)

    def preparar(self, *, mesmo_paciente=False):
        inicio = int(time.time() * 1000) + 30 * 86400000
        payload = {"inicio1": inicio, "fim1": inicio+3600000, "inicio2": inicio+7200000,
                   "fim2": inicio+10800000, "inicio_destino": inicio+86400000,
                   "fim_destino": inicio+90000000, "mesmo_paciente": mesmo_paciente}
        resposta, _, _ = self.chamar("POST", "/preparar", esperado=200, json=payload)
        return resposta.json()

    def snapshot(self):
        resposta, _, _ = self.chamar("GET", "/verificar", esperado=200)
        return {nome: sorted(linhas, key=lambda r: r["id"]) for nome, linhas in resposta.json().items()}

    @staticmethod
    def negocio(snapshot):
        return {k:v for k,v in snapshot.items() if k != "agenda_controle"}

    def reagendar(self, consulta, destino, *, variante="reagendamento", perfil="administrador", esperado=None):
        return self.chamar("POST", f"/consultas/{consulta}/{variante}", perfil=perfil,
                           esperado=esperado, json={"disponibilidade_id": destino, "justificativa": "Justificativa fictícia de teste"})

    def concorrentes(self, primeira, segunda):
        with ThreadPoolExecutor(max_workers=2) as executor:
            a = executor.submit(primeira)
            b = executor.submit(segunda)
            ra, rb = a.result(), b.result()
        assert ra[1] < rb[1] < ra[2], "As execuções precisam se sobrepor no servidor."
        assert rb[1] - ra[1] >= 3
        assert sorted([ra[0].status_code, rb[0].status_code]) == [201, 409]
        return ra[0].status_code, rb[0].status_code, round(rb[1]-ra[1], 3)

    def testar(self):
        dados = self.preparar()
        antes = self.snapshot()
        for perfil, status in ((None,401),("paciente",403),("profissional",403)):
            self.reagendar(dados["consulta1"], dados["destino"], perfil=perfil, esperado=status)
        assert self.snapshot() == antes
        self.registrar("autorizacao", sem_token=401, paciente=403, profissional=403, sem_alteracoes=True)
        for corpo in ({}, {"disponibilidade_id":True,"justificativa":"Fictícia"},
                      {"disponibilidade_id":dados["destino"],"justificativa":" "},
                      {"disponibilidade_id":dados["destino"],"justificativa":"Fictícia","paciente_id":999}):
            self.chamar("POST", f"/consultas/{dados['consulta1']}/reagendamento", esperado=400, json=corpo)
        self.reagendar(9999999, dados["destino"], esperado=404)
        self.reagendar(dados["consulta1"], dados["origem1"], esperado=409)
        assert self.snapshot() == antes
        self.registrar("validacao", invalidos=4, inexistente=404, mesmo_horario=409, sem_alteracoes=True)
        for perfil in ("administrador", "recepcionista"):
            if perfil == "recepcionista":
                dados = self.preparar()
                antes = self.snapshot()
            resposta, _, _ = self.reagendar(dados["consulta1"], dados["destino"], perfil=perfil, esperado=201)
            depois = self.snapshot()
            nova = resposta.json()["consulta"]["id"]
            original = next(c for c in depois["consulta"] if c["id"]==dados["consulta1"])
            original_antes = next(c for c in antes["consulta"] if c["id"]==dados["consulta1"])
            assert original == {**original_antes, "situacao":"Cancelada"}
            vinculo = next(r for r in depois["consulta_reagendamento"] if r["consulta_original_id"]==dados["consulta1"])
            assert vinculo["consulta_nova_id"] == nova and vinculo["conta_acesso_id"]==self.contas[perfil]
            assert depois["consulta_procedimento"] == antes["consulta_procedimento"]
            assert depois["registro_clinico"] == antes["registro_clinico"]
            assert next(d for d in depois["disponibilidade_agenda"] if d["id"]==dados["origem1"])["situacao"]=="disponivel"
            assert next(d for d in depois["disponibilidade_agenda"] if d["id"]==dados["destino"])["situacao"]=="reservado"
            self.reagendar(dados["consulta1"], dados["alternativo"], esperado=409)
            self.registrar("sucesso_"+perfil, status=201, vinculo_explicito=True, relacoes_preservadas=True, repeticao=409)
        dados = self.preparar()
        antes = self.snapshot()
        self.reagendar(dados["consulta1"],dados["destino"],variante="reagendamento_falha",esperado=409)
        assert self.snapshot()==antes, "Rollback precisa restaurar inclusive controles e auditoria."
        self.registrar("rollback_induzido", status=409, snapshot_integral_preservado=True)
        for cenario in ("mesma_consulta","mesmo_destino","mesmo_paciente","edicao_destino"):
            dados=self.preparar(mesmo_paciente=cenario=="mesmo_paciente")
            primeira=lambda: self.reagendar(dados["consulta1"],dados["destino"],variante="reagendamento_lento")
            if cenario=="edicao_destino":
                segunda=lambda: self.chamar("PATCH",f"/disponibilidades/{dados['destino']}",json={"situacao":"bloqueado"})
            else:
                segunda=lambda: self.reagendar(dados["consulta1"] if cenario=="mesma_consulta" else dados["consulta2"], dados["alternativo"] if cenario in ("mesma_consulta","mesmo_paciente") else dados["destino"])
            status=self.concorrentes(primeira,segunda)
            depois=self.snapshot()
            assert sum(r["consulta_original_id"] in (dados["consulta1"],dados["consulta2"]) for r in depois["consulta_reagendamento"])==1
            assert next(d for d in depois["disponibilidade_agenda"] if d["id"]==dados["destino"])["situacao"]=="reservado"
            self.registrar("concorrencia_"+cenario, primeira=status[0],segunda=status[1],intervalo=status[2],uma_substituta=True)


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("acao",choices=("planejar","executar","limpar"))
    argumentos=parser.parse_args()
    verificacao=Verificacao()
    getattr(verificacao,argumentos.acao)()
