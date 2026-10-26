## Context

Ver `proposal.md` e `specs/edicao-paciente/spec.md`. O cliente já implementa GET e PATCH, e os fontes Xano já contêm autorização para Administrador e Recepcionista. A instância publicada não tinha o PATCH e o GET publicado respondeu `ERROR_FATAL` com `Invalid pipe` durante teste com dados fictícios. O menu customizado da equipe é a primeira coluna de `layout-equipe`; atualmente não possui posicionamento fixo.

## Goals / Non-Goals

**Goals:** disponibilizar os contratos cadastrais existentes no grupo Xano da aplicação, validar o fluxo real como Recepcionista e manter a navegação da equipe acessível em telas longas de desktop.

**Non-Goals:** alterar o modelo de dados, permitir edição de dados clínicos, modificar permissões de Profissional ou redesenhar a navegação móvel.

## Decisions

- Corrigir a construção da resposta do GET usando valores opcionais inicializados e condicionais explícitas, evitando o pipe que falha em execução; publicar novamente a rota.
- Publicar o PATCH existente no mesmo grupo após compilar o fonte, mantendo sua checagem de sessão e perfil no Xano.
- Fixar a coluna Streamlit que contém o menu em desktop com CSS `position: sticky`; aplicar o posicionamento somente ao contêiner interno não funciona porque ele fica limitado pela altura da própria coluna. Limitar o menu ao viewport e permitir sua rolagem interna. Desativar esse posicionamento em telas estreitas para preservar a ordem atual.
- Na leitura para edição, validar a estrutura da resposta e a data, aceitando os campos de contato/CPF vazios em cadastros antigos. Manter a validação obrigatória completa no envio da atualização, para que seja possível abrir e completar esses cadastros.
- No teste visual, rolar o contêiner real `stMain` e confirmar que o conteúdo se deslocou antes de comparar a posição do menu. `window.scrollTo` não percorre a página interna do Streamlit e não serve como evidência dessa interação.
- Manter mensagens ao usuário seguras e usar os testes de contrato existentes para validar autorização, payload e tratamento de erros.

## Risks / Trade-offs

- A instância pode ter configuração diferente da branch local → compilar os fontes em grupo temporário e executar fluxo real com Conta de Acesso e Paciente fictícios antes da validação final.
- Se um contêiner ancestral aplicar `overflow` incompatível, `position: sticky` pode não aderir ao viewport → validar visualmente a tela longa em desktop e ajustar o seletor ao contêiner real.
- O teste real cria registros → gerar dados aleatórios fictícios, encerrar a sessão e inativar a Conta de Acesso e o Paciente de teste sem apagar histórico.
