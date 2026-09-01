
# Modelo de Domínio — Sistema para Clínica Odontológica

## 1. Objetivo

Este documento descreve os principais conceitos do sistema para clínica odontológica, seus relacionamentos e regras de negócio.

O modelo é conceitual. Ele explica o domínio, mas ainda não define as tabelas físicas do Xano.

## 2. Atores do sistema

### Paciente

Pessoa que recebe atendimento odontológico.

Pode:

- consultar profissionais;
- visualizar horários disponíveis;
- agendar consultas;
- consultar seus agendamentos;
- cancelar consultas permitidas;
- visualizar informações liberadas pela clínica.

### Profissional

Dentista ou outro profissional autorizado a realizar atendimentos.

Pode:

- consultar sua agenda;
- criar ou bloquear horários;
- visualizar os pacientes agendados;
- iniciar e concluir consultas;
- registrar informações clínicas;
- registrar procedimentos;
- solicitar e registrar exames.

### Administrador ou recepcionista

Pessoa responsável pelas atividades administrativas.

Pode:

- cadastrar pacientes;
- cadastrar profissionais;
- organizar a agenda;
- agendar, confirmar, cancelar ou reagendar consultas;
- cadastrar procedimentos;
- administrar contas de acesso.

Informações clínicas só podem ser alteradas por profissionais autorizados.

## 3. Visão geral dos relacionamentos

```text
Conta de Acesso
├── Paciente
├── Profissional
└── Administrador/Recepcionista

Paciente
├── Consultas
├── Prontuário
│   └── Registros Clínicos
└── Exames

Profissional
├── Disponibilidades da Agenda
├── Consultas
└── Registros Clínicos

Consulta
├── Paciente
├── Profissional
├── Disponibilidade
├── Registro Clínico
├── Procedimentos
└── Exames
```

## 4. Entidades do domínio

## 4.1 Conta de Acesso

Representa a identidade utilizada para entrar no sistema.

A conta de acesso não deve ser confundida com paciente ou profissional. Ela contém as informações de autenticação e autorização.

### Principais informações

- identificador da conta;
- nome de exibição;
- e-mail;
- credencial de autenticação;
- perfil de acesso;
- situação da conta;
- data de criação;
- data do último acesso.

### Perfis possíveis

- paciente;
- profissional;
- administrador;
- recepcionista.

### Estados possíveis

- ativo;
- inativo;
- bloqueado.

### Relacionamentos

- uma conta pode estar associada a um paciente;
- uma conta pode estar associada a um profissional;
- uma conta administrativa pode não representar um paciente;
- uma conta deve possuir pelo menos um perfil.

### Regras

- o e-mail deve ser único;
- senhas não podem ser armazenadas em texto puro;
- uma conta bloqueada ou inativa não pode entrar no sistema;
- as permissões devem ser verificadas no Xano;
- esconder botões na interface não substitui a autorização no backend.

## 4.2 Paciente

Representa a pessoa que recebe atendimento na clínica.

No documento inicial, essa entidade aparece como “Usuário”. O nome “Paciente” evita confusão com a conta de acesso.

### Principais informações

- identificador do paciente;
- nome completo;
- CPF;
- RG;
- data de nascimento;
- sexo ou gênero informado;
- e-mail;
- telefone;
- celular;
- CEP;
- logradouro;
- número;
- complemento;
- bairro;
- cidade;
- estado;
- situação do cadastro;
- data de criação;
- data de atualização.

### Estados possíveis

- ativo;
- inativo.

### Relacionamentos

- pode possuir uma conta de acesso;
- possui um prontuário;
- pode possuir várias consultas;
- pode possuir vários exames;
- pode ser atendido por diferentes profissionais.

### Regras

- cada paciente deve possuir um identificador único;
- o CPF deve ser único, quando utilizado;
- o paciente só pode consultar os próprios dados;
- a inativação não deve apagar seu histórico;
- os dados pessoais não devem ser expostos sem autorização;
- o projeto acadêmico deve utilizar somente dados fictícios.

## 4.3 Profissional

Representa o dentista ou outro profissional responsável pelos atendimentos.

### Principais informações

