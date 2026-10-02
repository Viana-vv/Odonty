## 1. Levantamento e navegação

- [x] 1.1 Mapear as 15 referências do kit para telas e ações existentes; a especificação lista as telas e os testes JavaScript por rota verificam os contratos Xano exportados.
- [x] 1.2 Implementar navegação por Conta de Acesso e perfil; `tests/test_navegacao.py` e `tests/test_demo_interface.py` verificam áreas permitidas e não autorizadas.
- [x] 1.3 Criar camada demonstrativa de dados fictícios limitada à sessão; `pytest tests/test_demonstracao.py` verifica vínculos, operações e conflitos sem rede.

## 2. Identidade visual e estrutura

- [x] 2.1 Adicionar configuração explícita `SORRISOMAIS_MODO_DEMONSTRACAO` e atualizar tema, layout base, menu e componentes reutilizáveis; testes de configuração e interface cobrem alternância e foco visível. Limitar `GET /auth/me` e `GET /especialidades` conforme a janela de cache para respeitar o limite do workspace.
- [x] 2.2 Remover o rodapé atual e o cabeçalho visual da aplicação; validado pela revisão dos componentes e CSS, sem ocultar controles essenciais do Streamlit.
- [x] 2.3 Adaptar o login e a visão geral; testes de autenticação e `tests/test_demo_interface.py` verificam acesso e apresentação por perfil.

## 3. Telas do kit

- [x] 3.1 Adaptar agenda e formulário de Consulta com dados fictícios no modo demonstrativo e sem ações falsas no modo Xano; `tests/test_demonstracao.py`, `tests/test_navegacao.py` e `tests/test_demo_interface.py` verificam vínculos, conflitos e apresentação.
- [x] 3.2 Adaptar listagem, perfil e formulários de Paciente; `tests/test_demonstracao.py` cobre operações da sessão e `tests/test_pacientes.py` preserva o cadastro remoto no modo Xano.
- [x] 3.3 Adaptar listagem, perfil e formulário de Profissional; `tests/test_demonstracao.py` verifica operações demonstrativas e `tests/test_profissionais.py` cobre contratos remotos.
- [x] 3.4 Adaptar Prontuário e evolução clínica respeitando Paciente–Prontuário–Registros Clínicos; `tests/test_demonstracao.py` e `tests/test_navegacao.py` verificam histórico fictício e autorização por perfil.
- [x] 3.5 Adaptar catálogo de Procedimentos e painéis por perfil; `tests/test_demonstracao.py` verifica valores derivados e estados sem integração.

## 4. Testes e revisão

- [x] 4.1 Criar testes unitários em Python e JavaScript para cada contrato `GET` e `POST`, além do repositório demonstrativo, navegação, permissões, estados vazios, erros e cache; verificar cobertura rota a rota sem chamadas de rede.
- [x] 4.2 Executar testes unitários e regressão de autenticação, Pacientes e Profissionais; `pytest tests/api_contracts tests/test_demonstracao.py tests/test_navegacao.py tests/test_acesso.py tests/test_interface.py tests/test_profissionais.py tests/test_pacientes.py tests/test_demo_interface.py -q -p no:cacheprovider` e testes JavaScript das rotas; sem chamadas reais nos testes unitários.
- [x] 4.3 Verificar login e telas principais em computador, tablet e celular, incluindo ausência de rolagem horizontal e navegação por teclado.
- [x] 4.4 Atualizar a documentação de execução, registrar nas instruções permanentes o uso das referências visuais e os testes por contrato; README lista operações Xano disponíveis e pendentes. `openspec validate recriacao-layout-sorriso-mais --strict` passou.

## 5. Integração Xano pendente

- [x] 5.1 Inspecionar no Xano os schemas e contratos reais para Agenda, Consultas, listagens e Registros Clínicos; registrar lacunas sem publicar mudanças no workspace nem usar dados de pacientes reais. Pull read-only do workspace 149129/branch live (`v1`), sem `--records`/`--env`: há `consulta` com Paciente, Profissional, um único Procedimento, início/fim e situação, mas sem vínculo com Disponibilidade/Agenda; `prontuario` registra paciente, profissional, consulta opcional, procedimento, data e observações; `prontuario_paciente` possui vínculo único por Paciente. Não foram encontrados schemas de Agenda/Disponibilidade, Registro Clínico ou Exame, nem APIs de agenda/consultas/listagens/registros no grupo Sorriso Acesso. O vínculo único de procedimento e a ausência de disponibilidade conflitam com o modelo de domínio; nenhuma alteração remota ou leitura de registros foi feita.
- [x] 5.2 Propor change OpenSpec separada para endpoints, validações e permissões que faltarem; a proposta `agenda-consultas-registros-clinicos-api` foi validada com `--strict` e determina revisão dos contratos antes de qualquer Apply, sem implementação nem publicação no Xano nesta etapa.
