# Autoatendimento do Paciente

O portal é um serviço Streamlit independente do acesso da equipe.

## Execução local

Na raiz do projeto, com a configuração Xano do ambiente disponível:

```powershell
python -m streamlit run portal_paciente.py
```

O Streamlit informa o endereço local ao iniciar. O portal usa a mesma configuração de API Xano por variáveis de ambiente e não grava credenciais no navegador ou em arquivos.

## Implantação

Publique `portal_paciente.py` como serviço Streamlit separado do serviço da equipe em Render ou Railway. Configure o domínio/URL do portal na configuração de domínios da plataforma e mantenha o endereço atribuído à equipe separado. Não há URL pública fixa neste documento; use a URL fornecida pelo ambiente de implantação. Não copie segredos entre serviços: configure as variáveis Xano necessárias em cada serviço conforme o ambiente.
