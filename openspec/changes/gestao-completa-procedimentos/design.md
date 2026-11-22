## Context

O catálogo atual usa `GET /procedimentos` e é somente leitura. O agendamento já aceita múltiplos `procedimento_ids`, enquanto a Consulta possui vínculos `ConsultaProcedimento` e já existe leitura dos vínculos e registro de realização. A mudança deve completar esses fluxos sem substituir o modelo existente.

## Goals / Non-Goals

**Goals:**

- Reutilizar `Procedimento` e `ConsultaProcedimento` como entidades distintas.
- Centralizar autorização, validação de situação e preservação histórica no Xano.
- Manter interfaces separadas para catálogo administrativo e atendimento profissional.
- Atualizar o catálogo e os vínculos sem apagar registros históricos.

**Non-Goals:**

- Pagamentos ou cobrança.
- Campos odontológicos por dente ou região nesta etapa.
- Acesso de Paciente ao gerenciamento de Procedimentos.
- Exclusão física.

## Decisions

- **API REST separada por responsabilidade:** adicionar rotas de catálogo para POST/PATCH e rotas de ConsultaProcedimento para inclusão e transição de situação. Isso evita usar o endpoint de leitura como mutação.
- **Inativação lógica:** o campo de situação/ativo será alterado no Procedimento, mantendo os vínculos existentes. Procedimentos inativos não serão retornados nas opções de novas Consultas.
- **Autorização no backend:** Administrador e Recepcionista gerenciam o catálogo; Profissional também pode criar Procedimentos para uso no atendimento, mas não edita nem inativa o catálogo. Somente Profissional do escopo da Consulta altera vínculos clínicos e realiza/cancela Procedimentos.
- **Interface por contexto:** o catálogo terá formulário/modal para equipe administrativa; a tela de Procedimentos da Consulta terá seletor de Procedimento ativo e cards de situação para o Profissional.
- **Compatibilidade de dados:** o cliente aceitará os campos opcionais do catálogo sem quebrar respostas legadas, mas rejeitará respostas inválidas de contratos obrigatórios.

## Risks / Trade-offs

- [Contratos Xano ainda não existentes para todas as mutações] → definir e testar cada rota antes de conectar os controles do Streamlit.
- [Vínculos duplicados] → validação transacional no Xano por Consulta e Procedimento.
- [Procedimento inativado com histórico] → separar listagem de opções ativas da listagem histórica de vínculos.
- [Permissão clínica indevida] → validar profissional da Consulta e perfil em cada endpoint, sem confiar no frontend.
- [Procedimento criado pelo Profissional sem dados suficientes] → exigir pelo menos nome válido no Xano e preencher os demais campos opcionais com valores neutros definidos no contrato.

## Migration Plan

1. Criar e validar as rotas Xano sem alterar dados existentes.
2. Atualizar cliente Python e contratos JavaScript/Python.
3. Atualizar telas e navegação por perfil.
4. Verificar cenários de autorização, duplicidade, inativação e histórico.

Rollback: desabilitar os novos controles e rotas de mutação; não remover dados históricos nem vínculos existentes.