- identificador do profissional;
- nome completo;
- CPF;
- RG;
- CRO ou registro profissional;
- especialidade;
- e-mail profissional;
- telefone;
- celular;
- situação do cadastro;
- duração padrão da consulta;
- data de criação;
- data de atualização.

### Estados possíveis

- ativo;
- inativo;
- afastado.

### Relacionamentos

- pode possuir uma conta de acesso;
- possui várias disponibilidades;
- realiza várias consultas;
- cria registros clínicos;
- solicita exames;
- registra procedimentos.

### Regras

- o CRO deve ser único;
- somente profissionais ativos podem receber novos agendamentos;
- profissionais inativos continuam aparecendo no histórico;
- um profissional não pode possuir duas consultas no mesmo horário;
- somente profissionais autorizados podem acessar informações clínicas.

## 4.4 Especialidade

Representa uma área de atuação odontológica.

### Exemplos

- clínica geral;
- ortodontia;
- endodontia;
- periodontia;
- odontopediatria;
- implantodontia.

### Relacionamentos

- um profissional pode possuir uma ou mais especialidades;
- uma especialidade pode pertencer a vários profissionais.

Para o MVP, a especialidade pode ser inicialmente uma informação dentro do profissional.

## 4.5 Disponibilidade da Agenda

Representa um período no qual o profissional pode receber uma consulta.

Essa entidade corresponde à “Agenda” do documento inicial.

### Principais informações

- identificador da disponibilidade;
- profissional;
- data;
- horário de início;
- horário de término;
- situação;
- observação;
- motivo do bloqueio;
- data de criação.

### Estados possíveis

- disponível;
- reservado;
- bloqueado;
- indisponível.

### Relacionamentos

- pertence a um profissional;
- pode estar associada a uma consulta;
- um profissional pode ter várias disponibilidades.

### Regras

- o horário final deve ser posterior ao horário inicial;
- não pode haver horários sobrepostos para o mesmo profissional;
- um horário bloqueado não pode ser agendado;
- um horário reservado não pode receber outra consulta;
- horários passados não podem receber novos agendamentos;
- cancelar uma consulta pode liberar o horário;
- o histórico da consulta cancelada deve ser preservado.

## 4.6 Consulta

Representa o atendimento agendado entre um paciente e um profissional.

A consulta não deve ser confundida com prontuário, procedimento ou exame.

### Principais informações

- identificador da consulta;
- paciente;
- profissional;
- disponibilidade da agenda;
- data e horário;
- motivo informado pelo paciente;
- observações administrativas;
- situação;
- data do agendamento;
- data da confirmação;
- data do cancelamento;
- motivo do cancelamento;
- responsável pelo agendamento;
- responsável pelo cancelamento.

### Estados possíveis

```text
Agendada
   ↓
Confirmada
   ↓
Em atendimento
   ↓
Realizada
```

Também pode assumir os estados:

- cancelada;
- falta.

### Relacionamentos

- pertence a um paciente;
- pertence a um profissional;
- utiliza uma disponibilidade;
- pode gerar um registro clínico;
- pode possuir vários procedimentos;
- pode possuir vários exames.

### Regras

- paciente, profissional e horário são obrigatórios;
- o horário deve pertencer ao profissional;
- não pode existir conflito de horário;
- o paciente não pode ter duas consultas no mesmo horário;
- uma consulta cancelada continua no histórico;
- uma consulta realizada não pode ser apagada;
- somente usuários autorizados podem alterar sua situação;
- uma consulta só pode ser marcada como realizada após o atendimento;
- alterações importantes devem registrar data e responsável;
- reagendamentos devem preservar o histórico.

## 4.7 Prontuário

Representa o histórico clínico e odontológico permanente do paciente.

O prontuário não representa uma única consulta. Ele reúne os registros produzidos durante todos os atendimentos.

### Principais informações

- identificador do prontuário;
- paciente proprietário;
- data de abertura;
- situação;
- observações gerais autorizadas.

### Relacionamentos

- pertence a um único paciente;
- um paciente possui um prontuário ativo;
- contém vários registros clínicos;
- seus registros podem estar relacionados a consultas, procedimentos e exames.

### Regras

