# Design: histórico individual do Prontuário

## Dados e autorização

A tela obtém a credencial da sessão Streamlit e chama `listar_consultas` e `listar_registros_clinicos`. Não envia filtros de Paciente derivados de entrada livre. A descoberta e a seleção usam identificadores e nomes retornados pelas rotas; se o nome não estiver disponível, a interface mostra somente o identificador retornado. A lista de Registros Clínicos recebida já está restrita pelo Xano ao Profissional autenticado ou aos Registros liberados do Paciente autenticado. A interface aplica o filtro visual do Paciente selecionado, sem tratar isso como autorização.

Contas administrativas não recebem conteúdo clínico, de acordo com o contrato de Registros Clínicos. A tela não registra conteúdo clínico em logs, não usa dados de demonstração e não cria autor, nome ou Consulta ausentes da resposta.

## Apresentação

Seguir a composição da referência `13-prontuario-individual.png`: título e descrição, seletor de Paciente, lista lateral de Pacientes recentes e histórico em linha do tempo. No Streamlit, usar colunas responsivas e cartões simples. Como o contrato de Registros Clínicos não inclui nome do Profissional, não apresentar autoria nominal. Exibir conteúdo, data e identificador do Registro Clínico apenas quando retornados.

O carregamento acontece em uma operação com indicador visual. Falhas de API exibem mensagem segura sem mostrar exceções técnicas. Coleções vazias informam que não há histórico disponível. Para evitar chamadas repetidas nos reruns do Streamlit, respostas bem-sucedidas ficam em cache por 20 segundos na sessão, vinculadas a um fingerprint da credencial; falhas não são armazenadas e a limpeza da sessão remove o cache.

## Verificação

Testes de interface usam cliente simulado sem rede para sucesso, acesso negado, erro, vazio e seleção. Os contratos GET permanecem inalterados e já têm cobertura Python e JavaScript.

## Limitação de integração

O export da rota e da tabela `registro_clinico` inclui os GUIDs do ambiente Xano. O endpoint consulta primeiro pelo escopo obrigatório do Profissional ou do Paciente (incluindo `liberado_paciente=true`) e aplica os filtros opcionais no backend depois da consulta escopada. O principal validou no Xano: login Profissional HTTP 200; `GET /consultas` HTTP 200; `GET /registros-clinicos` autenticado HTTP 200 com coleção vazia e `Cache-Control: no-store`; perfil Administrativo HTTP 403; filtro `paciente_id=-1` HTTP 400; logout HTTP 204. As contas fictícias de teste e o Profissional associado foram inativados após a verificação. Não houve validação com um Paciente autenticado nem com Registros Clínicos existentes.

Limitação observada: `paciente_id=0` retornou HTTP 200 com coleção vazia em vez de HTTP 400, embora o export contenha validação `<= 0`. A causa dessa diferença ainda precisa ser investigada e testada no Xano antes de considerar concluída a validação desse filtro. Nenhuma credencial ou dado clínico de teste é documentado aqui.

O cliente `ClienteXano.listar_registros_clinicos` também normaliza a resposta sem preservar `registrado_em`, embora o export local contenha esse campo. A tela omite a data enquanto ela não estiver disponível no objeto retornado pelo cliente. Incluir a data requer uma alteração separada ao cliente da API, fora do escopo isolado desta tela.
