## Contexto

O cadastro já é exibido no modal `modal-profissional`. O formulário consulta especialidades pelo endpoint existente e envia o cadastro pelo `POST /profissionais`. Esse POST exige nome, e-mail, senha, CRO e especialidade; o Xano valida a sessão e o perfil Administrador e cria Profissional e Conta de Acesso na mesma transação. O refinamento não modifica esse contrato nem a autorização.

A referência 10 apresenta cabeçalho com título e descrição, nome em largura total, campos em pares e ações no rodapé. Como os campos funcionais atuais incluem senha inicial e confirmação, eles permanecem no formulário e serão organizados em pares abaixo dos campos principais.

## Decisões

- Reutilizar os containers, chaves CSS e formulário Streamlit existentes para preservar navegação, callbacks e estado.
- Ajustar ordem e colunas apenas na renderização: nome em largura total; especialidade com CRO; e-mail com senha inicial; confirmação de senha em largura compatível, sem remover campo funcional.
- Usar CSS compartilhado para dimensão, espaçamento e breakpoint móvel; manter `max-height` com rolagem e uma coluna em larguras estreitas.
- Não adicionar telefone: o contrato atual não o aceita e a referência não autoriza mudar o payload.
- Preservar fluxo de sucesso/erro, proteção contra envio duplicado, limpeza de senha e permissões existentes.

## Riscos

- O Streamlit pode alterar os seletores estruturais; manter seletores restritos à chave `modal-profissional`.
- O conjunto de campos diverge parcialmente da referência; a compatibilidade do formulário e do contrato prevalece.

## Verificação

Executar testes de interface e contratos Python/JavaScript já existentes sem chamadas reais de rede. A inspeção visual manual do modal em largura ampla e estreita depende de execução local e deve ser confirmada pelo grupo.