- o prontuário deve pertencer a um paciente;
- não deve ser apagado quando o paciente for inativado;
- somente profissionais autorizados podem acessar informações clínicas;
- o paciente não pode alterar registros clínicos;
- correções devem preservar o histórico;
- alterações devem ser registradas como complemento ou retificação.

## 4.8 Registro Clínico

Representa as informações clínicas registradas durante ou após uma consulta.

O registro clínico é separado do prontuário porque um prontuário contém vários registros.

### Principais informações

- identificador do registro;
- prontuário;
- consulta relacionada;
- profissional responsável;
- data e horário;
- queixa principal;
- histórico médico;
- histórico odontológico;
- avaliação clínica;
- diagnóstico;
- plano de tratamento;
- orientações;
- observações;
- data da última atualização.

### Relacionamentos

- pertence a um prontuário;
- pode estar associado a uma consulta;
- é criado por um profissional;
- pode estar relacionado a procedimentos e exames.

### Regras

- somente profissionais autorizados podem criar registros clínicos;
- todo registro deve identificar o profissional responsável;
- o registro deve pertencer ao mesmo paciente da consulta;
- registros concluídos não devem ser apagados;
- correções devem preservar as informações anteriores;
- observações administrativas e clínicas devem ficar separadas;
- o paciente visualiza somente as informações liberadas pela clínica.

## 4.9 Procedimento

Representa um serviço ou tratamento odontológico.

### Exemplos

- limpeza;
- restauração;
- extração;
- aplicação de flúor;
- tratamento de canal;
- manutenção ortodôntica.

### Principais informações

- identificador do procedimento;
- nome;
- descrição;
- categoria;
- duração estimada;
- valor de referência;
- situação.

### Estados possíveis

- ativo;
- inativo.

### Relacionamentos

- um procedimento pode aparecer em várias consultas;
- uma consulta pode possuir vários procedimentos;
- a ligação é realizada por `ConsultaProcedimento`.

### Regras

- o nome é obrigatório;
- procedimentos inativos não podem ser adicionados a novas consultas;
- procedimentos antigos permanecem no histórico;
- o valor é apenas uma referência, pois pagamentos estão fora do MVP.

## 4.10 ConsultaProcedimento

Representa a realização ou o planejamento de um procedimento durante uma consulta.

Essa entidade resolve o relacionamento de muitos para muitos:

```text
Consulta N ← ConsultaProcedimento → N Procedimento
```

### Principais informações

- identificador;
- consulta;
- procedimento;
- profissional responsável;
- dente ou região;
- quantidade;
- valor registrado;
- observações;
- situação;
- data de realização.

### Estados possíveis

- planejado;
- autorizado;
- realizado;
- cancelado.

### Regras

- consulta e procedimento são obrigatórios;
- procedimento realizado deve identificar data e profissional;
- a informação permanece no histórico mesmo que o procedimento seja inativado;
- procedimentos cancelados não devem ser apagados.

## 4.11 Exame

Representa um exame solicitado ou realizado durante o acompanhamento do paciente.

O exame é uma forma de investigação. Ele não representa uma consulta.

### Exemplos

- radiografia;
- fotografia odontológica;
- tomografia;
- exame laboratorial.

### Principais informações

- identificador do exame;
- paciente;
- consulta relacionada;
- profissional solicitante;
- tipo;
- data da solicitação;
- data da realização;
- resultado;
- observações;
- referência do arquivo;
- situação.

### Estados possíveis

```text
Solicitado
   ↓
Realizado
   ↓
Resultado disponível
```

Outros estados:

- cancelado;
- não realizado.

### Relacionamentos

- pertence a um paciente;
- pode estar relacionado a uma consulta;
- pode ser solicitado por um profissional;
- uma consulta pode possuir vários exames.

### Regras

- o exame deve pertencer ao paciente da consulta;
- a realização não pode acontecer antes da solicitação;
- somente profissionais autorizados podem alterar resultados;
- arquivos não podem ficar publicamente acessíveis;
- todos os arquivos utilizados no projeto devem ser fictícios;
- o histórico deve ser preservado.

## 5. Cardinalidades

