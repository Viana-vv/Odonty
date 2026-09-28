import sys, os, time, json
from pathlib import Path
from datetime import datetime, timedelta, timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ["XANO_API_BASE_URL"]="https://exemplo.invalid/api:teste"
from sorrisomais.api import ClienteXano, Credencial, ContaAcesso
prazo=datetime.now(timezone.utc)+timedelta(hours=1)
contador=0
def entrar(self,email,senha):
    global contador
    contador+=1
    Path("test-results/submissoes.json").write_text(json.dumps({"chamadas":contador}),encoding="utf-8")
    time.sleep(5)
    return Credencial("token-simulado",prazo)
ClienteXano.entrar=entrar
ClienteXano.identificar=lambda self,token: ContaAcesso(1,"Pessoa Ficticia",("profissional",),prazo)
ClienteXano.sair=lambda self,token: None
from streamlit.web import bootstrap
bootstrap.load_config_options({"server.port":8502,"server.address":"127.0.0.1","server.headless":True,"browser.gatherUsageStats":False})
bootstrap.run(str(Path("app.py").resolve()),False,[],{"server.port":8502,"server.address":"127.0.0.1","server.headless":True,"browser.gatherUsageStats":False})
