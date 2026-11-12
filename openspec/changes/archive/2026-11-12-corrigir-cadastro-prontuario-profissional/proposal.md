# Corrigir cadastro de Registro Clínico no Prontuário pelo Profissional

## Contexto

Na tela de Prontuários, o Profissional autenticado consegue abrir Nova evolução,
mas o cadastro pode falhar porque o endpoint usa a variável da Consulta
explicitamente selecionada mesmo quando o Paciente foi validado por uma Consulta
encontrada no escopo do Profissional. A interface também usa uma mensagem 404
genérica que não identifica a possibilidade de Prontuário ausente.

## Objetivo

Permitir que o Profissional registre um Registro Clínico no Prontuário do
Paciente autorizado, com ou sem Consulta selecionada no formulário, mantendo a
validação de escopo no Xano.

## Escopo

- corrigir a resolução do identificador de Consulta no POST de Registros Clínicos;
- manter a exigência de vínculo entre Profissional e Paciente quando não houver
  Consulta explícita;
- atualizar a mensagem segura da interface para refletir todos os vínculos
  validados;
- adicionar testes locais para os caminhos corrigidos.

## Fora do escopo

- alterar permissões do Xano;
- criar novos perfis, tabelas ou rotas;
- permitir registro para Paciente fora da agenda do Profissional;
- usar dados reais ou fazer chamadas reais ao Xano nos testes.

