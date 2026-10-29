# verificacao-autoatendimento-xano Specification

## Purpose
TBD - created by archiving change validar-autoatendimento-xano-publicado. Update Purpose after archive.

## Requirements

### Requirement: Verificar contratos publicados do autoatendimento
O projeto MUST oferecer um procedimento de integração opt-in contra o grupo Xano publicado real para verificar os contratos de autenticação e leitura usados pelo portal do Paciente. A verificação MUST usar somente Conta de Acesso e dados fictícios previamente provisionados, MUST NOT criar, alterar ou excluir dados, e MUST NOT imprimir nem persistir senha, token de sessão ou conteúdo clínico.

#### Scenario: Integração publicada habilitada com credenciais de teste
- **WHEN** a pessoa operadora habilita explicitamente a suíte e fornece configuração válida e credenciais fictícias por variáveis de ambiente
- **THEN** os testes verificam login, identidade, leituras de Consultas, Registros Clínicos e Exames, e logout contra o grupo principal publicado, removendo token da memória ao final

#### Scenario: Credenciais ou configuração ausentes
- **WHEN** a suíte real não está habilitada ou falta configuração obrigatória
- **THEN** o teste é ignorado ou interrompido com indicação clara do pré-requisito ausente, sem tentar credenciais inventadas e sem enviar requisição

#### Scenario: Conta sem autenticação ou sem autorização
- **WHEN** a API recebe requisição protegida sem sessão válida ou a Conta de Acesso não possui perfil Paciente autorizado
- **THEN** o Xano rejeita a operação e a verificação não expõe dados do Paciente ou detalhes sensíveis da resposta

#### Scenario: Dados próprios retornados
- **WHEN** a Conta de Acesso fictícia consulta os endpoints do portal
- **THEN** as respostas correspondem apenas ao Paciente vinculado à sessão, Registros Clínicos não liberados não são retornados e resultado de Exame é omitido até estar liberado
