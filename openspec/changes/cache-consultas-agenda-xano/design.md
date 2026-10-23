## Context

A Agenda usa `listar_consultas` com intervalo de um dia e aplica busca e situação no Streamlit. O Streamlit reroda a página após interações; sem cache, cada rerun repete a mesma leitura. O contrato Xano e sua autorização permanecem inalterados.

## Goals / Non-Goals

**Goals:**
- Reutilizar as Consultas da mesma data durante vinte segundos, vinculadas ao hash do token da Conta de Acesso.
- Manter os filtros de busca e situação locais e invalidar respostas após alterações.
- Aplicar intervalo de nova tentativa após falha e remover o cache no logout.

**Non-Goals:**
- Alterar endpoints, autorização, modelo de dados ou resultados de negócio.
- Cachear respostas de erro ou compartilhar dados entre Contas de Acesso.

## Decisions

- Guardar respostas bem-sucedidas em `st.session_state`, agrupadas por Conta de Acesso e data, com duração de vinte segundos. Reruns que mudam apenas busca ou situação reutilizam a lista carregada.
- Limitar o cache a sete datas recentes por sessão para manter seu tamanho previsível.
- Apagar o cache após atualização de situação, agendamento, criação de Disponibilidade, troca de Conta de Acesso e logout. Ao receber uma falha, não armazenar dados e aguardar vinte segundos antes de nova tentativa.
- Manter toda validação e autorização no Xano; o cache somente evita chamadas GET redundantes.

## Risks / Trade-offs

- A lista pode ficar desatualizada por até vinte segundos quando outra Conta de Acesso altera uma Consulta; invalidar imediatamente após ações feitas nesta sessão e expirar automaticamente.
- Uma falha bloqueia novas tentativas da Agenda por vinte segundos; mostrar mensagem de espera e não mascarar a falha como lista vazia.

## Migration Plan

Não há migração de dados nem alteração do Xano. O rollback consiste em remover o cache de sessão e voltar à leitura existente por renderização.
