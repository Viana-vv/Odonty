## Why

A equipe já pode consultar e cadastrar Pacientes, mas não consegue corrigir seus dados cadastrais pela aplicação. A edição precisa carregar e validar os dados no Xano e preservar consultas e histórico clínico vinculados.

## What Changes

- Adicionar leitura individual e atualização parcial de dados cadastrais de um Paciente para Administrador e Recepcionista autenticados e autorizados.
- Permitir editar nome, nascimento, CPF, telefone, celular e e-mail, com validações equivalentes às do cadastro e proteção contra CPF duplicado.
- Integrar a edição ao Streamlit, com mensagens compreensíveis, sem expor respostas técnicas ou dados pessoais em logs.
- Preservar prontuário, consultas, registros clínicos e exames; não permitir editar observações de saúde nesta tela administrativa.

## Capabilities

### New Capabilities

- `edicao-paciente`: leitura e edição autorizadas dos dados cadastrais de um Paciente.

### Modified Capabilities

Nenhuma.

## Impact

- Xano: novas rotas REST autenticadas para buscar e atualizar Paciente por identificador, autorizadas no backend.
- Streamlit: cliente da API, formulário de edição e navegação a partir da listagem.
- Testes: contratos unitários em Python e JavaScript para cada rota, sem chamadas reais à rede.
- Referência visual `12-editar-paciente.png`: manter o padrão visual do modal e omitir “Observações de saúde”, que não pode ser alterado por equipe administrativa.

## Fora de escopo

- Editar observações clínicas, prontuário, registros clínicos, consultas, exames, situação do cadastro ou Conta de Acesso.
- Alteração de dados pelo Paciente ou Profissional nesta interface.
- Publicação no Xano remoto sem ambiente de teste autorizado.
