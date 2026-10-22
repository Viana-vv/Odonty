## Context

A proposta e os requisitos estão em `proposal.md` e `specs/interface-pacientes/spec.md`. O modo conectado usa módulos Streamlit por área e o cliente existente valida a resposta de `listar_opcoes_agenda`. Esta change habilita Contas de Acesso ativas com perfil Paciente nas rotas existentes de autenticação e identidade para acesso a Prontuários; as rotas clínicas do Xano continuam responsáveis por validar vínculo ativo e escopo dos dados.

## Goals / Non-Goals

**Goals:** compor uma tela responsiva inspirada na hierarquia visual da referência aprovada, adaptada aos campos mínimos do contrato existente; isolar a renderização em um módulo próprio; conectar módulos disponíveis ao roteamento comum sem acoplar suas implementações.

**Non-Goals:** implementar o conteúdo das telas de Profissionais, Prontuários, Procedimentos ou Nova Consulta; ampliar o contrato da API; criar operações de cadastro, edição, inativação ou consulta de detalhes.

## Decisions

- A tela chamará somente `cliente.listar_opcoes_agenda(token)` e consumirá o grupo `pacientes`, mantendo o cliente responsável pela validação do contrato. Uma rota exclusiva de listagem exigiria mudança de backend fora do escopo autorizado.
- A referência contém campos que a rota não retorna. A tabela será simplificada para identificador e nome, com busca somente pelo nome; não haverá placeholders nem chamadas a outras rotas.
- A função de renderização ficará em `sorrisomais/pagina_pacientes_xano.py`; `navegacao.py` manterá o mapa de módulos e `paginas_equipe.py` fará o despacho comum.
- A resposta será mantida apenas na sessão Streamlit por até 20 segundos para que a busca local e outros reruns não repitam o GET `/agenda/opcoes`. A ação Atualizar força uma nova leitura; falhas não são armazenadas, e a sessão limpa o cache ao sair ou expirar.
- O menu conectado resolverá módulos por um mapa de nomes conhecido e só habilitará áreas cujos módulos existirem. A guarda de perfil será aplicada tanto no menu quanto no despacho de uma área recebida via estado da sessão.
- Pacientes podem abrir somente a área Prontuários entre as áreas conectadas; o módulo e o Xano mantêm a consulta limitada ao escopo próprio e aos Registros Clínicos liberados.
- A autenticação Xano reconhece uma Conta de Acesso ativa com perfil Paciente para que ela alcance a aplicação; cada rota de dados clínicos continua validando o vínculo ativo com o Paciente e restringindo conteúdo liberado ao próprio titular.
- Atalhos a Nova Consulta na Visão geral e na Agenda serão exibidos a Administrador e Recepcionista, e habilitados somente quando o módulo estiver disponível. O botão de formulário já existente na Agenda será preservado.
- Os testes de UI simularão o cliente e a sessão Streamlit; nenhuma requisição real de rede será realizada.

## Risks / Trade-offs

- A rota de opções também fornece dados de Profissionais e Procedimentos; o cliente valida esses grupos como parte do contrato. A tela usa somente `pacientes` e não altera a rota.
- Como a API retorna somente registros elegíveis e não permite paginação, a busca é local sobre os itens recebidos; a interface não promete busca em campos ausentes.
- Módulos que outros agentes ainda não tenham criado continuarão indisponíveis; o roteamento não incluirá stubs que aparentem ser telas funcionais.
