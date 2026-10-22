## Why

O agendamento está disponível como formulário dentro da Agenda, enquanto a referência aprovada apresenta Nova Consulta como uma tela própria. A equipe administrativa precisa concluir o agendamento com os contratos Xano já disponíveis e receber retorno claro quando os dados ou a disponibilidade forem recusados.

## What Changes

- Criar uma tela própria de Nova Consulta seguindo a referência `08-nova-consulta.png`.
- Usar os contratos existentes para opções de Agenda, Disponibilidades e criação de Consulta.
- Tratar falhas de carregamento, campos obrigatórios e conflitos retornados pelo Xano, com atualização explícita das opções e horários.

Fora do escopo: criar ou alterar endpoints, regras de negócio, autorização no Xano, navegação global e outros formulários.

## Capabilities

### New Capabilities
- `interface-nova-consulta`: apresentação e envio do formulário próprio de agendamento.

### Modified Capabilities
Nenhuma.

## Impact

- Novo módulo Streamlit `sorrisomais/pagina_nova_consulta_xano.py` e estilos escopados em `assets/estilos.css`, testados isoladamente.
- Os contratos existentes de `GET /agenda/opcoes`, `GET /disponibilidades` e `POST /consultas` são consumidos pelo cliente REST existente.
- Nenhuma mudança no backend Xano ou no roteamento global nesta etapa.
