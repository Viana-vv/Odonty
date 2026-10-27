## Why
As páginas Streamlit repetem leituras GET do Xano após reruns e navegação, enquanto caches existentes são fragmentados e inconsistentes. Um cache sob demanda, persistido somente na sessão e isolado por Conta de Acesso, reduz chamadas sem pré-carregar dados nem misturar informações privadas.

## What Changes
- Criar helper público `carregar_cache(state, token, namespace, loader, force=False)` e `invalidar_cache(state, namespaces=None)`.
- Usar chave de escopo derivada por hash unidirecional do token; nunca persistir o token no cache/chaves ou logs.
- Cachear somente respostas válidas após sucesso do loader, sem TTL automático; force ou mutação bem-sucedida busca dados novos.
- Limpar dados privados em 401/403, logout, expiração e troca de Conta de Acesso/perfil.
- Integrar as leituras GET da UI no helper e invalidar namespaces dependentes após mutações.
- Preservar os contratos REST Xano e excluir a tela/módulo específico de cadastro de Paciente desta integração coordenada.
- Adicionar testes sem rede para chamadas, navegação, refresh, invalidação e erros.

## Capabilities
### New Capabilities
- `cache-leituras`: cache sob demanda de leituras GET autenticadas entre navegações Streamlit.

### Modified Capabilities
Nenhuma.

## Impact
Módulos Python em `sorrisomais/`, integração do ciclo de sessão, páginas que consomem endpoints GET, testes Python e JavaScript por rota, e documentação OpenSpec. Nenhuma mudança de endpoint ou backend Xano. Dados privados permanecem somente em `st.session_state`.
