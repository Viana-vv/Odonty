# consulta-contas-acesso Specification

## Purpose
Restaurar na especificação vigente os requisitos aprovados nos deltas arquivados para a capacidade `consulta-contas-acesso`.

## Requirements

### Requirement: Listagem de Contas de Acesso para equipe administrativa
O sistema MUST permitir que Administrador e Recepcionista consultem Contas de Acesso e negar a listagem aos demais perfis.

#### Cenário: Administrador ou Recepcionista autorizado
- DADO que a Conta de Acesso autenticada está ativa e possui perfil Administrador ou Recepcionista
- QUANDO consulta a listagem
- ENTÃO o sistema retorna somente id, nome, e-mail, perfis e situação
- E não retorna senha, hash, token ou outros campos

#### Cenário: Perfil sem autorização
- DADO que a Conta de Acesso autenticada não possui perfil administrativo
- QUANDO consulta a listagem
- ENTÃO o Xano responde acesso negado sem retornar Contas de Acesso

### Requirement: Tela informativa e somente leitura
A tela MUST exibir as Contas de Acesso autorizadas sem oferecer controles para editar perfis ou situação, redefinir credenciais ou criar contas.

#### Cenário: Lista vazia
- QUANDO a consulta autorizada não encontra Contas de Acesso
- ENTÃO a tela informa que não há Contas de Acesso para exibir

#### Cenário: Falha de consulta
- QUANDO a API falha
- ENTÃO a tela mostra uma mensagem compreensível sem detalhes técnicos ou dados sensíveis
