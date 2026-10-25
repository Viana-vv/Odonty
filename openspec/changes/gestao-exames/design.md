## Context

O domínio já possui Consulta, Paciente e Profissional, mas não há fluxo completo de Exame no frontend. A entrega precisa manter autenticação e autorização no Xano, usar REST e respeitar o plano atual sem armazenamento privado de arquivos.

## Goals / Non-Goals

**Goals:**

- Criar contrato REST isolado para listar, solicitar e atualizar Exames.
- Aplicar filtragem por perfil e vínculo de consulta no backend.
- Exibir uma tela Streamlit responsiva no padrão visual Sorriso Mais.
- Cobrir os contratos com testes Python e JavaScript sem chamadas de rede.

**Non-Goals:**

- Upload, armazenamento ou download de anexos.
- Alteração de tabelas clínicas existentes fora do escopo de Exames.
- Expor resultado a perfis sem autorização.

## Decisions

1. **API isolada em módulo próprio.** O cliente REST de exames ficará separado para reduzir conflito com outros agentes e facilitar testes por rota.
2. **Vínculo obrigatório com Consulta na solicitação.** O Xano valida que o profissional solicitante, Paciente e Consulta formam um relacionamento autorizado; isso evita solicitações clínicas sem contexto.
3. **Estados controlados no backend.** O Xano aceitará apenas `Solicitado`, `Realizado`, `Resultado disponível`, `Cancelado` e `Não realizado`, com transições validadas. O frontend apenas apresenta os estados.
4. **Sem arquivo nesta entrega.** A tela não terá componente de upload nem campo de URL. A decisão evita links públicos e respeita a limitação do plano atual.
5. **Projeção por perfil.** A resposta será reduzida ao necessário para cada perfil, e mensagens de erro não conterão dados clínicos.

6. **Histórico append-only de situações.** Criar tabela aditiva `exame_situacao_historico`; a solicitação registra o estado inicial e cada avanço grava evento anterior/novo, autor e data na mesma transação da atualização. Nunca editar nem excluir esses eventos. O registro atual de Exame mantém a projeção mais recente.
7. **Transições e concorrência.** Permitir `Solicitado` para `Realizado`, `Cancelado` ou `Não realizado`, e `Realizado` para `Resultado disponível`. Estados finais não podem regredir. A realização deve ocorrer entre a solicitação e o momento atual; liberar resultado exige texto não vazio. `exame_situacao_controle`, com índice único por Exame, serializa alterações concorrentes sem editar duas vezes o registro clínico.

## Risks / Trade-offs

- [Resultado clínico exposto por filtro incorreto] → centralizar filtros e autorização no Xano e testar paciente de outro paciente, profissional não relacionado e perfil sem permissão.
- [Conflito de rate limit do plano gratuito] → testes remotos, quando disponíveis, devem ser sequenciais com intervalo mínimo de aproximadamente três segundos; os testes unitários não acessam a rede.
- [Necessidade futura de anexos] → manter o contrato sem campos públicos de arquivo; uma futura mudança deverá adotar armazenamento privado e URLs assinadas.

## Migration Plan

1. Criar tabela/rotas de Exames no ambiente Xano de teste.
2. Publicar o cliente e a tela na branch da atividade.
3. Validar testes automatizados e, se houver ambiente seguro, executar cenários remotos com dados fictícios.
4. Em rollback, remover somente os artefatos da change no ambiente de teste; nenhuma alteração é aplicada à branch principal nesta etapa.
