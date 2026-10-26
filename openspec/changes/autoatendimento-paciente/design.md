# Design

## Contexto

O entrypoint atual (`app.py`) compõe login e área da equipe, mas atualmente chama `paginas_equipe` para qualquer Conta de Acesso aceita por `/auth/me`, incluindo perfil somente Paciente. O cliente `sorrisomais.api.ClienteXano` já oferece login, identificação, logout e métodos para Consultas, Registros Clínicos e Exames. Os contratos Xano existentes restringem Registros Clínicos do Paciente por conta vinculada e `liberado_paciente=true`, e Exames pela conta vinculada, ocultando o resultado até `Resultado disponível`.

## Decisões

- Criar um segundo entrypoint Streamlit (`portal_paciente.py`), isolado do `app.py` da equipe, com composição própria de login/sessão e área do Paciente. Não alterar `sorrisomais/navegacao.py` nem `sorrisomais/paginas_equipe.py`.
- Ajustar `app.py` para somente chamar a área interna quando a Conta de Acesso possuir perfil administrador, recepcionista ou profissional. Para conta somente Paciente, mostrar aviso de que o autoatendimento fica em endereço separado; nenhuma área interna é renderizada. As operações internas seguem protegidas pelo Xano.
- Reutilizar ClienteXano e os contratos REST existentes. Não criar parâmetros `paciente_id` na interface; a autorização e derivação do escopo permanecem no Xano.
- Usar `st.session_state` em memória para a credencial, em módulo isolado; não armazenar em query params, arquivos, cookies próprios ou localStorage. Limpar senha imediatamente após o envio e credencial ao expirar/perder identidade.
- Reutilizar a tela isolada de Consultas; acrescentar seções separadas para Registros Clínicos liberados e Exames com resultado disponível.
- Exibir apenas campos já retornados pelos contratos: Consultas sem Procedimentos; Registros Clínicos liberados com conteúdo/data/profissional; Exames com tipo, situação e datas, com resultado condicional. Nunca mostrar observações clínicas de Exame ou referência de arquivo.
- Seguir cores, hierarquia e padrões responsivos do kit Sorriso Mais pela folha existente, sem alterar CSS global.
- Não duplicar testes de contratos GET/POST que já tenham testes Python e JavaScript por rota. Acrescentar testes de integração da interface/sessão sem rede e cobrir especificamente a barreira de perfil no `app.py`.

## Arquivos esperados

- Novo `portal_paciente.py`, módulos de sessão/apresentação do Paciente e testes isolados.
- Alteração localizada em `app.py` para negar a composição interna a perfil somente Paciente.
- Atualização da documentação OpenSpec e instruções operacionais em `docs/autoatendimento-paciente.md`.
- Nenhuma alteração nas rotas Xano, em `sorrisomais/navegacao.py`, `sorrisomais/paginas_equipe.py`, nos testes de contrato de `GET /consultas` ou no CSS global.

## Execução e implantação

Execução local: `python -m streamlit run portal_paciente.py`. Em implantação, publicar este entrypoint como serviço Streamlit separado e configurar seu domínio/URL no ambiente de hospedagem; não presumir URL pública nem reutilizar a URL do serviço da equipe.

## Questões em aberto

Nenhuma questão funcional em aberto após inspeção dos contratos locais. A aparência final requer inspeção manual pelo grupo em computador e largura móvel.
- Preservar no parser local de Registros Clínicos a data `registrado_em` já retornada pelo contrato, sem criar novos campos ou rotas Xano.
