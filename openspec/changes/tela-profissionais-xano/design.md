# Design

## Decisões

- Implementar a tela isolada em `sorrisomais/pagina_profissionais_xano.py`; a navegação será integrada pelo responsável pela composição do app.
- Obter a credencial da sessão existente e carregar os dados usando exclusivamente `listar_opcoes_agenda`. Mostrar apenas a coleção `profissionais`, sem consultar outra API.
- Usar cartões simples com iniciais e nome, em colunas responsivas. O indicador “Ativo” decorre do contrato que retorna apenas cadastros ativos; nenhum atributo adicional será inferido ou exibido.
- Não manter uma lista de resultados anterior após erro. Apresentar mensagem segura e estado de carregamento pelo Streamlit.
- Manter somente a lista de Profissionais bem-sucedida em cache de sessão por 20 segundos; invalidar ao trocar o token e oferecer atualização manual. Nunca conservar cache após falha.
- Não incluir ações de cadastro ou gerenciamento: não fazem parte do contrato desta entrega.

## Verificação

Testar lista, resposta vazia, falha de API, sessão ausente e perfil sem acesso com doubles de interface e cliente, sem chamadas de rede.
