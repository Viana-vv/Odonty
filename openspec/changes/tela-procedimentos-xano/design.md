# Design: catálogo conectado de Procedimentos

A tela exclusiva para Administrador chama uma única vez `listar_opcoes_agenda(token)` e usa somente `opcoes["procedimentos"]`, cujo contrato contém `id` e `nome`. O identificador serve somente à chave do componente. A interface não infere outros atributos. A Recepcionista pode usar a mesma rota para formulários de agendamento, mas não acessa esta área de catálogo.

O carregamento é síncrono com indicador visual. Falhas apresentam mensagem genérica e opção para tentar novamente; respostas vazias e buscas sem resultado têm estados próprios. Respostas 401/403 limpam a sessão e exibem a mensagem segura da API. Cartões em duas colunas Streamlit se reorganizam no espaço estreito. O catálogo não oferece ações de escrita.

O Xano autoriza Administrador e Recepcionista. A interface faz uma verificação de apresentação adicional e não solicita opções para outros perfis.
