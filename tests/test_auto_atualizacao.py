from pathlib import Path


def test_atualizacao_automatica_usa_fragmento_de_vinte_segundos_e_protege_edicao():
    codigo = (Path(__file__).resolve().parents[1] / "app.py").read_text(encoding="utf-8")
    assert '@st.fragment(run_every="20s")' in codigo
    assert 'invalidar_cache(st.session_state)' in codigo
    assert '"pacientes_xano_edicao"' in codigo
