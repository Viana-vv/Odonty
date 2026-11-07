## MODIFIED Requirements

### Requirement: Proteção de credenciais
O sistema SHALL NOT expor senhas, tokens e segredos em código versionado, URLs, logs ou mensagens de erro, ressalvada exclusivamente a presença em URL do token próprio de redefinição nas condições abaixo. A senha SHALL NOT ser persistida após o processamento da autenticação. Exclusivamente para redefinicao-senha, um token próprio de finalidade única, imprevisível, válido por no máximo 15 minutos e de uso único SHALL poder integrar o link destinado ao titular após aprovação expressa desta alteração e verificação das proteções da implantação. Todas as demais classes de tokens e segredos permanecem proibidas em URLs. Esse token SHALL NOT autenticar uma sessão e SHALL ser removido da URL visível na primeira captura, sem persistência em arquivos, caches globais ou armazenamento do navegador. Logs da cadeia inteira e mensagens de erro SHALL NOT registrar esse token ou o link completo. A remoção da URL SHALL NOT ser apresentada como garantia de apagamento de histórico ou de registros anteriores.

#### Scenario: Erro com dados sensíveis
- **WHEN** uma resposta técnica contém informações sensíveis
- **THEN** a interface e os registros de diagnóstico não reproduzem essas informações

#### Scenario: Token de sessão em URL
- **WHEN** qualquer fluxo tenta transportar uma credencial de sessão ou administrativa em uma URL
- **THEN** a operação é impedida, sem aplicar a exceção restrita de redefinição

#### Scenario: Link específico sem condições aprovadas
- **WHEN** a exceção não foi aprovada ou a implantação não impede exposição em logs e referências externas
- **THEN** o envio do link com token permanece desabilitado e nenhum fluxo alternativo é ativado silenciosamente
