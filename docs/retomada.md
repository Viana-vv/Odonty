# Ponto de retomada — 10/10/2026

O Odonty é um projeto acadêmico em conjunto: o usuário e mais dois amigos. As mudanças devem ficar prontas para revisão do grupo, seguindo o AGENTS.md e o fluxo OpenSpec.

## Trabalho realizado nesta conversa

- Leitura do AGENTS.md, README.md, configuração OpenSpec, documentos de contexto e estrutura existente.
- Atualização do README.md para refletir a Agenda conectada, verificações pendentes, módulos atuais, changes não arquivadas e referência correta ao mascote.
- Diagnóstico da inicialização: `.venv` aponta para um Python 3.10 ausente; `.venv-win` funciona com Python 3.12 e Streamlit 1.64.0.
- Atualização dos comandos Windows no README.md para usar `.venv-win`.
- Inicialização do Streamlit na porta 8501 e confirmação de resposta `ok` em `/_stcore/health`. Isso não verifica login nem os fluxos da interface.

Nenhuma implementação funcional, alteração no Xano, commit ou publicação no GitHub foi realizada nesta conversa. As alterações estão salvas localmente e ainda precisam de revisão do grupo. O servidor pode precisar ser iniciado novamente na próxima sessão.

## Executar no Windows

```powershell
$env:XANO_API_BASE_URL = "https://x8ki-letl-twmt.n7.xano.io/api:sorriso-acesso:v1"
.\.venv-win\Scripts\python.exe -m streamlit run app.py
```

Abrir http://localhost:8501. O login exige uma Conta de Acesso fictícia ativa no Xano. Não há configuração administrativa da Metadata API no terminal consultado; a senha original não pode ser recuperada do campo password. Não guardar credenciais neste documento.

## Pendências para retomada

- Revisar as alterações documentais com o grupo.
- Conferir a Agenda conectada nos perfis Administrador, Recepcionista e Profissional, incluindo exibição após correção de leitura e cancelamento após correção do PATCH, conforme os registros da change `tela-agenda-xano`.
- `gestao-disponibilidades-site` tem tarefas marcadas como concluídas, mas ainda não está arquivada.
- `sessao-prolongada-equipe` permanece proposta, com tarefas pendentes. A sessão atual continua com prazo de uma hora.
- Consultar novamente os documentos e as changes antes de novas alterações; este registro não substitui suas especificações.

## Verificação desta conversa

O diff do README.md foi revisado e `git diff --check` passou. Nenhuma suíte de testes foi executada, pois as alterações foram documentais. Os registros de testes anteriores citados no README e nas changes não são novas verificações desta conversa.