```text
Paciente 1 -------- 1 Prontuário

Prontuário 1 ------ N Registro Clínico

Paciente 1 -------- N Consulta

Profissional 1 ---- N Consulta

Profissional 1 ---- N Disponibilidade

Disponibilidade 1 - 0..1 Consulta

Consulta 1 -------- 0..1 Registro Clínico

Consulta 1 -------- N ConsultaProcedimento

Procedimento 1 ---- N ConsultaProcedimento

Consulta 1 -------- N Exame

Paciente 1 -------- N Exame
```

## 6. Matriz de permissões

| Operação | Paciente | Profissional | Administrador/Recepcionista |
|---|---:|---:|---:|
| Consultar próprios dados | Sim | Sim | Conforme permissão |
| Alterar próprios dados | Sim | Sim | Sim |
| Consultar agenda | Sim | Sim | Sim |
| Criar disponibilidade | Não | Sim | Sim |
| Bloquear horário | Não | Sim | Sim |
| Agendar consulta | Sim | Conforme regra | Sim |
| Cancelar consulta | Própria | Conforme regra | Sim |
| Consultar prontuário | Próprio, de forma limitada | Pacientes autorizados | Somente com permissão |
| Criar registro clínico | Não | Sim | Não |
| Alterar registro clínico | Não | Profissional autorizado | Não |
| Cadastrar procedimento | Não | Conforme permissão | Sim |
| Associar procedimento | Não | Sim | Conforme permissão |
| Solicitar exame | Não | Sim | Não |
| Registrar resultado | Não | Sim | Não |
| Administrar contas | Não | Não | Sim |

Todas as permissões devem ser verificadas no Xano.

## 7. Regras gerais do domínio

### Autenticação

- toda operação protegida exige autenticação;
- contas bloqueadas ou inativas não podem acessar o sistema;
- a sessão deve possuir prazo de validade;
- a interface não deve armazenar senhas.

### Agenda

- não pode haver sobreposição de horários;
- horários bloqueados não podem ser agendados;
- somente horários futuros recebem agendamentos;
- o profissional precisa estar ativo;
- o horário precisa ter início e fim válidos.

### Consulta

- paciente, profissional e horário são obrigatórios;
- um horário não pode receber duas consultas;
- consultas canceladas permanecem no histórico;
- consulta realizada não pode voltar para agendada sem correção autorizada;
- falta e cancelamento são situações diferentes.

### Prontuário

- cada paciente possui um prontuário;
- prontuários não devem ser excluídos;
- informações clínicas são restritas;
- cada registro deve identificar data e profissional;
- correções devem preservar o histórico.

### Procedimento

- uma consulta pode ter vários procedimentos;
- procedimentos inativos permanecem no histórico;
- procedimento realizado deve possuir responsável;
- cobrança e pagamentos estão fora do MVP.

### Exame

- o exame deve pertencer a um paciente;
- o paciente deve ser o mesmo da consulta;
- resultados só podem ser registrados por usuário autorizado;
- arquivos devem utilizar acesso protegido;
- não podem ser usados dados ou arquivos reais.

## 8. Privacidade e segurança

- utilizar somente dados fictícios;
- não colocar CPF, RG, exames ou prontuários reais no GitHub;
- não armazenar senhas em texto puro;
- não colocar chaves ou tokens no código;
- utilizar variáveis de ambiente;
- aplicar autorização no Xano;
- paciente acessa somente os próprios dados;
- profissional acessa somente dados necessários;
- recepcionista não altera informações clínicas;
- informações clínicas não aparecem em logs ou métricas;
- arquivos de exames não devem possuir links públicos;
- o MVP acadêmico não está autorizado para uso clínico real.

## 9. Exemplo completo do domínio

Carlos é um paciente cadastrado na clínica.

A Dra. Mariana é uma profissional ativa, com especialidade em clínica geral.

A Dra. Mariana cria uma disponibilidade para o dia 28/09, das 14h às 15h.

Carlos consulta os horários disponíveis e escolhe esse horário.

O sistema verifica que a disponibilidade continua livre, cria a consulta e altera o horário para reservado.

Durante a consulta, Carlos relata dor no dente 26.

A Dra. Mariana registra a queixa e a avaliação no prontuário de Carlos.

A profissional solicita um exame de radiografia.

Depois de receber o resultado, registra o diagnóstico e associa um procedimento de restauração à consulta.

A consulta é marcada como realizada, mas continua disponível no histórico do paciente e do profissional.