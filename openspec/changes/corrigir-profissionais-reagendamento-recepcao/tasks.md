## 1. Profissionais

- [x] 1.1 Corrigir especialidade ausente no GET Xano e aceitar campos vazios no cliente sem aceitar respostas malformadas; verificar contratos Python e JavaScript sem rede.
- [x] 1.2 Exibir cadastro incompleto com identificador e campos não informados; verificar leitura da Recepcionista e manutenção dos controles por perfil.

## 2. Reagendamento

- [x] 2.1 Substituir opções da Agenda por leituras próprias e filtrar destino incompleto; verificar seleção, atualização, sessão, erros e sucesso em testes de interface simulados.

## 3. Integração

- [x] 3.1 Atualizar documentação e executar regressões Python, contratos JavaScript e validação estrita OpenSpec.
- [x] 3.2 Publicar somente GET `/profissionais` após prévia e verificar listagem e carregamento do reagendamento com Conta de Acesso fictícia de Recepcionista, sem alterar consultas existentes.

## Verificação

- Issue #148. Alterações locais na `main` por solicitação explícita do usuário.
- 50 testes focados aprovados; regressão ampliada com 280 testes Python e 7 subtestes aprovados (contratos REST, telas, roteamento e cache).
- 51 testes JavaScript aprovados; validação estrita OpenSpec e `git diff --check` sem erros.
- GET `/profissionais` publicado com push limitado ao arquivo da rota após prévia que indicou somente esse endpoint, sem mudanças em tabelas ou cadastros.
- Integração real em 21/11/2026: login com Conta de Acesso fictícia de Recepcionista e renderização Streamlit com REST real confirmaram 17 cartões em Profissionais, incluindo `Profissional #26` como incompleto. Reagendar Consulta abriu e permitiu selecionar Paciente e Consulta existentes e ler horários sem erro nem chamada a `/agenda/opcoes`. Nenhuma escrita de reagendamento foi enviada; logout concluído e Conta de Acesso fictícia inativada. Uma primeira tentativa interrompida pelo mecanismo de inspeção do AppTest também teve sua Conta de Acesso fictícia inativada.
