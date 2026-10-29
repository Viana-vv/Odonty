import unittest
from streamlit.testing.v1 import AppTest
from sorrisomais.cache_xano import carregar_cache, invalidar_cache
from sorrisomais.pagina_nova_consulta_xano import _normalizar_namespace_cache

class ErroHTTP(Exception):
    def __init__(self, status):
        self.status = status

class TestCacheXano(unittest.TestCase):
    def test_hit_force_and_namespace_invalidation(self):
        state = {}
        calls = []
        loader = lambda: calls.append(1) or {"ok": True}
        self.assertEqual(carregar_cache(state, "a", "consultas", loader), {"ok": True})
        carregar_cache(state, "a", "consultas", loader)
        self.assertEqual(len(calls), 1)
        carregar_cache(state, "a", "consultas", loader, force=True)
        self.assertEqual(len(calls), 2)
        invalidar_cache(state, ("consultas",))
        carregar_cache(state, "a", "consultas", loader)
        self.assertEqual(len(calls), 3)

    def test_namespace_aliases_are_canonical_and_parameterized(self):
        self.assertEqual(_normalizar_namespace_cache(("agenda/opcoes",)), "agenda/opcoes")
        self.assertEqual(_normalizar_namespace_cache(("exames-solicitacao-opcoes",)), "agenda/opcoes")
        self.assertEqual(_normalizar_namespace_cache(("reagendamento-consultas", 17)), "consultas:paciente=17")
        self.assertEqual(_normalizar_namespace_cache(("consultas:paciente", 17)), "consultas:paciente=17")
        self.assertEqual(_normalizar_namespace_cache(("disponibilidades", 3, "inicio", "fim")),
                         "disponibilidades:profissional=3:inicio=inicio:fim=fim")
        self.assertNotEqual(_normalizar_namespace_cache(("consultas", 17)),
                            _normalizar_namespace_cache(("consultas", 18)))

    def test_namespace_invalidation_is_prefix_scoped_without_collisions(self):
        state = {}
        for namespace in ("consultas:paciente=17", "consultas:inicio=hoje",
                          "procedimentos-consulta:31", "contas-acesso"):
            carregar_cache(state, "a", namespace, lambda value=namespace: [value])
        invalidar_cache(state, ("consultas",))
        remaining = {key[1] for key in state["xano_get_cache"]}
        self.assertEqual(remaining, {"contas-acesso"})
        invalidar_cache(state, ("agenda/opcoes",))
        self.assertIn("contas-acesso", {key[1] for key in state["xano_get_cache"]})

    def test_mutation_categories_invalidate_documented_dependencies(self):
        dependencies = {
            "consultas": {"consultas:inicio=hoje", "disponibilidades:profissional=3", "agenda/opcoes",
                          "procedimentos-consulta:31", "exames", "registros-clinicos"},
            "disponibilidades": {"disponibilidades:profissional=3", "consultas:inicio=hoje", "agenda/opcoes"},
            "profissionais": {"profissionais", "especialidades", "agenda/opcoes", "consultas:inicio=hoje",
                              "disponibilidades:profissional=3"},
            "pacientes": {"pacientes", "paciente:17", "agenda/opcoes", "consultas:inicio=hoje"},
            "registros-clinicos": {"registros-clinicos", "consultas:inicio=hoje"},
            "exames": {"exames", "registros-clinicos"},
            "procedimentos": {"procedimentos", "agenda/opcoes", "procedimentos-consulta:31"},
        }
        namespaces = ("profissionais", "especialidades", "procedimentos", "agenda/opcoes", "consultas:inicio=hoje",
                      "disponibilidades:profissional=3", "procedimentos-consulta:31", "exames",
                      "registros-clinicos", "pacientes", "paciente:17")
        for mutation, expected in dependencies.items():
            with self.subTest(mutation=mutation):
                state = {}
                calls = {namespace: 0 for namespace in namespaces}
                def loader(namespace):
                    def load():
                        calls[namespace] += 1
                        return [namespace]
                    return load
                for namespace in namespaces:
                    carregar_cache(state, "a", namespace, loader(namespace))
                invalidar_cache(state, (mutation,))
                remaining = {key[1] for key in state.get("xano_get_cache", {})}
                self.assertEqual(set(namespaces) - remaining, expected)
                for namespace in expected:
                    carregar_cache(state, "a", namespace, loader(namespace))
                    self.assertEqual(calls[namespace], 2)
        state = {}
        invalidar_cache(state)
        self.assertNotIn("xano_get_escopo", state)

    def test_nova_consulta_and_catalog_share_options_get(self):
        script = "\n".join([
            "import streamlit as st",
            "from sorrisomais.pagina_nova_consulta_xano import _leitura_com_cache",
            "from sorrisomais.cache_xano import carregar_cache",
            "class ClienteFalso:",
            "    def listar_opcoes_agenda(self, token):",
            "        st.session_state['get_count'] = st.session_state.get('get_count', 0) + 1",
            "        return {'pacientes': [], 'profissionais': [], 'procedimentos': []}",
            "cliente = ClienteFalso()",
            "token = 'token-ficticio'",
            "_leitura_com_cache(token, ('agenda/opcoes',), lambda: cliente.listar_opcoes_agenda(token))",
            "carregar_cache(st.session_state, token, 'agenda/opcoes', lambda: cliente.listar_opcoes_agenda(token))",
        ])
        app = AppTest.from_string(script).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["get_count"], 1)
        app.run()
        self.assertEqual(app.session_state["get_count"], 1)

    def test_identity_change_and_logout(self):
        state = {}
        calls = []
        loader = lambda: calls.append(1) or [1]
        carregar_cache(state, "account-one", "registros", loader)
        self.assertEqual(carregar_cache(state, "account-two", "registros", loader), [1])
        self.assertEqual(len(calls), 2)
        invalidar_cache(state)
        self.assertNotIn("xano_get_cache", state)
        self.assertNotIn("xano_get_escopo", state)
        self.assertNotIn("account-two", repr(state))

    def test_force_failure_discards_old_value_and_logout_removes_scope_hash(self):
        state = {}
        carregar_cache(state, "a", "consultas", lambda: ["old"])
        scope = state["xano_get_escopo"]
        with self.assertRaises(RuntimeError):
            carregar_cache(state, "a", "consultas", lambda: (_ for _ in ()).throw(RuntimeError()), force=True)
        self.assertNotIn((scope, "consultas"), state["xano_get_cache"])
        invalidar_cache(state)
        self.assertNotIn("xano_get_escopo", state)

    def test_errors_never_cache_and_auth_error_clears_private_values(self):
        state = {}
        carregar_cache(state, "a", "public", lambda: ["private"])
        with self.assertRaises(RuntimeError):
            carregar_cache(state, "a", "failure", lambda: (_ for _ in ()).throw(RuntimeError()))
        self.assertNotIn((state["xano_get_escopo"], "failure"), state["xano_get_cache"])
        with self.assertRaises(ErroHTTP):
            carregar_cache(state, "a", "restricted", lambda: (_ for _ in ()).throw(ErroHTTP(403)))
        self.assertNotIn("xano_get_cache", state)

if __name__ == "__main__":
    unittest.main()
