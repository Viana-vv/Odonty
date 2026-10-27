# listagem profissionais Specification

## Purpose

Restaurar na especificação vigente os requisitos aprovados nos deltas arquivados para a capacidade `listagem-profissionais`.

## ADDED Requirements

### Requirement: Consultar Profissionais ativos
O sistema SHALL exibir a lista fornecida pelo Xano usando o contrato existente `GET /agenda/opcoes`, sem criar endpoints ou apresentar atributos que não sejam identificador e nome.

#### Cenário: Lista carregada
- **WHEN** Administrador ou Recepcionista abre a área Profissionais e o Xano retorna Profissionais
- **THEN** a interface apresenta os nomes em cartões responsivos e usa os identificadores apenas para distinguir os cartões

#### Cenário: Lista vazia
- **WHEN** o Xano retorna uma coleção de Profissionais vazia
- **THEN** a interface informa que não há Profissionais ativos para exibir

#### Cenário: Reexecução da tela
- **WHEN** Streamlit reexecuta a tela dentro de 20 segundos sem troca de sessão
- **THEN** a lista bem-sucedida é reutilizada sem nova chamada ao Xano, e a equipe pode solicitar atualização manual

#### Cenário: Falha ao consultar
- **WHEN** a API falha ou a sessão não pode acessar o recurso
- **THEN** a interface apresenta mensagem compreensível sem exibir dados antigos como atuais

#### Cenário: Sessão expirada
- **WHEN** o Xano responde com HTTP 401 ao consultar a lista
- **THEN** a interface limpa a sessão local e informa que é necessário entrar novamente

#### Cenário: Acesso negado pelo Xano
- **WHEN** o Xano responde com HTTP 403 ao consultar a lista
- **THEN** a interface informa a falta de permissão e preserva a sessão local

#### Cenário: Acesso por perfil não autorizado
- **WHEN** uma Conta de Acesso sem perfil Administrador ou Recepcionista abre diretamente a tela
- **THEN** a tela não solicita nem apresenta a lista, mantendo a autorização definitiva no Xano

