# Project Overview — Sistema para Clínica Odontológica

## 1. Visão geral

Aplicação web para auxiliar uma clínica odontológica no gerenciamento
de pacientes, profissionais, agendas, consultas, prontuários,
procedimentos e exames.

## 2. Problema

Clínicas odontológicas podem ter dificuldades para organizar horários,
evitar conflitos de agenda e manter as informações dos atendimentos
centralizadas.

Antes de concluir esta seção, o grupo entrevistará profissionais da
área para validar quais problemas realmente acontecem na clínica.

## 3. Objetivos

- organizar a agenda dos profissionais;
- permitir o agendamento de consultas;
- evitar conflitos de horário;
- registrar atendimentos odontológicos;
- manter o histórico clínico do paciente;
- relacionar procedimentos e exames às consultas.

## 4. Usuários do sistema

### Paciente

Pode cadastrar-se, consultar horários, agendar consultas e acompanhar
seus agendamentos.

### Profissional

Pode consultar sua agenda, visualizar consultas e registrar informações
do atendimento.

### Administrador ou recepcionista

Pode cadastrar profissionais, pacientes, horários e procedimentos,
conforme as permissões definidas pelo grupo.

## 5. Escopo do MVP

O MVP deverá possuir:

- autenticação;
- cadastro de pacientes;
- cadastro de profissionais;
- disponibilidade de horários;
- agendamento e cancelamento de consultas;
- registro básico do atendimento no prontuário;
- associação de procedimentos;
- registro de exames;
- integração entre frontend e backend;
- implantação em produção.

## 6. Fora do escopo inicial

- pagamentos;
- convênios;
- estoque;
- odontograma gráfico;
- integração com WhatsApp;
- diagnóstico por inteligência artificial;
- suporte para várias clínicas.

## 7. Principais funcionalidades

- login e logout;
- controle de acesso por perfil;
- cadastro de pacientes e profissionais;
- gerenciamento da agenda;
- agendamento de consultas;
- cancelamento e confirmação;
- registro no prontuário;
- cadastro de procedimentos;
- registro de exames.

## 8. Arquitetura tecnológica

- Linguagem: Python;
- Frontend: Streamlit;
- Backend e banco de dados: Xano;
- Especificação das mudanças: OpenSpec;
- Versionamento: Git e GitHub;
- Implantação: Render ou Railway;
- Comunicação: API REST.

## 9. Segurança e privacidade

- usar somente pacientes e dados fictícios;
- não colocar senhas ou chaves no GitHub;
- aplicar as permissões no backend Xano;
- limitar o acesso conforme o perfil;
- armazenar configurações sensíveis em variáveis de ambiente.

## 10. Estratégia de desenvolvimento

O sistema será desenvolvido em pequenas mudanças utilizando OpenSpec.

Cada mudança seguirá:

Explore → Propose → Review → Apply → Testes → Archive

## 11. Fonte de verdade

O GitHub será a fonte oficial do código, da documentação, das decisões,
dos testes e do histórico do projeto.