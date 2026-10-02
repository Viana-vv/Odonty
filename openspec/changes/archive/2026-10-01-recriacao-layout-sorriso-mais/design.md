## Context

Consulte `proposal.md` e `specs/interface-equipe/spec.md`. O app atual usa Streamlit em `app.py`, separa acesso a Xano e sessão nos módulos `sorrisomais/` e centraliza estilos em `assets/estilos.css`. Há integração Xano para autenticação, cadastro de Paciente e operações de Profissional/especialidade, mas os arquivos locais não definem contratos para todas as telas do kit.

## Goals / Non-Goals

**Goals:**

- Reorganizar a experiência da equipe nas telas e padrões visuais das referências do kit, com uma demonstração navegável de ponta a ponta.
- Manter a separação entre interface Streamlit, cliente REST, sessão e regras/persistência no Xano.
- Permitir testar navegação, permissões de apresentação e operações demonstrativas sem chamadas de rede.
- Preservar operações remotas existentes fora do modo demonstrativo e manter explícita a ausência de integração nas demais.

**Non-Goals:**

- Criar ou publicar endpoints, tabelas ou regras de negócio no Xano sem contrato aprovado.
- Usar dados demonstrativos como persistência ou misturá-los a registros reais.
- Alterar autenticação ou permissões já aplicadas no backend.

## Decisions

1. **Compor telas com controles Streamlit e componentes reutilizáveis.** Isso mantém estado, validação, semântica e navegação por teclado sob o modelo já adotado. HTML/CSS será usado para acabamento visual, sem recriar formulários funcionais em HTML avulso.

2. **Separar navegação de apresentação e acesso a dados.** A navegação escolhe a tela autorizada. Com `SORRISOMAIS_MODO_DEMONSTRACAO=1`, as telas usam um repositório fictício isolado na sessão; sem essa opção, usam as chamadas Xano existentes e apresentam indisponibilidade clara para contratos ausentes.

3. **Remover o rodapé renderizado pelo app e o cabeçalho visual solicitado, sem esconder controles essenciais do Streamlit.** Evita remover ações de acessibilidade ou funcionalidades de execução por seletores CSS frágeis.

4. **Não alterar o Xano nesta change.** Consultas, agenda, listagens e registros clínicos usam o repositório demonstrativo na primeira etapa. Integração real depende de inspeção do workspace Xano e de change posterior com contratos aprovados.

5. **Criar um repositório demonstrativo limitado à sessão.** Ele contém entidades fictícias relacionadas e operações de demonstração; não grava em arquivo, cache compartilhado ou Xano. O login continua usando o endpoint real de autenticação.

6. **Criar testes unitários em Python e JavaScript para contratos REST GET e POST.** Python exercita chamadas, payloads, respostas e falhas com transporte simulado; JavaScript verifica a correspondência de método/rota com os exports Xano versionados. Nenhum teste unitário acessa a rede.

7. **Criar testes unitários adicionais com dependências externas substituídas por doubles.** Eles verificam o repositório demonstrativo, roteamento por perfil, estados vazios e integração do frontend com serviços, sem depender de rede ou contas reais.

8. **Usar o kit como referência de composição, não como fonte de regras de domínio.** Entidades e vínculos seguem `docs/domain-model.md`; por exemplo, o Paciente possui um Prontuário, que contém vários Registros Clínicos.

## Risks / Trade-offs

- Dados demonstrativos podem ser confundidos com dados persistidos → identificar cada tela demonstrativa e informar que os dados se perdem com a sessão.
- O modo demonstrativo pode se misturar ao cliente real → escolher a fonte de dados uma vez pela configuração e nunca usar os dois repositórios na mesma operação.
- Algumas operações não possuem endpoint verificado → manter modo Xano limitado aos contratos presentes até a change de backend.
- CSS sobre elementos internos do Streamlit pode quebrar após atualização → preferir containers nomeados e estilos simples; cobrir telas-chave em verificação visual.
- Exibir uma navegação com áreas parcialmente indisponíveis pode confundir a equipe → rotular estado e não oferecer botões que pareçam concluir operações inexistentes.
- Diferenças entre a referência e as regras de domínio podem surgir → manter os nomes e relacionamentos definidos pelo modelo do projeto.

## Migration Plan

1. Introduzir configuração e repositório demonstrativo por sessão, sem alterar o Xano.
2. Migrar as telas para a composição nova preservando o login real e os formulários integrados no modo Xano.
3. Executar testes unitários e regressão dos fluxos atuais.
4. Revisar telas em computador, tablet e celular.
5. Desativar o modo demonstrativo pela configuração para voltar ao comportamento integrado atual; não há migração de dados.

Após esta change, abrir uma proposta específica para operações Xano ausentes, baseada na inspeção do schema e nos endpoints existentes. Não criar operações até esse contrato ser revisto.
