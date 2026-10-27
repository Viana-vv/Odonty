# Design: Atualização do cache após cadastro

No caminho de resposta 201 validada por `ClienteXano.cadastrar_paciente`, invalidar o namespace `pacientes` por meio de `cache_xano.invalidar_cache`. A chamada não recebe nem persiste o token. Enquanto o módulo compartilhado não estiver presente neste branch, a integração conserva um ponto local de invalidação da chave de sessão usada pela listagem, para que o branch permaneça executável; a coordenação deve reconciliar com a API comum antes do merge.

Nenhuma invalidação ocorre no `except` ou em resultado incerto. O estado `pac_pendente`, inclusive `operacao_id`, continua preservado para reenvio idempotente. A rota POST e seus contratos permanecem inalterados.

A verificação usa AppTest com cliente mockado e cache previamente populado, confirma chamada única ao POST e que o cache foi removido após sucesso. O teste real isolado já exercita a rota publicada em apigroup temporário para Administrador e Recepcionista; não requer novos dados reais.
