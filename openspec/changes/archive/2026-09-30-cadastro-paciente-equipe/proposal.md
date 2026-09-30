## Why

A equipe já consegue autenticar-se e cadastrar Dentistas, mas não consegue cadastrar a pessoa que será atendida. O cadastro de Paciente prepara a base para o futuro agendamento e deve garantir desde a criação seu vínculo único com um Prontuário.

## What Changes

- Disponibilizar Cadastrar paciente para Administrador e Recepcionista ativos.
- Cadastrar nome, nascimento, telefone, CPF, e-mail e celular como campos obrigatórios, com validação de cada dado.
- Criar Paciente ativo e Prontuário vazio na mesma transação no Xano.
- Separar Paciente de Conta de Acesso: este formulário não pede senha nem concede login.
- Tratar validação, duplicação, perda de permissão e resultado incerto sem expor dados pessoais.

Fora do escopo: busca/listagem, edição, inativação, cadastro público, login de Paciente, agendamento, dados clínicos e consulta do prontuário. A busca recomendada na revisão fica para uma change posterior, mantendo esta entrega focada na criação.

## Capabilities

### New Capabilities
- `cadastro-paciente`: criação autorizada e atômica de Paciente e Prontuário pela equipe.

### Modified Capabilities
- `acesso-autenticado`: incluir a ação Cadastrar paciente para Administrador e Recepcionista, preservando o cadastro de Profissional exclusivo do Administrador.

## Impact

Interface Streamlit, cliente REST, limpeza de sessão, scripts Xano, testes e README. Reutilizar autenticação e validação de sessão; inspecionar metadados remotos antes de definir o mapeamento físico das entidades, preservando estruturas legadas.

A change cadastro-profissional-admin permanece em andamento e também modifica acesso-autenticado. Esta proposta preserva seus comportamentos; sincronizar essa dependência antes de arquivar a nova change, sem sobrescrever requisitos. Riscos: criação parcial, duplicação concorrente de CPF, reenvio após timeout e exposição de dados. Detalhes e decisões propostas estão no design, sujeitos à revisão antes do Apply.
