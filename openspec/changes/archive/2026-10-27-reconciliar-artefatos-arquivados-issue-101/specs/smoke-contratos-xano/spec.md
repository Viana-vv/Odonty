# smoke contratos xano Specification

## Purpose

Restaurar na especificação vigente os requisitos aprovados nos deltas arquivados para a capacidade `smoke-contratos-xano`.

## ADDED Requirements

### Requirement: Evidência separada
O roteiro MUST distinguir validação local sem rede de validação remota e MUST registrar bloqueios sem atribuir resultados não observados.

#### Cenário: Relato verificável
- **WHEN** os testes locais ou remotos terminam
- **THEN** o relatório identifica os comandos e resultados executados nesta rodada, a cadência remota quando aplicável e os cenários pendentes

### Requirement: Smoke remoto isolado e controlado
A verificação remota MUST ser explicitamente ativada e usar somente um grupo Xano temporário segregado autorizado, credenciais administrativas fornecidas por variáveis de ambiente e dados fictícios. MUST NOT publicar, alterar ou executar operações de escrita no grupo principal automaticamente.

#### Cenário: Configuração administrativa ausente
- **WHEN** falta Metadata URL, identificador do workspace, token ou alvo segregado confirmado
- **THEN** nenhuma chamada remota é feita, o bloqueio é registrado e somente validações locais sem rede são executadas

#### Cenário: Rate limit
- **WHEN** a verificação inicia chamadas remotas
- **THEN** não inicia mais de 10 requisições em qualquer janela móvel de 20 segundos e aguarda entre chamadas; respostas 429 pausam e só repetem chamadas seguras ou operações de teste desenhadas para repetição segura

#### Cenário: Respostas de contrato
- **WHEN** os cenários aplicáveis são executados no grupo temporário
- **THEN** verificam 401, 403, 400, 404 e 409, sucesso e ausência de alterações indevidas; Reagendamento também verifica rollback integral induzido e conflitos

#### Cenário: Limpeza segura
- **WHEN** a execução termina ou falha
- **THEN** remove somente artefatos temporários de sua propriedade e inativa somente contas fictícias temporárias, preservando dados e históricos preexistentes

