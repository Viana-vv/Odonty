import os, subprocess, yaml
from pathlib import Path
c=yaml.safe_load((Path.home()/".xano/credentials.yaml").read_text())
p=c["profiles"][c["default"]]
env=os.environ.copy()
env.update(XANO_TESTAR_REAL="1", XANO_API_BASE_URL=p["instance_origin"]+"/api:sorriso-acesso:v1",
           XANO_METADATA_TOKEN=p["access_token"], XANO_WORKSPACE_ID="149129")
os.environ.update(env)
import runpy
Ambiente = runpy.run_path("tests/test_xano_real.py")["Ambiente"]
alvo = Ambiente()
anteriores = alvo.listar(f"/table/{alvo.contas}/content")
for conta in anteriores:
    if (conta.get("nome") == "Pessoa Ficticia de Verificacao"
            and conta.get("email", "").startswith("verificacao.")
            and conta.get("email", "").endswith("@example.com")
            and conta.get("situacao") != "inativo"):
        alvo.alterar(conta, situacao="inativo")
alvo.admin.close()
print("Contas de verificacoes anteriores inativadas.", flush=True)
result=subprocess.run([str(Path(".venv/Scripts/python.exe").resolve()),"-m","pytest","tests/test_xano_real.py","-q","--tb=short","--junitxml=test-results/xano-real.xml"],env=env)
raise SystemExit(result.returncode)
