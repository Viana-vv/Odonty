## 1. Contratos e sessão

- [x] 1.1 Confirmar os testes Python e JavaScript existentes por rota para login, identidade, logout, Consultas, Registros Clínicos e Exames; complementar a chamada GET de Exames do portal sem rede real.
- [x] 1.2 Criar sessão isolada de Paciente com credencial em estado temporário, limpeza de senha, expiração e logout; verificar sucesso, perfil inválido e expiração em testes.

## 2. Superfície de autoatendimento

- [x] 2.1 Criar entrypoint Streamlit separado e impedir que perfil somente Paciente componha área interna; verificar o bloqueio por teste e preservar composição para perfil interno.
- [x] 2.2 Apresentar Consultas próprias reutilizando a tela existente, sem `paciente_id`, dados clínicos ou Procedimentos; executar testes da tela para futuras, passadas, vazias e falha da API.
- [x] 2.3 Apresentar Registros Clínicos liberados e Exames próprios com resultado somente quando disponível; verificar resposta sem identificador de Paciente e campos exibidos com dados fictícios.
- [x] 2.4 Aplicar identidade visual do kit Sorriso Mais e verificar renderização Streamlit dos conteúdos e controles com AppTest.

## 3. Verificação e documentação

- [x] 3.1 Executar testes Python e JavaScript pertinentes sem tráfego de rede e validar autorização/escopo nos contratos Xano existentes.
- [x] 3.2 Documentar comando local e implantação como serviço separado, validar OpenSpec e revisar diff para confirmar isolamento dos módulos da equipe e ausência de credenciais/dados reais.
