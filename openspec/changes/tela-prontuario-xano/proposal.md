# Tela de histórico individual do Prontuário

## Objetivo

Conectar a tela de histórico individual do Prontuário ao Xano, apresentando Registros Clínicos e Consultas retornados dentro do escopo da Conta de Acesso autenticada.

## Escopo

- Usar somente `GET /consultas` e `GET /registros-clinicos` existentes.
- Permitir selecionar Paciente a partir dos dados recebidos por essas rotas.
- Apresentar estados de carregamento, erro, lista vazia e histórico vazio.
- Restringir a apresentação clínica na interface a Contas com perfil Paciente ou Profissional, mantendo o Xano como autoridade de autorização.

## Fora do escopo

- Criar ou alterar endpoints, autenticação, dados ou regras do Xano.
- Criar, retificar ou excluir Registros Clínicos.
- Apresentar Consultas ou nomes de Profissionais não retornados pelos contratos.
