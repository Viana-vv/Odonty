## ADDED Requirements

### Requirement: Opções utilizáveis com cadastros legados incompletos
O Xano SHALL retornar em GET `/agenda/opcoes` somente Pacientes e Procedimentos ativos com nome preenchido e Profissionais ativos com nome, CRO e vínculo positivo de Especialidade. Cadastros incompletos SHALL permanecer armazenados e não SHALL impedir leitura das opções válidas. O formato e as permissões administrativas SHALL ser preservados.

#### Scenario: Profissional sem nome
- **WHEN** Administrador ou Recepcionista abre Home ou Nova Consulta e existe um Profissional ativo sem nome ou CRO
- **THEN** as opções válidas são carregadas sem esse registro incompleto e sem mensagem genérica de conexão

#### Scenario: Nenhuma opção válida
- **WHEN** não existem cadastros ativos com os campos exigidos
- **THEN** a coleção correspondente fica vazia e a interface informa a ausência sem permitir envio incompleto

#### Scenario: Sem permissão
- **WHEN** uma Conta de Acesso sem perfil administrativo consulta as opções
- **THEN** o Xano recusa o acesso sem retornar opções
