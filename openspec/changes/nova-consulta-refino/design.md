## Context

Veja `proposal.md` e `specs/interface-equipe/spec.md`. A tela conectada já implementa autorização de Administrador/Recepcionista, leituras GET, validação, submissão POST e tratamento dos estados de erro e vazio. A referência 08 é um modal com agrupamento visual e ações no rodapé; a tela Streamlit é integrada ao app, então o refinamento não deve recriar a Agenda nem imitar modal sem comportamento existente.

## Goals / Non-Goals

**Goals:**
- Reorganizar somente a apresentação dos controles existentes na tela integrada.
- Manter a sequência dependente: Data e Profissional definem a lista de Horários; seleção de Horário pode coexistir visualmente com Procedimentos.
- Reutilizar o layout responsivo nativo do Streamlit e estilos existentes.

**Non-Goals:**
- Criar modal, campos ou contratos novos.
- Alterar payloads, validações, permissões ou lógica no Xano.
- Modificar a Agenda ou a navegação geral.

## Decisions

- Manter todos os valores e widgets atuais, alterando apenas agrupamento, rótulos de apoio e espaçamento da composição do formulário. Isso reduz risco de mudança funcional.
- Agrupar Paciente em linha própria; Data e Profissional juntos; Horário e Procedimentos juntos; Observações em largura integral; ações no rodapé. Em telas menores, as colunas devem empilhar usando o comportamento padrão responsivo do Streamlit.
- Preservar Horário como campo dinâmico baseado em Data e Profissional. A aparência da referência não justifica alterar essa dependência ou adicionar campo de horário livre.
- Manter os caminhos de erro/estado vazio antes da renderização do formulário e os contratos `GET /agenda/opcoes`, `GET /disponibilidades` e `POST /consultas` intactos.

## Risks / Trade-offs

- [As colunas do Streamlit podem empilhar de modo diferente conforme a largura] → validar fluxo em teste de interface e fazer smoke visual em computador e celular.
- [Refinamento apenas de layout pode não ser suficiente para avaliar responsividade em AppTest] → registrar a inspeção visual manual como limitação, sem introduzir dependência de browser ou rede.

## Migration Plan

Sem migração de dados ou implantação de backend. Rollback: restaurar a composição anterior da função de renderização.
