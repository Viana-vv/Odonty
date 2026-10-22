# Design: catálogo conectado de Procedimentos

A tela exclusiva para Administrador chama uma única vez `listar_opcoes_agenda(token)` e usa somente `opcoes["procedimentos"]`, cujo contrato contém `id` e `nome`. O identificador serve somente à chave do componente. A interface não infere outros atributos. A Recepcionista pode usar a mesma rota para formulários de agendamento, mas não acessa esta área de catálogo.

O carregamento é síncrono com indicador visual. Resultados bem-sucedidos ficam em cache apenas na sessão Streamlit e vinculados a uma impressão digital do token; buscas e outros reruns não repetem a chamada. Falhas não armazenam resposta e aguardam uma ação explícita de nova tentativa. Respostas 401/403 limpam sessão e cache e exibem a mensagem segura da API. Sem credencial local, a tela informa que é necessário entrar novamente e não chama a API. Respostas vazias e buscas sem resultado têm estados próprios. Cartões em duas colunas Streamlit se reorganizam no espaço estreito. O catálogo não oferece ações de escrita.

O Xano autoriza Administrador e Recepcionista. A interface faz uma verificação de apresentação adicional e não solicita opções para outros perfis.
