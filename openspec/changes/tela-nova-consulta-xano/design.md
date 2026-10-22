# Design: Nova Consulta como tela própria

## Decisão

Criar um módulo Streamlit independente com `renderizar(cliente, conta)`. O módulo recebe o cliente REST e a Conta de Acesso em vez de acoplar a tela ao roteador. A autorização visual usa os perfis da Conta de Acesso, enquanto o Xano continua sendo a autoridade final.

## Integração

- `GET /agenda/opcoes`: carregar Pacientes, Profissionais e Procedimentos ativos por `cliente.listar_opcoes_agenda`.
- `GET /disponibilidades`: carregar horários por Profissional e limites de data via `cliente.listar_disponibilidades`.
- `POST /consultas`: criar a Consulta via `cliente.agendar_consulta`.
- Reutilizar `ErroAcesso` para tratar erros. Nenhum endpoint ou regra de negócio novo será criado.

## Interface e estado

Seguir o modal da referência como formulário de página: título e instrução, seleção de Paciente, data e horário, Profissional e Procedimentos, observação administrativa e ações de cancelar/agendar. Usar estado da sessão para conservar valores durante falhas e limpar o formulário após criação confirmada.

Os horários devem ser apresentados no fuso `America/Sao_Paulo`. A tela não presume elegibilidade por conta própria: a lista recebida e a resposta do Xano são autoritativas. Conflitos mantêm a tela preenchida para permitir outra escolha.

## Testes

Testes unitários isolados simulam os métodos do cliente, sem rede real. Cobrir sucesso, carregamento e falha, permissões, campos ausentes e conflito.
