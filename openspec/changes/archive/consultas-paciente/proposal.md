# Consultas do Paciente

## Por quê

O Paciente precisa acompanhar as próprias Consultas passadas e futuras conforme previsto no modelo de domínio.

## O que muda

- Criar uma tela Streamlit isolada que consulta `GET /consultas` com a Conta de Acesso autenticada.
- Separar as Consultas futuras e passadas e apresentar somente dados administrativos da Consulta.
- Exibir orientação para solicitar cancelamento à clínica.

Fora do escopo: agendamento, cancelamento, informação clínica, novo contrato de API ou alteração das permissões do Xano.

## Review

Escopo revisado: módulo isolado e testes unitários de tela; a integração à navegação depende da composição de acesso do Paciente e será feita pelo módulo principal.
