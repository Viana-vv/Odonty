# Design: Nova Consulta como tela própria

## Decisão

Criar um módulo Streamlit independente com `renderizar(cliente, conta)`. O módulo recebe o cliente REST e a Conta de Acesso em vez de acoplar a tela ao roteador. A autorização visual usa os perfis da Conta de Acesso, enquanto o Xano continua sendo a autoridade final. Um seletor CSS escopado em `assets/estilos.css` aplica o cartão central e responsivo da referência sem alterar outros formulários.

## Integração

- `GET /agenda/opcoes`: carregar Pacientes, Profissionais e Procedimentos ativos por `cliente.listar_opcoes_agenda`.
- `GET /disponibilidades`: carregar horários por Profissional e limites de data via `cliente.listar_disponibilidades`.
- `POST /consultas`: criar a Consulta via `cliente.agendar_consulta`.
- Reutilizar `ErroAcesso` para tratar erros. Nenhum endpoint ou regra de negócio novo será criado.

## Interface e estado

Seguir o modal da referência como formulário de página: título e instrução, seleção de Paciente, data e horário, Profissional e Procedimentos, observação administrativa e ações de cancelar/agendar. Usar estado da sessão para conservar valores durante falhas e limpar o formulário após criação confirmada.

Os horários devem ser apresentados no fuso `America/Sao_Paulo`. As leituras usam cache curto limitado à sessão autenticada para evitar GET repetido em cada rerun; o botão Atualizar limpa esse cache. Respostas de erro não são armazenadas, e erros 401, 403 ou conflito invalidam os dados em cache. A tela não presume elegibilidade por conta própria: a lista recebida e a resposta do Xano são autoritativas. Conflitos mantêm a tela preenchida para permitir outra escolha.

As respostas bem-sucedidas das leituras são mantidas somente na sessão atual por até 20 segundos para evitar repetir chamadas em cada rerun do Streamlit. Erros não são cacheados; sessão expirada, conflito de agenda ou criação confirmada invalidam o cache.

## Testes

Testes unitários isolados simulam os métodos do cliente, sem rede real. Cobrir sucesso, carregamento e falha, permissões, campos ausentes e conflito.
