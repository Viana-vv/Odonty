# Design: histórico individual do Prontuário

## Dados e autorização

A tela obtém a credencial da sessão Streamlit e chama `listar_consultas` e `listar_registros_clinicos`. Não envia filtros de Paciente derivados de entrada livre. A descoberta e a seleção usam identificadores e nomes retornados pelas rotas; se o nome não estiver disponível, a interface mostra somente o identificador retornado. A lista de Registros Clínicos recebida já está restrita pelo Xano ao Profissional autenticado ou aos Registros liberados do Paciente autenticado. A interface aplica o filtro visual do Paciente selecionado, sem tratar isso como autorização.

Contas administrativas não recebem conteúdo clínico, de acordo com o contrato de Registros Clínicos. A tela não registra conteúdo clínico em logs, não usa dados de demonstração e não cria autor, nome ou Consulta ausentes da resposta.

## Apresentação

Seguir a composição da referência `13-prontuario-individual.png`: título e descrição, seletor de Paciente, lista lateral de Pacientes recentes e histórico em linha do tempo. No Streamlit, usar colunas responsivas e cartões simples. Como o contrato de Registros Clínicos não inclui nome do Profissional, não apresentar autoria nominal. Exibir conteúdo, data e identificador do Registro Clínico apenas quando retornados.

O carregamento acontece em uma operação com indicador visual. Falhas de API exibem mensagem segura sem mostrar exceções técnicas. Coleções vazias informam que não há histórico disponível.

## Verificação

Testes de interface usam cliente simulado sem rede para sucesso, acesso negado, erro, vazio e seleção. Os contratos GET permanecem inalterados e já têm cobertura Python e JavaScript.

## Limitação de integração

Na validação conjunta, o Xano conectado respondeu HTTP 404 a `GET /registros-clinicos`, embora o export local da rota exista. Portanto, essa rota local não está publicada no Xano conectado e a tela ainda não pode ser considerada funcional em produção. Não criar endpoint alternativo nem inferir outro caminho; a publicação e a validação do contrato existente precisam ocorrer antes dessa conclusão.

O cliente `ClienteXano.listar_registros_clinicos` também normaliza a resposta sem preservar `registrado_em`, embora o export local contenha esse campo. A tela omite a data enquanto ela não estiver disponível no objeto retornado pelo cliente. Incluir a data requer uma alteração separada ao cliente da API, fora do escopo isolado desta tela.
