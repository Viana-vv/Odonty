# Design: Preservar a rota e invalidar cache após confirmação

Em `paginas_equipe.renderizar`, tratar `pagina == "paciente"` como rota interna com topbar, sem tentar carregá-la por `navegacao.carregar_modulo_xano`. O modal existente continua sendo renderizado após a área de conteúdo; a rota permanece no estado da sessão até completar o POST.

No retorno 201 validado por `ClienteXano.cadastrar_paciente`, invalidar namespaces `pacientes` e `agenda/opcoes` via `cache_xano.invalidar_cache`. A lista usa `cache_xano.carregar_cache` no namespace `pacientes`, com a consulta como loader e o botão Atualizar como `force=True`. Tokens não são persistidos pelo helper.

Nenhuma invalidação acontece no `except`: timeout, falha de rede, resposta incompatível e rejeição preservam comportamento atual. Resultado incerto conserva `pac_pendente` e `operacao_id` para reenvio manual.

Verificação: AppTest do fluxo pela listagem, formulário, POST mockado, navegação de volta, novo GET único e Paciente visível; testes existentes de sucesso e resultado incerto; teste opt-in contra POST publicado como Administrador e Recepcionista com verificação de persistência por Metadata API e limpeza/inativação.
