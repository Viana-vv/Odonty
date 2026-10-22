# Design: catálogo conectado de Procedimentos

A tela chama uma única vez `listar_opcoes_agenda(token)` e usa somente `opcoes["procedimentos"]`, cujo contrato contém `id` e `nome`. O identificador serve somente à chave do componente. A interface não infere outros atributos.

O carregamento é síncrono com indicador visual. Falhas apresentam mensagem genérica e opção para tentar novamente; respostas vazias e buscas sem resultado têm estados próprios. Cartões em duas colunas Streamlit se reorganizam no espaço estreito. O catálogo não oferece ações de escrita.

O Xano autoriza Administrador e Recepcionista. A interface faz uma verificação de apresentação adicional e não solicita opções para outros perfis.
